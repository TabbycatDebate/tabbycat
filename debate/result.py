# cannot import debate.models here - would create circular dep

class Scoresheet(object):
    """
    Representation of an adjudicator's scoresheet

    self.data is a nested dictionary, such that
    self.data[team][pos] = score
    """

    def __init__(self, ballots, adjudicator):
        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicator = adjudicator
        self.POSITIONS_RANGE = self.debate.round.tournament.POSITIONS

        from debate import models as m

        self.da = m.DebateAdjudicator.objects.get(
            adjudicator = self.adjudicator,
            debate = self.debate,
        )
        self.dts = self.debate.debateteam_set.all()

        self.data = {
            'aff': self._no_scores(),
            'neg': self._no_scores()
        }

        self._init_side('aff')
        self._init_side('neg')

    def _no_scores(self):
        return dict((i, None) for i in self.POSITIONS_RANGE)

    def _init_side(self, side):
        """
        Load from database
        """

        from debate import models as m

        dt = self.debate.get_dt(side)

        scores = m.SpeakerScoreByAdj.objects.filter(
            ballot_submission = self.ballots,
            debate_adjudicator = self.da,
            debate_team = dt,
        )

        for ss in scores:
            self.set_score(side, ss.position, ss.score)

    def save(self):

        from debate import models as m

        # delete existing db objects
        m.SpeakerScoreByAdj.objects.filter(
            ballot_submission = self.ballots,
            debate_adjudicator = self.da,
        ).delete()

        self._save_side('aff')
        self._save_side('neg')

    def _save_side(self, side):
        """
        Save to database
        """

        from debate import models as m

        dt = self.debate.get_dt(side)

        # create new ones
        for pos in self.POSITIONS_RANGE:
            m.SpeakerScoreByAdj(
                ballot_submission = self.ballots,
                debate_adjudicator = self.da,
                debate_team = dt,
                position = pos,
                score = self.get_score(side, pos),
            ).save()


    def set_score(self, side, position, score):
        self.data[side][position] = score

    def get_score(self, side, position):
        return self.data[side][position]

    @property
    def aff_score(self):
        return self.get_total('aff')

    @property
    def neg_score(self):
        return self.get_total('neg')

    def get_total(self, side):
        """
        Return total score for side
        """
        scores = [self.data[side][p] for p in self.POSITIONS_RANGE]
        if None in scores:
            return 0
        return sum(scores)

    @property
    def aff_win(self):
        return self.aff_score > self.neg_score

    @property
    def neg_win(self):
        return self.neg_score > self.aff_score

class BallotSet(object):
    """
    Encapsulates a set of ballots

    This class makes it easier for views and forms to work with a set of
    ballots for a particular debate.

    It acts as a translation layer on top of the following db models:

    BallotSubmission
    TeamScore
    SpeakerScore
    Motion
    """

    def __init__(self, ballots):
        """Constructor.
        'ballots' must be a BallotSubmission.
        """
        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicators = self.debate.adjudicators.list
        self.POSITIONS_RANGE = self.debate.round.tournament.POSITIONS

        self.loaded_sheets = False
        self._adjudicator_sheets = None

        self.speakers = {
            'aff': {},
            'neg': {},
        }

        self.points = {
            'aff': None,
            'neg': None,
        }

        self.total_score = {
            'aff': None,
            'neg': None,
        }

        self.wins = {
            'aff': None,
            'neg': None,
        }

        self.margins = {
            'aff': None,
            'neg': None,
        }

        self._other = {
            'aff': 'neg',
            'neg': 'aff',
        }

        self.motion_veto = {
            'aff': None,
            'neg': None,
        }

        self._init_side('aff')
        self._init_side('neg')

    @property
    def confirmed(self):
        return self.ballots.confirmed

    @confirmed.setter
    def confirmed(self, new):
        self.ballots.confirmed = new

    @property
    def discarded(self):
        return self.ballots.discarded

    @discarded.setter
    def discarded(self, new):
        self.ballots.discarded = new

    @property
    def motion(self):
        return self.ballots.motion

    @motion.setter
    def motion(self, new):
        self.ballots.motion = new

    @property
    def aff_motion_veto(self):
        return self.motion_veto['aff']

    @aff_motion_veto.setter
    def aff_motion_veto(self, new):
        self.motion_veto['aff'] = new

    @property
    def neg_motion_veto(self):
        return self.motion_veto['neg']

    @neg_motion_veto.setter
    def neg_motion_veto(self, new):
        self.motion_veto['neg'] = new

    def _init_side(self, side):
        dt = self.debate.get_dt(side)
        from debate.models import SpeakerScore, TeamScore, DebateTeamMotionPreference

        for sss in SpeakerScore.objects.filter(
            debate_team = dt,
            ballot_submission = self.ballots,
        ):

            self.speakers[side][sss.position] = sss.speaker

        try:
            ts = TeamScore.objects.get(
                ballot_submission = self.ballots,
                debate_team = dt)
            points = ts.points
            score = ts.score
            win = ts.win
            margin = ts.margin
        except TeamScore.DoesNotExist:
            points = None
            score = None
            win = None
            margin = None

        self.points[side] = points
        self.total_score[side] = score
        self.wins[side] = win
        self.margins[side] = margin

        try:
            dtmp = DebateTeamMotionPreference.objects.get(
                ballot_submission = self.ballots,
                debate_team = dt,
                preference = 3
            )
            veto = dtmp.motion
        except DebateTeamMotionPreference.DoesNotExist:
            veto = None
        self.motion_veto[side] = veto


    @property
    def adjudicator_sheets(self):
        if not self._adjudicator_sheets:
            self._adjudicator_sheets = dict(
                (a, Scoresheet(self.ballots, a)) for a in self.adjudicators
            )
            self.loaded_sheets = True
        return self._adjudicator_sheets

    def save(self):
        self.ballots.save()

        for sheet in self.adjudicator_sheets.values():
            sheet.save()

        # Tally scores per adjudicator and determine majority
        self._calc_decision()

        # Create team score, speaker score, and motion preference objects
        self._save('aff')
        self._save('neg')

    def _calc_decision(self):
        decision = []
        for adj in self.adjudicators:
            aff_score = self.adjudicator_sheets[adj].aff_score
            neg_score = self.adjudicator_sheets[adj].neg_score
            decision.append((adj, aff_score > neg_score))

        votes = [v for a, v in decision]
        majority_aff = votes.count(True) > votes.count(False)
        self.majority_adj = [a for a, v in decision if v == majority_aff]


    def _save(self, side):
        from debate.models import TeamScore, SpeakerScore, DebateTeamMotionPreference

        dt = self.debate.get_dt(side)
        total = self._score(side)
        points = self._points(side)
        win = self._win(side)
        margin = self._margin(side)

        TeamScore.objects.filter(ballot_submission=self.ballots, debate_team=dt).delete()
        TeamScore(ballot_submission=self.ballots,
                  debate_team=dt, score=total, points=points, win=win,
                  margin=margin).save()

        SpeakerScore.objects.filter(ballot_submission=self.ballots, debate_team=dt).delete()
        for i in self.POSITIONS_RANGE:
            speaker = self.speakers[side][i]
            score = self.get_avg_score(side, i)
            SpeakerScore(
                ballot_submission = self.ballots,
                debate_team = dt,
                speaker = speaker,
                score = score,
                position = i,
            ).save()

        DebateTeamMotionPreference.objects.filter(ballot_submission=self.ballots, debate_team=dt, preference=3).delete()
        if self.motion_veto[side] is not None:
            DebateTeamMotionPreference(ballot_submission=self.ballots, debate_team=dt, preference=3, motion=self.motion_veto[side]).save()

        self.ballots.motion = self.motion
        self.ballots.save()

    def get_speaker(self, side, position):
        """
        Return the speaker object for side/position
        """
        return self.speakers[side].get(position)

    def get_score(self, adj, side, position):
        """
        Return the score for the speaker in side/position
        """
        return self.adjudicator_sheets[adj].get_score(side, position)

    def get_avg_score(self, side, position):
        """
        Return the average score of majority adjudicators for side/position
        """
        return sum(self.adjudicator_sheets[adj].get_score(side, position)
                   for adj in self.majority_adj) / len(self.majority_adj)

    def set_speaker(self, side, pos, speaker):
        self.speakers[side][pos] = speaker

    def set_score(self, adj, side, position, score):
        """
        Set the score given by adj for side/position
        """
        self.adjudicator_sheets[adj].set_score(side, position, score)


    def _score(self, side):
        if not self.loaded_sheets:
            return self.total_score[side]

        return sum(self.adjudicator_sheets[adj].get_total(side) for adj in
                   self.majority_adj) / len(self.majority_adj)

    def _dissenting_inclusive_score(self, side):
        dissenting_score = sum(self.adjudicator_sheets[adj].get_total(side) for adj in
                   self.adjudicators) / len(self.adjudicators)
        return dissenting_score

    @property
    def aff_score(self):
        return self._score('aff')

    @property
    def neg_score(self):
        return self._score('neg')

    # Abstracted to not be tied to wins
    def _points(self, side):
        if not self.loaded_sheets:
            return self.points[side]

        if self._score(side):
            if self._score(side) > self._score(self._other[side]):
                return 1
            return 0

        return None

    # Supplants _points; ie its a count of the number of wins
    def _win(self, side):
        if not self.loaded_sheets:
            return self.win[side]

        if self._score(side):
            if self._score(side) > self._score(self._other[side]):
                return True
            return False

        return None

    def _margin(self, side):
        if not self.loaded_sheets:
            return self.margin[side]

        if self.debate.round.tournament.config.get('margin_includes_dissenters') is False:
            if self._score(side) and self._score(self._other[side]):
                return self._score(side) - self._score(self._other[side])
        else:
            if self._dissenting_inclusive_score(side) and self._dissenting_inclusive_score(self._other[side]):
                dissenting_inclusive_margin = self._dissenting_inclusive_score(side) - self._dissenting_inclusive_score(self._other[side])
                return dissenting_inclusive_margin

        return None

    @property
    def aff_points(self):
        return self._points('aff')

    @property
    def neg_points(self):
        return self._points('neg')

    @property
    def aff_win(self):
        return self.aff_points

    @property
    def neg_win(self):
        return self.neg_points

    def is_trainee(self, adj):
        from debate import models as m
        da = m.DebateAdjudicator.objects.get(
            adjudicator = adj,
            debate = self.debate)
        return da.type == m.DebateAdjudicator.TYPE_TRAINEE

    @property
    def adjudicator_results(self):
        self._calc_decision()
        splits = [adj not in self.majority_adj and not self.is_trainee(adj) for _, adj in self.debate.adjudicators]
        for (type, adj), split in zip(self.debate.adjudicators, splits):
            yield type, adj, split

    def sheet_iter(self):
        REPLY_POSITION = self.debate.round.tournament.REPLY_POSITION
        POSITIONS = self.debate.round.tournament.POSITIONS

        class Position(object):

            def __init__(self2, sheet, side, pos):
                self2.sheet = sheet
                self2.pos = pos
                self2.side = side

            def name(self2):
                return (self2.pos == REPLY_POSITION) and "Reply" or str(self2.pos)

            def speaker(self2):
                return self.get_speaker(self2.side, self2.pos)

            def score(self2):
                return self2.sheet.data[self2.side][self2.pos]

        class ScoresheetWrapper(object):

            def __init__(self2, adj):
                self2.sheet = self.adjudicator_sheets[adj]
                self2.adjudicator = adj

            def position_iter(self2, side):
                for pos in POSITIONS:
                    yield Position(self2.sheet, side, pos)

            def affs(self2):
                return self2.position_iter('aff')

            def negs(self2):
                return self2.position_iter('neg')

            def aff_score(self2):
                return self2.sheet.aff_score

            def neg_score(self2):
                return self2.sheet.neg_score

            def aff_win(self2):
                return self2.sheet.aff_win

            def neg_win(self2):
                return self2.sheet.neg_win

        for adj in self.adjudicators:
            yield ScoresheetWrapper(adj)


class ForfeitBallotSet(BallotSet):
    # This is WADL-specific for now

    def __init__(self, ballots, forfeiter):
        """Constructor.
        'ballots' must be a BallotSubmission.
        """
        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicators = self.debate.adjudicators.list
        self.forfeiter = forfeiter

    def save_side(self, side):

        dt = self.debate.get_dt(side)

        if self.forfeiter == dt:
            points = 0
            win = False
        else:
            points = 2
            win = True


        from debate.models import TeamScore
        # Note: forfeited debates have fake scores/margins, thus the affects_average toggle
        TeamScore.objects.filter(ballot_submission=self.ballots, debate_team=dt).delete()
        TeamScore(
            ballot_submission=self.ballots,
            debate_team=dt,
            points=points,
            win=win,
            score=0,
            margin=0,
            affects_averages=False).save()


    def save(self):
        self.ballots.forfeit = self.forfeiter
        self.ballots.save()
        self.save_side('aff')
        self.save_side('neg')


