"""Debate result classes.

Debate result classes aggregate scoresheets to produce results for an entire
debate, and interact with the database with respect to models recording scores
given in the debate. They do not deal with metadata (like motions), only scores
and results. These classes track team and speaker identities, so that they can
save them to the database.

These classes never read TeamScore instances. When loading existing results,
they rely on scoresheets, which in turn rely on SpeakerScoreByAdj (for voting
decisions) or SpeakerScore (for consensus decisions) to calculate results.
However, these classes do *save* TeamScore objects, overwriting existing objects
if necessary, so that other parts of Tabbycat (e.g., standings) don't have to
recalculate them.

A debate result class is associated with a ballot submission, not a debate. This
allows multiple versions of the result to be retained for a single debate, which
helps avoid data loss when multiple results are (presumably erroneously)
submitted. However, these classes do not edit or save the BallotSubmission
instances; the instance passed to it is used only for looking up related
objects.

Notes on terminology:
 - "Position" in this file always means speaker position as a number. Replies
   take the number one greater than the last substantive speaker.
 - "Side" means the team position, e.g. affirmative (in two-team) or opening
   government (in BP). By convention, these are represented as strings.
 - "Team" refers to the actual team (e.g. Auckland 1).

A few notes on error checking:
 - In general, the validity of 'side' and 'position' arguments aren't checked.
   It is the responsibility of the caller to comply with valid values.
 - When loading from the database, it filters for `self.sides` and
   `self.positions` to prevent queries from returning instances with invalid
   side and position arguments.
 - When scores aren't being used, `self.positions` should be set to an empty
   list. It it assumed that this is sufficient to prevent it from calling
   methods specific to classes inheriting `ScoreMixin` (in scoresheet.py).
"""

import logging
from functools import wraps
from statistics import mean

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator

from .scoresheet import get_scoresheet_class
from .utils import side_and_position_names

logger = logging.getLogger(__name__)


class ResultError(RuntimeError):
    pass


def DebateResult(ballotsub, *args, **kwargs):  # noqa: N802 (factory function)
    """Factory function. Returns an instance of a subclass of BaseDebateResult
    appropriate for the ballot submission's tournament's settings.

    If `tournament` is provided as a keyword argument, the function wil use this
    to determine which subclass it should instantiate, rather than fetching
    `ballotsub.debate.round.tournament`. Callers can use this on repeated calls
    to avoid a deluge of repeated SQL queries.

    The different subclasses have different method signatures. It is the
    responsibility of the caller to ensure that it conforms with the signatures
    of the returned instance. The caller can do so by checking the `.is_voting`
    attribute of the returned instance.
    """
    r = ballotsub.debate.round
    tournament = kwargs.pop('tournament', None)
    if tournament is None:
        tournament = ballotsub.debate.round.tournament
    teams_in_debate = tournament.pref('teams_in_debate')

    if r.ballots_per_debate == 'per-adj' and teams_in_debate == 'two':
        return VotingDebateResult(ballotsub, *args, **kwargs)
    elif r.ballots_per_debate == 'per-debate' and teams_in_debate == 'two':
        return ConsensusDebateResult(ballotsub, *args, **kwargs)
    elif r.ballots_per_debate == 'per-debate' and teams_in_debate == 'bp':
        if r.is_break_round:
            return BPEliminationDebateResult(ballotsub, *args, **kwargs)
        else:
            return BPDebateResult(ballotsub, *args, **kwargs)
    else:
        raise ValueError("Invalid combination for 'ballots_per_debate' and 'teams_in_debate' preferences: %s, %s" %
                (r.ballots_per_debate, teams_in_debate))


class BaseDebateResult:
    """Base class for debate result.

    The base class implements management of debate teams, side allocations and
    team score saving.

    The loading process calls three functions in turn:
      - First, it calls `self.init_blank_buffer()`, which should initialize
        "blank" buffers for all information that it stores to eventually be
        saved to the database.
      - Then, it calls `self.load_from_db()`, which reads the database and
        populates the buffers accordingly.
      - Finally, it calls, `self.assert_loaded()`, which verifies that the
        buffers are of the correct form, and raises an `AssertionError` if they
        are not. (It does not check for completeness, only form.)

    Debate result classes don't edit BallotSubmission instances themselves, only
    objects related to them. Therefore, when saving, this class does NOT call
    `self.ballotsub.save()`. It is the responsibility of the caller to save the
    BallotSubmission. Because this class saves related objects, new
    BallotSubmission instances must have been saved to the database before the
    debate result is saved.

    Subclasses should extend these functions as necessary to accommodate the
    additional buffers they add to the class.

    Subclasses should implement a `teamscorefield_<fieldname>` method for each
    field of TeamScore that is relevant to them, for example,
    `teamscorefield_win(side)` or `teamscorefield_margin(side)`. These methods
    take one argument, a side string, e.g. `'aff'` or `'og'`, and return the
    value that should be saved to that field. When saving TeamScore objects to
    the database, the base class calls these methods to get the value it should
    save to that field. If the method does not exist, it does not write to that
    field, which normally means that the field will be left as null.
    """

    TEAMSCORE_FIELDS = ['points', 'win', 'margin', 'score', 'votes_given', 'votes_possible', 'forfeit']

    # These are used by prefetch_results to determine whether to populate
    # certain fields.
    is_voting = False
    uses_advancing = False
    uses_speakers = False

    def __init__(self, ballotsub, load=True):
        """Constructor.
        `ballotsub` must be a BallotSubmission.

        If `load` is False, the constructor will not load any data from the
        database (at all). It is then the responsibility of the caller to do so;
        the instance will crash otherwise, as the relevant attributes will not
        be created. (For example, in prefetch.py, `populate_results()` uses this
        to load results in bulk.) Callers can use `.init_blank_buffer()` to
        initialize the correct buffers and `.assert_loaded()` to check that data
        was loaded correctly.
        """

        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.tournament = self.debate.round.tournament
        self.sides = self.tournament.sides

        if load:
            self.full_load()

    def __repr__(self):
        return "<{classname} at {id:#x} for {bsub!s}>".format(
            classname=self.__class__.__name__, id=id(self), bsub=self.ballotsub)

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def full_load(self):
        self.init_blank_buffer()
        self.load_from_db()
        self.assert_loaded()

    def init_blank_buffer(self):
        """Initialises the data attributes. External initialisers might find
        this helpful. The `self.sides` and `self.positions` attributes must be
        set prior to calling this function. Subclasses should extend this
        method as necessary.
        """
        self.debateteams = dict.fromkeys(self.sides, None)

    def assert_loaded(self):
        """Raise an AssertionError if there is some problem with the data
        structure. External initialisers might find this helpful. Subclasses
        should extend this method as necessary."""
        assert set(self.debateteams) == set(self.sides)

    def is_complete(self):
        """Returns True if all elements of the results have been populated;
        False if any one is missing.  Logs (but does not raise) the exception if
        self.assert_loaded() fails.

        Subclasses should extend this method as necessary."""

        try:
            self.assert_loaded()
        except AssertionError:
            logger.exception("When checking for completeness, DebateResult.assert_loaded() failed.")
            return False

        if any(self.debateteams[side] is None for side in self.sides):
            return False

        return True

    def is_valid(self):
        """Returns True if the result is a valid result, i.e., contains no
        contradictions. The base implementation just calls `self.is_complete()`.
        If this is overridden, it must return False if `self.is_complete()` is
        False."""
        return self.is_complete()

    def identical(self, other):
        """Returns True of all fields are the same as those in `other`."""
        if self.debateteams != other.debateteams:
            return False
        return True

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_from_db(self):
        """Populates the buffer from the database. Subclasses should extend this
        method as necessary."""
        self.load_debateteams()

    def load_debateteams(self):

        if not self.debate.sides_confirmed:
            return  # don't load if sides aren't confirmed

        debateteams = self.debate.debateteam_set.filter(
                side__in=self.sides).select_related('team')

        for dt in debateteams:
            self.debateteams[dt.side] = dt

    def save(self):
        """Saves to the database.
        Raises ResultError if the ballot set is incomplete or invalid."""

        if not self.is_valid():
            raise ResultError("Tried to save an invalid result.")

        for side in self.sides:
            dt = self.debateteams[side]

            teamscorefields = {}
            for field in self.TEAMSCORE_FIELDS:
                get_field = getattr(self, 'teamscorefield_%s' % field, None)
                if get_field is not None:
                    teamscorefields[field] = get_field(side)

            self.ballotsub.teamscore_set.update_or_create(debate_team=dt,
                    defaults=teamscorefields)

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def set_sides(self, *teams):
        """Sets the sides, saving the sides to the database immediately.
        Arguments must be a list of Team instances, which each must relate to a
        DebateTeam instance in this debate. (Sides are saved immediately to
        enable the use of side keys to refer to teams.)"""

        debateteams_by_team = {dt.team: dt for dt in self.debate.debateteam_set.filter(team__in=teams)}
        for side, team in zip(self.sides, teams):
            try:
                debateteam = debateteams_by_team[team]
            except KeyError:
                raise ValueError("Team %s is not in debate %s" % (team, self.debate))
            debateteam.side = side
            debateteam.save()

        self.debate.sides_confirmed = True
        self.debate.save()

        self.debate._populate_teams()  # refresh
        self.load_debateteams()  # refresh


class BaseDebateResultWithSpeakers(BaseDebateResult):
    """Adds management of speaker identities, ghosts and scores."""

    uses_speakers = True

    def __init__(self, ballotsub, load=True):
        super().__init__(ballotsub, load=False)

        self.positions = self.tournament.positions

        # Hard-coded until low-point wins etc. implemented at form and model level
        self.scoresheet_class = get_scoresheet_class(self.tournament)

        # Note: declared winners aren't currently used, and it's not yet clear
        # to me what the best way is to pass these through to/from Scoresheet.
        self.takes_scores = hasattr(self.scoresheet_class, 'set_score')
        self.takes_declared_winners = hasattr(self.scoresheet_class, 'set_declared_winner')

        if load:
            self.full_load()

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        super().init_blank_buffer()
        self.speakers = {side: dict.fromkeys(self.positions, None) for side in self.sides}
        self.ghosts = {side: dict.fromkeys(self.positions, False) for side in self.sides}

    def assert_loaded(self):
        super().assert_loaded()
        assert set(self.speakers) == set(self.sides)
        assert set(self.ghosts) == set(self.sides)
        for side in self.sides:
            assert set(self.speakers[side]) == set(self.positions)
            assert set(self.ghosts[side]) == set(self.positions)

    def is_complete(self):
        if not super().is_complete():
            return False
        if any(self.speakers[s][p] is None for s in self.sides for p in self.positions):
            return False
        return True

    def identical(self, other):
        if not super().identical(other):
            return False
        if self.speakers != other.speakers:
            return False
        if self.ghosts != other.ghosts:
            return False
        return True

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_from_db(self):
        super().load_from_db()
        self.load_speakers()

    def load_speakers(self):
        """Loads team and speaker identities from the database into the buffer."""

        if not self.debate.sides_confirmed:
            return  # don't load if sides aren't confirmed

        speakerscores = self.ballotsub.speakerscore_set.filter(
            debate_team__side__in=self.sides,
            position__in=self.positions,
        ).select_related('speaker', 'debate_team')

        for ss in speakerscores:
            self.speakers[ss.debate_team.side][ss.position] = ss.speaker
            self.ghosts[ss.debate_team.side][ss.position] = ss.ghost

    def save(self):
        super().save()

        for side in self.sides:
            dt = self.debateteams[side]
            for pos in self.positions:
                speaker = self.speakers[side][pos]
                is_ghost = self.ghosts[side][pos]
                score = self.get_speaker_score(side, pos)
                self.ballotsub.speakerscore_set.update_or_create(debate_team=dt,
                    position=pos, defaults=dict(speaker=speaker, score=score, ghost=is_ghost))

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def get_speaker(self, side, position):
        return self.speakers[side].get(position)

    def set_speaker(self, side, position, speaker):
        if self.debateteams[side] is None:
            raise TypeError("Set sides using self.set_sides() before setting speakers")
        team = self.debateteams[side].team
        if speaker not in team.speakers:
            logger.error("Speaker %s isn't in team %s", speaker.name, team.short_name)
            return
        self.speakers[side][position] = speaker

    def get_ghost(self, side, position):
        return self.ghosts[side].get(position)

    def set_ghost(self, side, position, is_ghost):
        self.ghosts[side][position] = is_ghost

    def get_speaker_score(self, side, position):
        raise NotImplementedError

    # --------------------------------------------------------------------------
    # Other common functionality (helper functions)
    # --------------------------------------------------------------------------

    def calculate_margin(self, side):
        # The purpose of this function is to prevent code duplication between
        # other functions that require a teamscorefield_margin() method.
        aff_total = self.teamscorefield_score('aff')
        neg_total = self.teamscorefield_score('neg')

        if aff_total is None or neg_total is None:
            return None

        if side == 'aff':
            return aff_total - neg_total
        elif side == 'neg':
            return neg_total - aff_total
        else:
            raise ValueError("side must be 'aff' or 'neg'")

    def sheet_as_dicts(self, sheet):
        """Returns a list of dicts, each being a team in the debate. Used by
        subclasses' `as_dicts()` methods."""
        teams = []
        for side, (side_name, pos_names) in zip(self.sides, side_and_position_names(self.tournament)):
            side_dict = {
                "side": side_name,
                "team": self.debateteams[side].team,
                "total": sheet.get_total(side),
                "speakers": [],
            }

            # Colour result according to outcome of debate
            if hasattr(sheet, 'winner'):
                side_dict["win_style"] = "success" if sheet.winner() == side else "danger"
            elif hasattr(sheet, 'rank'):
                rank = sheet.rank(side)
                if rank:
                    side_dict["win_style"] = ["success", "info", "warning", "danger"][rank-1]

            for pos, pos_name in zip(self.positions, pos_names):
                side_dict["speakers"].append({
                    "pos": pos,
                    "name": pos_name,
                    "speaker": self.get_speaker(side, pos),
                    "score": sheet.get_score(side, pos),
                })
            teams.append(side_dict)
        return teams


class VotingDebateResult(BaseDebateResultWithSpeakers):
    """Instantiates a scoresheet for each voting adjudicator, and calculates
    the decision according to a majority vote among them."""

    is_voting = True

    def __init__(self, ballotsub, load=True):
        super().__init__(ballotsub, load)
        self._decision_calculated = False

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        super().init_blank_buffer()
        self.debateadjs = {}   # don't load adjudicators, it's a database hit
        self.scoresheets = {}

    def assert_loaded(self):
        super().assert_loaded()
        assert set(self.debate.adjudicators.voting()) == set(self.scoresheets)
        assert set(self.debateadjs) == set(self.scoresheets)
        assert self.sides == ['aff', 'neg'], "VotingDebateResult can only be used for two-team formats."

    def is_complete(self):
        if not super().is_complete():
            return False
        if not self.debate.adjudicators.has_chair:
            return False
        if not all(sheet.is_complete() for sheet in self.scoresheets.values()):
            return False
        return True

    def is_valid(self):
        return super().is_valid() and all(sheet.is_valid() for sheet in self.scoresheets.values())

    def identical(self, other):
        if not super().identical(other):
            return False
        if not set(self.scoresheets.keys()) == set(other.scoresheets.keys()):
            return False
        for adj, other_sheet in other.scoresheets.items():
            if not self.scoresheets[adj].identical(other_sheet):
                return False
        return True

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_from_db(self):
        super().load_from_db()
        self.load_scoresheets()

    def load_scoresheets(self):
        debateadjs = self.debate.debateadjudicator_set.exclude(type=DebateAdjudicator.TYPE_TRAINEE).select_related('adjudicator')
        self.debateadjs = {da.adjudicator: da for da in debateadjs}
        self.scoresheets = {adj: self.scoresheet_class(self.positions) for adj in self.debateadjs.keys()}

        speakerscorebyadjs = self.ballotsub.speakerscorebyadj_set.filter(
            debate_adjudicator__in=debateadjs,
            debate_team__side__in=self.sides,
            position__in=self.positions,
        ).select_related('debate_adjudicator__adjudicator', 'debate_adjudicator__adjudicator__institution', 'debate_team')

        for ssba in speakerscorebyadjs:
            self.set_score(ssba.debate_adjudicator.adjudicator,
                    ssba.debate_team.side, ssba.position, ssba.score)

    def save(self):
        super().save()

        for adj, sheet in self.scoresheets.items():
            da = self.debateadjs[adj]
            for side in self.sides:
                dt = self.debateteams[side]
                for pos in self.positions:
                    self.ballotsub.speakerscorebyadj_set.update_or_create(
                        debate_team=dt, debate_adjudicator=da, position=pos,
                        defaults=dict(score=self.get_score(adj, side, pos)))

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def get_score(self, adjudicator, side, position):
        try:
            return self.scoresheets[adjudicator].get_score(side, position)
        except AttributeError:
            logger.exception("Tried to get score, but scoresheet doesn't do scores. "
                    "self.takes_scores is %s", self.takes_scores)
            return None

    def set_score(self, adjudicator, side, position, score):
        scoresheet = self.scoresheets[adjudicator]
        try:
            scoresheet.set_score(side, position, score)
        except AttributeError:
            logger.exception("Tried to set score, but scoresheet doesn't do scores. "
                    "self.takes_scores is %s", self.takes_scores)

    def get_declared_winner(self, adjudicator):
        """Not currently used, in place for future implementation of declared winners."""
        try:
            return self.scoresheets[adjudicator].get_declared_winner()
        except AttributeError:
            logger.exception("Tried to get declared winner, but scoresheet doesn't do declared winners. "
                    "self.takes_declared_winners is %s", self.takes_declared_winners)
            return None

    def set_declared_winner(self, adjudicator, declared_winner):
        """Not currently used, in place for future implementation of declared winners."""
        try:
            return self.scoresheets[adjudicator].set_declared_winner(declared_winner)
        except AttributeError:
            logger.exception("Tried to set declared winner, but scoresheet doesn't do declared winners. "
                    "self.takes_declared_winners is %s", self.takes_declared_winners)

    # --------------------------------------------------------------------------
    # Decision calculation
    # --------------------------------------------------------------------------

    def _calculate_decision(self):
        """Calculates the majority decision and puts the adjudicators for each
        team in self._adjs_by_side and the winning DebateTeam in self._winner.
        If the panel is evenly split, it awards the debate to the team for which
        the chair voted.

        Raises ResultError if the ballot set is incomplete or invalid, or if
        any scoresheet doesn't have a winner.
        """

        if not self.is_valid():
            raise ResultError("Tried to calculate decision on an invalid ballot set.")

        self._adjs_by_side = {side: [] for side in self.sides} # group adjs by vote
        for adj, sheet in self.scoresheets.items():
            winner = sheet.winner()
            if winner is None:  # should never happen
                raise ResultError("The scoresheet for %s does not have a winner." % adj.name)
            self._adjs_by_side[winner].append(adj)

        votes_aff = len(self._adjs_by_side['aff'])
        votes_neg = len(self._adjs_by_side['neg'])

        if votes_aff > votes_neg:
            self._winner = 'aff'
        elif votes_neg > votes_aff:
            self._winner = 'neg'
        else:
            logger.warning("Adjudicators split %d-%d in debate %s, awarding by chair casting vote.", votes_aff, votes_neg, self.debate)
            self._winner = self.scoresheets[self.debate.adjudicators.chair].winner()

        self._decision_calculated = True

    def _requires_decision(default): # noqa: N805
        def wrap(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                if not self.is_complete():
                    return default
                if not self._decision_calculated:
                    self._calculate_decision()
                return func(self, *args, **kwargs)
            return wrapped
        return wrap

    @_requires_decision([])
    def majority_adjudicators(self):
        return self._adjs_by_side[self._winner]

    def relevant_adjudicators(self):
        if self.tournament.pref('margin_includes_dissenters'):
            return self.scoresheets.keys()
        else:
            return self.majority_adjudicators()

    def winning_side(self):
        return self._winner

    @_requires_decision(None)
    def winning_team(self):
        return self.debateteams[self._winner].team

    @_requires_decision(None)
    def get_speaker_score(self, side, position):
        return mean(self.scoresheets[adj].get_score(side, position) for adj in self.relevant_adjudicators())

    # --------------------------------------------------------------------------
    # Team score fields
    # --------------------------------------------------------------------------

    @_requires_decision(None)
    def teamscorefield_points(self, side):
        return int(side == self._winner)

    @_requires_decision(None)
    def teamscorefield_win(self, side):
        return side == self._winner

    @_requires_decision(None)
    def teamscorefield_score(self, side):
        return mean(self.scoresheets[adj].get_total(side) for adj in self.relevant_adjudicators())

    @_requires_decision(None)
    def teamscorefield_margin(self, side):
        return self.calculate_margin(side)

    @_requires_decision(None)
    def teamscorefield_votes_given(self, side):
        return len(self._adjs_by_side[side])

    def teamscorefield_votes_possible(self, side):
        return len(self.scoresheets)

    # --------------------------------------------------------------------------
    # Method for UI display
    # --------------------------------------------------------------------------

    def adjudicators_with_splits(self):
        """Iterator. Each iteration is a 3-tuple (adj, adjtype, split), where
        adjtype is a AdjudicatorAllocation.POSITION_* constant, adj is an
        Adjudicator object, and split is True if the adjudicator was in the
        minority and not a trainee, False if the adjudicator was in the majority
        or is a trainee. If there is no available result, split is always
        False.

        Raises a ResultError if the scoresheet is invalid."""

        self._calculate_decision()
        majority = self.majority_adjudicators()
        for adj, adjtype in self.debate.adjudicators.with_positions():
            split = adj not in majority and adjtype != AdjudicatorAllocation.POSITION_TRAINEE
            yield adj, adjtype, split

    def as_dicts(self):
        """Generates a sequence of dicts, each being a scoresheet from an
        adjudicator. This is used in PublicBallotScoresheetsView, which uses
        template public_ballot_set.html."""

        for adj in self.debate.adjudicators.voting():
            sheet_dict = {
                "adjudicator": adj,
                "teams": self.sheet_as_dicts(self.scoresheets[adj])
            }
            sheet_dict["adjudicator"] = adj
            yield sheet_dict


class BaseConsensusDebateResultWithSpeakers(BaseDebateResultWithSpeakers):
    """Basically a wrapper for a single scoresheet. Knows nothing about
    adjudicators."""

    is_voting = False

    def __init__(self, ballotsub, load=True):
        super().__init__(ballotsub, load=False)
        self.scoresheet = self.scoresheet_class(self.positions)
        if load:
            self.full_load()

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def is_complete(self):
        return super().is_complete() and self.scoresheet.is_complete()

    def is_valid(self):
        return super().is_valid() and self.scoresheet.is_valid()

    def identical(self, other):
        return super().identical(other) and self.scoresheet.identical(other.scoresheet)

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_from_db(self):
        super().load_from_db()
        self.load_scoresheet()

    def load_scoresheet(self):
        speakerscores = self.ballotsub.speakerscore_set.filter(
            debate_team__side__in=self.sides,
            position__in=self.positions
        ).select_related('debate_team')

        for ss in speakerscores:
            self.set_score(ss.debate_team.side, ss.position, ss.score)

    def save(self):
        super().save()

        for side in self.sides:
            dt = self.debateteams[side]
            for pos in self.positions:
                self.ballotsub.speakerscore_set.update_or_create(
                    debate_team=dt, position=pos,
                    defaults=dict(score=self.get_score(side, pos)))

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def get_score(self, side, position):
        try:
            return self.scoresheet.get_score(side, position)
        except AttributeError:
            logger.exception("Tried to get score, but scoresheet doesn't do scores. "
                    "self.takes_scores is %s", self.takes_scores)
            return None

    get_speaker_score = get_score  # for BaseDebateResult.save()

    def set_score(self, side, position, score):
        try:
            self.scoresheet.set_score(side, position, score)
        except AttributeError:
            logger.exception("Tried to set score, but scoresheet doesn't do scores. "
                    "self.takes_scores is %s", self.takes_scores)

    # --------------------------------------------------------------------------
    # Method for UI display
    # --------------------------------------------------------------------------

    def as_dicts(self):
        """Generates a sequence of dicts, each being a scoresheet from an
        adjudicator. This is used in PublicBallotScoresheetsView, which uses
        template public_ballot_set.html."""
        return [{"teams": self.sheet_as_dicts(self.scoresheet)}]


class ConsensusDebateResult(BaseConsensusDebateResultWithSpeakers):
    """For consensus decisions in two-team formats."""

    def winning_side(self):
        return self.scoresheet.winner()

    def winning_team(self):
        return self.debateteams[self.scoresheet.winner()].team

    def teamscorefield_points(self, side):
        return int(side == self.winning_side())

    def teamscorefield_win(self, side):
        return side == self.winning_side()

    def teamscorefield_score(self, side):
        return self.scoresheet.get_total(side)

    def teamscorefield_margin(self, side):
        return self.calculate_margin(side)


class BPDebateResult(BaseConsensusDebateResultWithSpeakers):
    """For British Parliamentary preliminary rounds."""

    def teamscorefield_points(self, side):
        return 4 - self.scoresheet.rank(side)

    def teamscorefield_score(self, side):
        return self.scoresheet.get_total(side)


class BaseEliminationDebateResult(BaseDebateResult):
    pass


class BPEliminationDebateResult(BaseEliminationDebateResult):
    """For British Parliamentary elimination rounds.  Does not take speaker
    identities, speaker scores or ranks.  Instead, it just notes the two
    advancing teams, using the `win` field, which is set to True for both of
    the advancing teams."""

    is_voting = False
    uses_advancing = True

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        super().init_blank_buffer()
        # To be complete, this list must have two sides in it, but we don't
        # enforce anything before checking completeness.
        self.advancing = []

    def is_complete(self):
        if not super().is_complete():
            return False
        if len(set(self.advancing)) != 2:
            return False
        return all(x in self.sides for x in self.advancing)

    def identical(self, other):
        if not super().identical(other):
            return False
        if self.advancing != other.advancing:
            return False
        return True

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_from_db(self):
        super().load_from_db()
        self.load_advancing()

    def load_advancing(self):
        queryset = self.ballotsub.teamscore_set.filter(
            debate_team__side__in=self.sides, win=True
        ).values_list('debate_team__side', flat=True)
        self.advancing = list(queryset)

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def set_advancing(self, sides):
        """Sets the advancing teams to those on the sides listed in `sides`.
        `sides` must be a list of two BP sides. If it's not, this method raises
        a ValueError."""
        if not all(x in self.sides for x in self.advancing):
            raise ValueError("Found invalid sides: %s" % sides)
        if len(sides) != 2:
            raise ValueError("Exactly two sides should be advancing, found: %s" % sides)
        self.advancing = sides

    def advancing_sides(self):
        return self.advancing

    def advancing_teams(self):
        """Returns the teams advancing from this debate. Doesn't check that the
        number of advancing teams is exactly two, which might be the case if
        this result was loaded from the database or if the result is incomplete.
        If that property is important, callers should check it themselves."""
        return [self.debateteams[side].team for side in self.advancing]

    # --------------------------------------------------------------------------
    # Team score fields
    # --------------------------------------------------------------------------

    def teamscorefield_win(self, side):
        return side in self.advancing


class ForfeitDebateResult(BaseDebateResult):
    # This is WADL-specific for now

    def __init__(self, ballotsub, forfeiter, load=True):
        super().__init__(ballotsub, load=False) # never load from database
        self.forfeiter = forfeiter
        if load:
            self.full_load()

    def teamscorefield_points(self, side):
        return int(side != self.forfeiter)

    def teamscorefield_win(self, side):
        return side != self.forfeiter

    def teamscorefield_forfeit(self, side):
        return True
