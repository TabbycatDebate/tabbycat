from django.core.exceptions import ObjectDoesNotExist

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam

class ResultError(RuntimeError):
    pass

class Scoresheet(object):
    """Representation of a single adjudicator's scoresheet in a single ballot
    submission, providing an interface that abstracts away database operations.
    Each instance initializes itself with the appropriate data on construction.

    The interface to the client (views and forms) uses Teams and Adjudicators
    (not DebateTeams and DebateAdjudicators), and raises a DoesNotExist error if
    a team or adjudicator not associated with the debate is supplied. Instead,
    'aff' and 'neg' can also be used to specify teams, but this will only work
    if team positions are already known.

    This class does *not* deal with any information about the *identity* of the
    speakers involved. That is all done in the BallotSet class, which comprises
    (among other things) one or more instances of this class. This class merely
    stores raw scores awarded by a particular adjudicator (in a particular
    submission), attaching scores to positions.

    Internally, scores are stored in a nested dictionary self.data, such that
        self.data[debateteam][pos] = score.
    This is known as the "buffer"."""

    def __init__(self, ballotsub, adjudicator):
        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.adjudicator = adjudicator
        self.da = self.debate.debateadjudicator_set.get(adjudicator=adjudicator)
        self.dts = self.debate.debateteam_set.all() # note, this is a QuerySet
        self.POSITIONS = self.debate.round.tournament.POSITIONS
        self.data = {dt: dict.fromkeys(self.POSITIONS, None) for dt in self.dts}
        for dt in self.dts:
            self._load_team(dt)

    def _dt(self, team):
        """Extracts a DebateTeam from a given team argument. The argument can be
        either a Team or 'aff'/'neg'."""
        if team in ['aff', 'neg']:
            return self.debate.get_dt(team)
        try:
            return self.dts.get(team=team)
        except ObjectDoesNotExist:
            raise ValueError("The team %s is not in the debate for this scoresheet." % team)

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    @property
    def is_complete(self):
        return all(all(self.data[dt][p] is not None for p in self.POSITIONS) \
                for dt in self.dts)

    def save(self):
        """Saves the information in this instance to the database."""
        assert self.is_complete, "Tried to save scoresheet when it is incomplete"
        self.ballotsub.speakerscorebyadj_set.filter(debate_adjudicator=self.da).delete()
        for dt in self.dts:
            self._save_team(dt)

    def _load_team(self, dt):
        """Loads the scores for the given DebateTeam from the database into the
        buffer."""
        scores = self.ballotsub.speakerscorebyadj_set.filter(
                debate_adjudicator=self.da, debate_team=dt)
        for ss in scores:
            self._set_score(dt, ss.position, ss.score)

    def _save_team(self, dt):
        """Saves the scores in the buffer for the given DebateTeam, to the
        database."""
        for pos in self.POSITIONS:
            self.ballotsub.speakerscorebyadj_set.create(
                debate_adjudicator=self.da,
                debate_team=dt,
                position=pos,
                score=self._get_score(dt, pos),
            )

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def set_score(self, team, position, score):
        """Sets the score for the given team and position in the data buffer,
        not saved to database."""
        return self._set_score(self._dt(team), position, score)

    def get_score(self, team, position):
        """Returns the score for the given team and position, reading from the
        data buffer."""
        return self._get_score(self._dt(team), position) or 0 # don't return None

    def get_total(self, team):
        """Returns the team score for the given team, reading from the data
        buffer."""
        return self._get_total(self._dt(team))

    @property
    def winner(self):
        """Returns the winner as a Team object."""
        return self._get_winner().team

    def _set_score(self, dt, position, score):
        self.data[dt][position] = score

    def _get_score(self, dt, position):
        return self.data[dt][position]

    def _get_total(self, dt):
        """Returns the team score for the given DebateTeam, or None if the
        scores are incomplete."""
        scores = [self.data[dt][p] for p in self.POSITIONS]
        if None in scores:
            return None
        return sum(scores)

    def _get_winner(self):
        """Returns the winner as a DebateTeam, or None if scoresheet is
        incomplete or if it is a draw."""
        if not self.is_complete:
            return None
        dts = list(self.dts) # fix order for loops
        totals = [self._get_total(dt) for dt in dts]
        max_total = max(totals)
        if totals.count(max_total) > 1:
            return None
        for dt, total in zip(dts, totals):
            if total == max_total:
                return dt
        raise RuntimeError("Unexpected error") # this should never happen

    # --------------------------------------------------------------------------
    # Side-specific methods
    # --------------------------------------------------------------------------

    @property
    def aff_score(self):
        return self._get_total(self.debate.aff_dt)

    @property
    def neg_score(self):
        return self._get_total(self.debate.neg_dt)

    @property
    def aff_win(self):
        return self.aff_score > self.neg_score

    @property
    def neg_win(self):
        return self.neg_score > self.aff_score


class BallotSet(object):
    """Representation of a set of ballots for a debate in a single ballot
    submission, providing an interface that abstracts away database operations.
    In particular, this class makes it easier for views and forms to work with a
    set of ballots, acting as a translation layer on top of the
    BallotSubmission, TeamScore, SpeakerScore and Motion models. Each instance
    initializes itself with the appropriate data on construction.

    The interface to the client (views and forms) uses Teams and Adjudicators
    (not DebateTeams and DebateAdjudicators), and raises a DoesNotExist error if
    a team or adjudicator not associated with the debate is supplied. Instead,
    'aff' and 'neg' can also be used to specify teams, but this will only work
    if team positions are already known.

    Specifcally, this class performs the following (non-trivial) functions:
      - Keeps track of which speaker spoke in which position.
      - Figures out which adjudicators are in the majority.
      - Calculates the majority-average speaker scores.
    """


    def __init__(self, ballotsub):
        """Constructor.
        'ballotsub' must be a BallotSubmission.
        """
        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.adjudicators = self.debate.adjudicators.list
        self.dts = self.debate.debateteam_set.all() # note, this is a QuerySet
        assert self.dts.count() == 2, "There aren't two DebateTeams in this debate: %s." % self.debate

        self.SIDES = (DebateTeam.POSITION_AFFIRMATIVE, DebateTeam.POSITION_NEGATIVE)
        self.POSITIONS = self.debate.round.tournament.POSITIONS

        self.loaded_sheets = False
        self._adjudicator_sheets = None

        self.speakers = {dt: {} for dt in self.dts}
        self.motion_veto = dict.fromkeys(self.dts, None)

        self.points_from_db      = dict.fromkeys(self.dts, None)
        self.total_score_from_db = dict.fromkeys(self.dts, None)
        self.wins_from_db        = dict.fromkeys(self.dts, None)
        self.margins_from_db     = dict.fromkeys(self.dts, None)

        self._other = {self.dts[0]: self.dts[1], self.dts[1]: self.dts[0]}

        for dt in self.dts:
            self._load_team(dt)

    def _dt(self, team):
        """Extracts a DebateTeam from a given team argument. The argument can be
        either a Team or 'aff'/'neg'."""
        if team in ['aff', 'neg']:
            return self.debate.get_dt(team)
        try:
            return self.dts.get(team=team)
        except ObjectDoesNotExist:
            raise ValueError("The team %s is not in the debate for this scoresheet." % team)

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    @property
    def adjudicator_sheets(self):
        if not self._adjudicator_sheets:
            self._adjudicator_sheets = {a: Scoresheet(self.ballotsub, a)
                    for a in self.adjudicators}
            self.loaded_sheets = True
        return self._adjudicator_sheets

    @property
    def is_complete(self):
        return all(sheet.is_complete for sheet in self.adjudicator_sheets.values())

    def save(self):
        assert self.is_complete, "Tried to save ballot set when it is incomplete"

        self.ballotsub.save() # need BallotSubmission object to exist first
        for sheet in self.adjudicator_sheets.values():
            sheet.save()
        self._calc_decision()
        for dt in self.dts:
            self._save_team(dt)
        self.ballotsub.save()

    def _load_team(self, dt):
        """Loads the scores for the given DebateTeam from the database into the
        buffer."""
        for ss in self.ballotsub.speakerscore_set.filter(debate_team=dt):
            self.speakers[dt][ss.position] = ss.speaker
            # ignore the speaker score itself, just look at SpeakerScoreByAdjs

        try:
            ts = self.ballotsub.teamscore_set.get(debate_team=dt)
            self.points_from_db[dt] = ts.points
            self.total_score_from_db[dt] = ts.score
            self.wins_from_db[dt] = ts.win
            self.margins_from_db[dt] = ts.margin
        except ObjectDoesNotExist:
            self.points_from_db[dt] = None
            self.total_score_from_db[dt] = None
            self.wins_from_db[dt] = None
            self.margins_from_db[dt] = None

        try:
            dtmp = self.ballotsub.debateteammotionpreference_set.get(
                    debate_team=dt, preference=3)
            self.motion_veto[dt] = dtmp.motion
        except ObjectDoesNotExist:
            self.motion_veto[dt] = None

    def _save_team(self, dt):
        """Saves the TeamScores, SpeakerScores and DebateTeamMotionPreferences
        for the given DebateTeam."""
        total = self._get_avg_total(dt)
        points = self._get_points(dt)
        win = self._get_win(dt)
        margin = self._get_margin(dt)
        self.ballotsub.teamscore_set.filter(debate_team=dt).delete()
        self.ballotsub.teamscore_set.create(debate_team=dt, score=total,
                points=points, win=win, margin=margin)

        self.ballotsub.speakerscore_set.filter(debate_team=dt).delete()
        for pos in self.POSITIONS:
            speaker = self.speakers[dt][pos]
            score = self._get_avg_score(dt, pos)
            self.ballotsub.speakerscore_set.create(debate_team=dt,
                    speaker=speaker, score=score, position=pos)

        self.ballotsub.debateteammotionpreference_set.filter(debate_team=dt,
                preference=3).delete()
        if self.motion_veto[dt] is not None:
            self.ballotsub.debateteammotionpreference_set.create(debate_team=dt,
                    preference=3, motion=self.motion_veto[dt])

    # --------------------------------------------------------------------------
    # Data setting and retrieval (speakers and per-adjudicator scores)
    # --------------------------------------------------------------------------

    def set_sides(self, *teams):
        """Sets the sides, saving the sides to the database immediately. The
        first team is the affirmative team, the second team is the negative
        team. (Sides are saved immediately to enable the use of 'aff' and 'neg'
        to refer to teams.)"""
        dts = list(map(self._dt, teams))
        for position, dt in zip(self.SIDES, dts):
            dt.position = position
            dt.save()
        self.dts = self.debate.debateteam_set.all() # refresh self.dts

    def get_speaker(self, team, position):
        """Returns the speaker object for team/position."""
        return self._get_speaker(self._dt(team), position)

    def get_score(self, adj, team, position):
        """Returns the score given by the adjudicator for the speaker in this
        team and position."""
        return self._get_score(adj, self._dt(team), position)

    def get_avg_score(self, team, position):
        """Returns the average score of majority adjudicators for this team and
        position."""
        return self._get_avg_score(self._dt(team), position)

    def set_speaker(self, team, position, speaker):
        """Sets the identity of the speaker in this team and position.
        Raises an exception if the speaker isn't in the team."""
        return self._set_speaker(self._dt(team), position, speaker)

    def set_score(self, adj, team, position, score):
        """Set the score given by adjudicator for this team and position."""
        return self._set_score(adj, self._dt(team), position, score)

    def _get_speaker(self, dt, position):
        return self.speakers[dt].get(position)

    def _get_score(self, adj, dt, position):
        return self.adjudicator_sheets[adj]._get_score(dt, position)

    def _get_avg_score(self, dt, position):
        if not self.is_complete:
            return None
        return sum(self.adjudicator_sheets[adj]._get_score(dt, position)
                   for adj in self.majority_adj) / len(self.majority_adj)

    def _set_speaker(self, dt, position, speaker):
        if speaker not in dt.team.speakers:
            raise ValueError("Speaker %s isn't in team %s" % (speaker.name, dt.team.short_name))
        self.speakers[dt][position] = speaker

    def _set_score(self, adj, dt, position, score):
        self.adjudicator_sheets[adj]._set_score(dt, position, score)

    # --------------------------------------------------------------------------
    # Data setting and retrieval (properties of BallotSubmission)
    # --------------------------------------------------------------------------

    @property
    def confirmed(self):
        return self.ballotsub.confirmed

    @confirmed.setter
    def confirmed(self, new):
        self.ballotsub.confirmed = new

    @property
    def discarded(self):
        return self.ballotsub.discarded

    @discarded.setter
    def discarded(self, new):
        self.ballotsub.discarded = new

    @property
    def motion(self):
        return self.ballotsub.motion

    @motion.setter
    def motion(self, new):
        self.ballotsub.motion = new

    def get_motion_veto(self, team):
        return self.motion_veto[self._dt(team)]

    def set_motion_veto(self, team, motion):
        self.motion_veto[self._dt(team)] = motion

    # --------------------------------------------------------------------------
    # Decision and majority methods
    # --------------------------------------------------------------------------

    def _calc_decision(self):
        """Calculates the majority decision and puts the majority adjudicators
        in self._majority_adj and the winning DebateTeam in self._winner. Raises
        AssertionError if scores are incomplete. Raises ResultError there is a
        draw somewhere among the adjudicators, or overall."""
        assert self.is_complete, "Tried to calculate decision on an incomplete ballot set."

        adjs_by_dt = {dt: [] for dt in self.dts} # group adjs by vote
        for adj, sheet in self.adjudicator_sheets.items():
            winner = sheet._get_winner()
            if winner is None:
                raise ResultError("The scoresheet for %s does not have a winner." % adj.name)
            adjs_by_dt[winner].append(adj)

        counts = {dt: len(adjs) for dt, adjs in adjs_by_dt.items()}
        max_count = max(counts.values()) # check that we have a majority
        if max_count < len(self.adjudicators) // 2 + 1:
            raise ResultError("No team had a majority in %s." % self.debate.matchup)

        for dt, count in counts.items(): # set self._majority_adj
            if count == max_count:
                self._majority_adj = adjs_by_dt[dt]
                self._winner = dt
                break

    @property
    def majority_adj(self):
        if not self.is_complete:
            return []
        try:
            return self._majority_adj
        except AttributeError:
            self._calc_decision()
            return self._majority_adj

    @property
    def winner(self):
        """Returns the winner of the debate as a Team object."""
        if not self.is_complete:
            return None
        try:
            return self._winner.team
        except AttributeError:
            self._calc_decision()
            return self._winner.team

    def get_avg_total(self, team):
        return self._get_avg_total(self._dt(team))

    def _get_avg_total(self, dt):
        if not self.loaded_sheets:
            return self.total_score_from_db[dt]
        return sum(self.adjudicator_sheets[adj]._get_total(dt) for adj in
                   self.majority_adj) / len(self.majority_adj)

    def _dissenting_inclusive_score(self, dt):
        dissenting_score = sum(self.adjudicator_sheets[adj]._get_total(dt) for adj in
                   self.adjudicators) / len(self.adjudicators)
        return dissenting_score

    # Abstracted to not be tied to wins
    def _get_points(self, dt):
        if not self.loaded_sheets:
            return self.points_from_db[dt]

        if self._get_avg_total(dt):
            if self._get_avg_total(dt) > self._get_avg_total(self._other[dt]):
                return 1
            return 0

        return None

    # Supplants _points; ie its a count of the number of wins
    def _get_win(self, dt):
        if not self.loaded_sheets:
            return self.wins_from_db[dt]

        if self._get_avg_total(dt):
            if self._get_avg_total(dt) > self._get_avg_total(self._other[dt]):
                return True
            return False

        return None

    def _get_margin(self, dt):
        if not self.loaded_sheets:
            return self.margins_from_db[dt]

        if self.debate.round.tournament.preferences.get_by_name('margin_includes_dissenters') is False:
            if self._get_avg_total(dt) and self._get_avg_total(self._other[dt]):
                return self._get_avg_total(dt) - self._get_avg_total(self._other[dt])
        else:
            if self._dissenting_inclusive_score(dt) and self._dissenting_inclusive_score(self._other[dt]):
                dissenting_inclusive_margin = self._dissenting_inclusive_score(dt) - self._dissenting_inclusive_score(self._other[dt])
                return dissenting_inclusive_margin

        return None

    # --------------------------------------------------------------------------
    # Side-specific methods
    # --------------------------------------------------------------------------

    @property
    def aff_score(self):
        return self._get_avg_total(self.debate.aff_dt)

    @property
    def neg_score(self):
        return self._get_avg_total(self.debate.neg_dt)

    @property
    def aff_points(self):
        return self._get_points(self.debate.aff_dt)

    @property
    def neg_points(self):
        return self._get_points(self.debate.neg_dt)

    @property
    def aff_win(self):
        return self.aff_points

    @property
    def neg_win(self):
        return self.neg_points

    @property
    def aff_motion_veto(self):
        return self.motion_veto[self.debate.aff_dt]

    @aff_motion_veto.setter
    def aff_motion_veto(self, new):
        self.motion_veto[self.debate.aff_dt] = new

    @property
    def neg_motion_veto(self):
        return self.motion_veto[self.debate.neg_dt]

    @neg_motion_veto.setter
    def neg_motion_veto(self, new):
        self.motion_veto[self.debate.neg_dt] = new

    # --------------------------------------------------------------------------
    # Methods for UI display
    # --------------------------------------------------------------------------

    def _is_trainee(self, adj):
        da = self.debate.debateadjudicator_set.get(adjudicator=adj)
        return da.type == DebateAdjudicator.TYPE_TRAINEE

    @property
    def adjudicator_results(self):
        """Iterator. Each iteration is a 3-tuple (adjtype, adj, split), where
        adjtype is a DebateAdjudicator.TYPE_* constant, adj is an Adjudicator
        object, and split is True if the adjudicator was in the minority and
        not a trainee, False if the adjudicator was in the majority or is a
        trainee. If there is no available result, split is always False."""
        try:
            self._calc_decision()
        except (ResultError, AssertionError):
            for adjtype, adj in self.debate.adjudicators:
                yield adjtype, adj, False
        else:
            for adjtype, adj in self.debate.adjudicators:
                yield adjtype, adj, (adj not in self.majority_adj and
                        adjtype != DebateAdjudicator.TYPE_TRAINEE)

    @property
    def sheet_iter(self):
        """Usage:

        for sheet in ballotset.sheet_iter:
            print sheet.adjudicator
            for pos in sheet.affs:
                print pos.name, pos.speaker, pos.score
            print sheet.aff_score, sheet.aff_win
            for pos in sheet.negs:
                print pos.name, pos.speaker, pos.score
            print sheet.neg_score, sheet.neg_win
        """
        REPLY_POSITION = self.debate.round.tournament.REPLY_POSITION
        POSITIONS = self.debate.round.tournament.POSITIONS
        ballotset = self # provide access in inner classes

        class Position(object):

            def __init__(self, sheet, side, pos):
                self.sheet = sheet
                self.pos = pos
                self.side = side

            @property
            def name(self):
                return "Reply" if (self.pos == REPLY_POSITION) else str(self.pos)

            @property
            def speaker(self):
                return ballotset.get_speaker(self.side, self.pos)

            @property
            def score(self):
                return self.sheet.get_score(self.side, self.pos)

        class ScoresheetWrapper(object):

            def __init__(self, adj):
                self.sheet = ballotset.adjudicator_sheets[adj]
                self.adjudicator = adj

            def position_iter(self, side):
                for pos in POSITIONS:
                    yield Position(self.sheet, side, pos)

            @property
            def affs(self):
                return self.position_iter('aff')

            @property
            def negs(self):
                return self.position_iter('neg')

            @property
            def aff_score(self):
                return self.sheet.aff_score

            @property
            def neg_score(self):
                return self.sheet.neg_score

            @property
            def aff_win(self):
                return self.sheet.aff_win

            @property
            def neg_win(self):
                return self.sheet.neg_win

        for adj in self.adjudicators:
            yield ScoresheetWrapper(adj)


class ForfeitBallotSet(BallotSet):
    # This is WADL-specific for now

    def __init__(self, ballotsub, forfeiter):
        """Constructor.
        'ballotsub' must be a BallotSubmission.
        """
        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.adjudicators = self.debate.adjudicators.list
        self.forfeiter = forfeiter
        self.motion_veto = None
        self.dts = self.debate.debateteam_set.all() # note, this is a QuerySet

    def _save_team(self, dt):
        if self.forfeiter == dt:
            points = 0
            win = False
        else:
            points = 2
            win = True

        # Note: forfeited debates have fake scores/margins, thus the affects_average toggle
        self.ballotsub.teamscore_set.filter(debate_team=dt).delete()
        self.ballotsub.teamscore_set.create(debate_team=dt, points=points,
                win=win, score=0, margin=0, affects_averages=False)

    def save(self):
        self.ballotsub.forfeit = self.forfeiter
        self.ballotsub.save()
        for dt in self.dts:
            self._save_team(dt)


