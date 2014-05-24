# cannot import debate.models here - would create circular dep

class Scoresheet(object):
    """
    Representation of an adjudicator's scoresheet

    self.data is a nested dictionary, such that
    self.data[side][pos] = score
    """

    def __init__(self, ballots, adjudicator):
        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicator = adjudicator

        from debate import models as m

        self.da = m.DebateAdjudicator.objects.get(
            adjudicator = self.adjudicator,
            debate = self.debate,
        )

        self.data = {
            'aff': self._no_scores(),
            'neg': self._no_scores()
        }

        self._init_side('aff')
        self._init_side('neg')

    def _no_scores(self):
        return dict((i, None) for i in range(1, 5))

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
        for pos in range(1, 5):
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
        scores = [self.data[side][p] for p in range(1, 5)]
        if None in scores:
            return 0
        return sum(scores)


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

        self._other = {
            'aff': 'neg',
            'neg': 'aff',
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

    def _init_side(self, side):
        dt = self.debate.get_dt(side)
        from debate.models import SpeakerScore, TeamScore

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
        except TeamScore.DoesNotExist:
            points = None
            score = None


        self.points[side] = points
        self.total_score[side] = score

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

        self._calc_decision()

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
        from debate.models import TeamScore, SpeakerScore

        dt = self.debate.get_dt(side)
        total = self._score(side)
        points = self._points(side)

        TeamScore.objects.filter(ballot_submission=self.ballots, debate_team=dt).delete()
        TeamScore(ballot_submission=self.ballots, debate_team=dt, score=total, points=points).save()

        SpeakerScore.objects.filter(ballot_submission=self.ballots, debate_team=dt).delete()
        for i in range(1, 5):
            speaker = self.speakers[side][i]
            score = self.get_avg_score(side, i)
            SpeakerScore(
                ballot_submission = self.ballots,
                debate_team = dt,
                speaker = speaker,
                score = score,
                position = i,
            ).save()


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

    def get_speaker_score(self, adj, side, position):
        return (self.get_speaker(side, position), self.get_score(side, position))

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

    @property
    def aff_score(self):
        return self._score('aff')

    @property
    def neg_score(self):
        return self._score('neg')

    def _points(self, side):
        if not self.loaded_sheets:
            return self.points[side]

        if self._score(side):
            if self._score(side) > self._score(self._other[side]):
                return 1
            return 0
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


class DebateResult(object):
    def __init__(self, *args):
        raise TypeError("DebateResult no longer exists, use BallotSet instead.")