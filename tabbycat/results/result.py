"""Debate result classes.

Debate result classes aggregate scoresheets to produce results for an entire
debate, and interact with the database with respect to models recording scores
given in the debate. They do not deal with metadata (like motions), only scores
and results. These classes track team and speaker identities, so that they can
save them to the database.

These classes never read TeamScore instances. When loading existing results,
they rely on scoresheets, which in turn rely on SpeakerScoreByAdj (for voting
decisions), SpeakerScore (for consensus decisions), and TeamScoreByAdj (for
declared winner decisions) to calculate results. However, these classes do
*save* TeamScore objects, overwriting existing objects if necessary, so that
other parts of Tabbycat (e.g., standings) don't have to recalculate them.

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
   list. It is assumed that this is sufficient to prevent it from calling
   methods specific to classes inheriting `ScoreMixin` (in scoresheet.py).
"""

import logging
from functools import wraps
from itertools import product
from statistics import mean
from typing import TYPE_CHECKING, Union

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from draw.types import DebateSide

from .result_info import DebateResultInfo
from .scoresheet import (HighPointWinsRequiredScoresheet, LowPointWinsAllowedScoresheet, PolyEliminationScoresheet,
    PolyNoWinScoresheet, PolyScoresheet, ResultOnlyScoresheet, TiedPointWinsAllowedScoresheet)
from .utils import side_and_position_names

if TYPE_CHECKING:
    from tournaments.models import Tournament
    from participants.models import Adjudicator

    from .models import SpeakerScore, SpeakerScoreByAdj

logger = logging.getLogger(__name__)


class ResultError(RuntimeError):
    pass


def get_result_class(ballotsub, round=None, tournament=None, overwrite_forfeit=False):
    if round is None:
        round = ballotsub.round
    if tournament is None:
        tournament = round.tournament

    teams_in_debate = tournament.pref('teams_in_debate')
    ballots_per_debate = round.ballots_per_debate
    scores_in_debate = tournament.pref('speakers_in_ballots')

    forfeit = ballotsub.forfeit and not overwrite_forfeit
    if ballots_per_debate == 'per-debate' or ballotsub.single_adj or forfeit:
        if ((teams_in_debate > 2 or scores_in_debate == 'prelim') and round.is_break_round) or scores_in_debate == 'never' or forfeit:
            return ConsensusDebateResult
        return ConsensusDebateResultWithScores
    elif ballots_per_debate == 'per-adj' and (teams_in_debate == 2 or tournament.pref('margin_includes_dissenters')):
        if scores_in_debate == 'prelim' and round.is_break_round or scores_in_debate == 'never':
            return DebateResultByAdjudicator
        return DebateResultByAdjudicatorWithScores
    else:
        raise ValueError("Invalid combination for 'ballots_per_debate' and 'teams_in_debate' preferences: %s, %s" %
                (ballots_per_debate, teams_in_debate))


def get_class_name(ballotsub, round, tournament=None, overwrite_forfeit=False):
    return get_result_class(ballotsub, round, tournament, overwrite_forfeit).__name__


def is_integer_step(tournament: 'Tournament', ss: Union['SpeakerScore', 'SpeakerScoreByAdj']) -> bool:
    return (
        ss.position > tournament.pref('substantive_speakers') and tournament.pref('reply_score_step') == int(tournament.pref('reply_score_step'))
    ) or (ss.position <= tournament.pref('substantive_speakers') and tournament.pref('score_step') == int(tournament.pref('score_step')))


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
    r = kwargs.pop('round', ballotsub.debate.round)
    tournament = kwargs.pop('tournament', r.tournament)
    result_class = get_result_class(ballotsub, r, tournament)
    if result_class.uses_speakers and 'criteria' not in kwargs:
        kwargs['criteria'] = tournament.scorecriterion_set.all()
    return result_class(ballotsub, *args, **kwargs)


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

    Subclasses should implement a `teamscore_field_<fieldname>` method for each
    field of TeamScore that is relevant to them, for example,
    `teamscore_field_win(side)` or `teamscore_field_margin(side)`. These methods
    take one argument, a side string, e.g. `DebateSide.AFF` or `DebateSide.OG`, and return the
    value that should be saved to that field. When saving TeamScore objects to
    the database, the base class calls these methods to get the value it should
    save to that field. If the method does not exist, it does not write to that
    field, which normally means that the field will be left as null.
    """

    teamscore_fields = ['points', 'win', 'margin', 'score', 'votes_given', 'votes_possible', 'has_ghost']

    is_voting = False
    uses_declared_winners = True
    uses_speakers = False

    def __init__(self, ballotsub, load=True, **kwargs):
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

        if 'sides' in kwargs:
            self.sides = kwargs['sides']
        elif self.tournament.pref('margin_includes_dissenters') and self.tournament.pref('teams_in_debate') != 2:
            self.sides = list(range(1+max(*[dt.side for dt in self.debate.debateteams])))
        else:
            self.sides = self.tournament.sides

        # Needed here (not in ScoresMixin) as is called by `.scoresheet_class`
        self.winners_declared = self.tournament.pref('winners_in_ballots')

        if load:
            if self.ballotsub.id is None:
                self.empty_load()
            else:
                self.full_load()

    def __repr__(self):
        return "<{classname} at {id:#x} for {bsub!s}>".format(
            classname=self.__class__.__name__, id=id(self), bsub=self.ballotsub)

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    @property
    def scoresheet_class(self):
        return ResultOnlyScoresheet

    def full_load(self):
        self.init_blank_buffer()
        self.full_load_from_db()
        self.assert_loaded()

    def empty_load(self):
        self.init_blank_buffer()
        self.load_from_db()

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
        assert set(self.debateteams) == {-1} or set(self.debateteams) == set(self.sides)

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

        return not any(self.debateteams[side] is None for side in self.sides)

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

    def full_load_from_db(self):
        """Populates the buffer from the database. Subclasses should extend this
        method as necessary."""
        self.load_from_db()
        self.load_scoresheets()

    def load_from_db(self):
        self.load_debateteams()

    def load_debateteams(self):
        if not self.debate.sides_confirmed:
            return  # don't load if sides aren't confirmed

        d_teams = self.debate.debateteams
        if set(dt.side for dt in d_teams) != set(self.sides):
            raise ResultError("Debate has invalid sides.")

        for dt in d_teams:
            self.debateteams[dt.side] = dt

    def load_scoresheets(self, **kwargs):
        pass

    def populate_from_merge(self, *results):
        pass

    def save(self):
        """Saves to the database.
        Raises ResultError if the ballot set is incomplete or invalid."""

        if not self.is_valid():
            raise ResultError("Tried to save an invalid result.")

        for side in self.sides:
            dt = self.debateteams[side]

            self.ballotsub.teamscore_set.update_or_create(debate_team=dt,
                    defaults=self.get_defaults_fields('teamscore', side))

    def get_defaults_fields(self, model, *args):
        """Collects fields defined in subclasses"""
        fields = {}
        model_fields = getattr(self, '%s_fields' % model, None)
        if model_fields is None:
            raise ResultError("Unrecognized model: %s" % model)
        for field in model_fields:
            get_field = getattr(self, '%s_field_%s' % (model, field), None)
            if get_field is not None:
                fields[field] = get_field(*args)
        return fields

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

    def winning_side(self):
        raise NotImplementedError

    def winning_dt(self):
        raise NotImplementedError

    def winning_team(self):
        raise NotImplementedError

    def losing_dt(self):
        raise NotImplementedError

    # --------------------------------------------------------------------------
    # Other common functionality (helper functions)
    # --------------------------------------------------------------------------

    def side_as_dicts(self, sheet, side, side_name):
        return {
            "side": side_name,
            "team": self.debateteams[side].team,
        }

    def speakers_as_dicts(self, sheet, side_dict, side, pos_names):
        pass

    def sheet_as_dicts(self, sheet):
        """Returns a list of dicts, each being a team in the debate. Used by
        subclasses' `as_dicts()` methods."""
        teams = []
        for side, (side_name, pos_names) in zip(self.sides, side_and_position_names(self.tournament)):
            side_dict = self.side_as_dicts(sheet, side, side_name)

            # Colour result according to outcome of debate
            if hasattr(sheet, 'rank') and len(self.sides) == 4:
                rank = sheet.rank(side)
                side_dict["rank"] = rank
                side_dict["win_style"] = ["success", "info", "warning", "danger"][rank-1]
            elif hasattr(sheet, 'winners'):
                side_dict["win"] = side in sheet.winners()
                side_dict["win_style"] = "success" if side in sheet.winners() else "danger"

            self.speakers_as_dicts(sheet, side_dict, side, pos_names)

            teams.append(side_dict)
        return teams

    def get_result_info(self):
        return DebateResultInfo(self)


class DebateResultByAdjudicator(BaseDebateResult):
    """Base class for voting ballots.

    Voting ballots have a DebateResult with one scoresheet per voting adjudicator.
    This also provides access to the TeamScoreByAdj table.

    This mixin presupposes the use of two-team scoresheets, as it would be impossible
    to have a voting BP result (Arrow's impossibility theorem)"""

    teamscorebyadj_fields = ['win', 'margin', 'score']

    is_voting = True

    def __init__(self, ballotsub, load=True, **kwargs):
        super().__init__(ballotsub, load=load, **kwargs)
        self._decision_calculated = False

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        super().init_blank_buffer()
        self.debateadjs = {}
        self.scoresheets = {}

    def load_from_db(self):
        super().load_from_db()
        self.load_debateadjs()

    def assert_loaded(self):
        super().assert_loaded()
        assert set(self.debate.adjudicators.voting()) == set(self.scoresheets)
        assert set(self.debateadjs) == set(self.scoresheets)

    def is_complete(self):
        return super().is_complete() and self.debate.adjudicators.has_chair and all(sheet.is_complete() for sheet in self.scoresheets.values())

    def is_valid(self):
        return super().is_valid() and all(sheet.is_valid() for sheet in self.scoresheets.values())

    def identical(self, other):
        if not super().identical(other):
            return False
        if not hasattr(other, 'scoresheets') or set(self.scoresheets.keys()) != set(other.scoresheets.keys()):
            return False
        for adj, other_sheet in other.scoresheets.items():
            if not self.scoresheets[adj].identical(other_sheet):
                return False
        return True

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_debateadjs(self):
        self.debateadjs_query = self.debate.debateadjudicator_set.exclude(
            type=DebateAdjudicator.TYPE_TRAINEE).select_related('adjudicator', 'adjudicator__tournament')
        self.debateadjs = {da.adjudicator: da for da in self.debateadjs_query}
        self.scoresheets = {adj: self.scoresheet_class(
            sides=self.sides,
            positions=getattr(self, 'positions', None),
            criteria=getattr(self, 'criteria', [])) for adj in self.debateadjs.keys()
        }

    def load_scoresheets(self):
        if not self.scoresheet_class.uses_declared_winners:
            return  # No need to add winners when already determined through scores

        teamscorebyadjs = self.ballotsub.teamscorebyadj_set.filter(
            debate_adjudicator__in=self.debateadjs_query,
            win=True,
        ).select_related('debate_adjudicator__adjudicator', 'debate_team')

        for tsba in teamscorebyadjs:
            self.add_winner(tsba.debate_adjudicator.adjudicator, tsba.debate_team.side)

    def populate_from_merge(self, *results) -> list[ResultError]:
        errors = []
        for result in results:
            adj = result.ballotsub.participant_submitter.adjudicator
            errors.extend(self.merge_speaker_result(result, adj))
            if self.scoresheet_class.uses_declared_winners:
                self.set_winners(adj, result.scoresheet.winners())

        for error in errors:
            key, side, pos = error.args[1:]

            if key == 'ghost':
                self.set_ghost(side, pos, False)

            if key == 'speaker':
                self.set_speaker(side, pos, None)

        return errors

    def merge_speaker_result(self, result, adj) -> list[ResultError]:
        return []

    def save(self):
        super().save()

        for adj, sheet in self.scoresheets.items():
            da = self.debateadjs[adj]
            for side in self.sides:
                dt = self.debateteams[side]
                self.ballotsub.teamscorebyadj_set.update_or_create(
                    debate_team=dt, debate_adjudicator=da,
                    defaults=self.get_defaults_fields('teamscorebyadj', adj, side))

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def get_winner(self, adjudicator):
        return next(iter(self.scoresheets[adjudicator].winners()), None)

    def add_winner(self, adjudicator, winner):
        self.scoresheets[adjudicator].add_declared_winner(winner)

    def set_winners(self, adjudicator, winners):
        self.scoresheets[adjudicator].set_declared_winners(winners)

    # --------------------------------------------------------------------------
    # Decision calculation
    # --------------------------------------------------------------------------

    def _requires_decision(default): # noqa: N805
        """Decorator for fields that may require a decision to be reached before accessing.
        It will provide a default (the parameter to itself) if a decision can't be reached
        (i.e. is incomplete) and will get the decision if not loaded.

        A decision is the collation of the various scoresheets by each voting adjudicator
        to form a final result."""
        def wrap(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                if not self.is_complete() or len(self.sides) > 2:
                    return default
                if not self._decision_calculated:
                    self._calculate_decision()
                return func(self, *args, **kwargs)
            return wrapped
        return wrap

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

        self._adjs_by_side = {side: set() for side in self.sides} # group adjs by vote
        for adj, sheet in self.scoresheets.items():
            if len(sheet.winners()) == 0:  # should never happen
                raise ResultError("The scoresheet for %s does not have a winner." % adj.name)
            winner = self.get_winner(adj)
            self._adjs_by_side[winner].add(adj)

        votes_aff = len(self._adjs_by_side[DebateSide.AFF])
        votes_neg = len(self._adjs_by_side[DebateSide.NEG])

        if votes_aff > votes_neg:
            self._winner = DebateSide.AFF
        elif votes_neg > votes_aff:
            self._winner = DebateSide.NEG
        else:
            logger.warning("Adjudicators split %d-%d in debate %s, awarding by chair casting vote.",
                           votes_aff, votes_neg, self.debate)
            self._winner = self.get_winner(self.debate.adjudicators.chair)

        self._decision_calculated = True

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
    def winning_dt(self):
        return self.debateteams[self._winner]

    @_requires_decision(None)
    def winning_team(self):
        return self.winning_dt().team

    @_requires_decision(None)
    def losing_dt(self):
        return [dt for s, dt in self.debateteams.items() if s != self._winner][0]

    # --------------------------------------------------------------------------
    # Model fields
    # --------------------------------------------------------------------------

    @_requires_decision(None)
    def teamscore_field_points(self, side):
        return int(side == self._winner)

    @_requires_decision(None)
    def teamscore_field_win(self, side):
        return side == self._winner

    @_requires_decision(None)
    def teamscore_field_votes_given(self, side):
        return len(self._adjs_by_side[side])

    def teamscore_field_votes_possible(self, side):
        return len(self.scoresheets)

    def teamscore_field_has_ghost(self, side):
        return False

    def teamscorebyadj_field_win(self, adj, side):
        return side in self.scoresheets[adj].winners()

    def teamscorebyadj_field_score(self, adj, side):
        return None  # Placeholder for subclasses

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

        if not self._decision_calculated and len(self.sides) == 2:
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
                "teams": self.sheet_as_dicts(self.scoresheets[adj]),
            }
            yield sheet_dict


class DebateResultWithScoresMixin:
    """Mixin to provide methods to interact with SpeakerScore."""

    speakerscore_fields = ['score', 'speaker', 'ghost', 'rank']
    speakercriterionscore_fields = ['score']

    uses_declared_winners = False
    uses_speakers = True

    def __init__(self, ballotsub, load=True, criteria=[], **kwargs):
        super().__init__(ballotsub, load=False, **kwargs)

        self.positions = self.tournament.positions
        self.criteria = criteria or []

        if load:
            if self.ballotsub.id is None:
                self.empty_load()
            else:
                self.full_load()

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    @property
    def scoresheet_class(self):
        if self.tournament.pref('teams_in_debate') != 2:
            if self.tournament.pref('margin_includes_dissenters'):
                return PolyNoWinScoresheet
            return PolyScoresheet
        return {
            'none': HighPointWinsRequiredScoresheet,
            'high-points': HighPointWinsRequiredScoresheet,
            'tied-points': TiedPointWinsAllowedScoresheet,
            'low-points': LowPointWinsAllowedScoresheet,
        }[self.winners_declared]

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
        return super().is_complete() and not any(self.speakers[s][p] is None for s in self.sides for p in self.positions)

    def identical(self, other):
        if not super().identical(other):
            return False
        if self.speakers != other.speakers:
            return False
        if self.ghosts != other.ghosts:
            return False
        return True

    def merge_speaker_order(self, result: BaseDebateResult) -> list[ResultError]:
        errors = []
        for side, pos in product(self.sides, self.positions):
            cur_speaker = self.get_speaker(side, pos)
            if cur_speaker is None:
                self.set_speaker(side, pos, result.get_speaker(side, pos))
            elif result.get_speaker(side, pos) != cur_speaker:
                errors.append(ResultError("Inconsistent speaker order", "speaker", side, pos))

            if not self.get_ghost(side, pos) and result.get_ghost(side, pos):
                self.set_ghost(side, pos, result.get_ghost(side, pos))
            elif self.get_ghost(side, pos) and not result.get_ghost(side, pos):
                errors.append(ResultError("Inconsistent ghost order", "ghost", side, pos))

        return errors

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def full_load_from_db(self):
        super().full_load_from_db()
        self.load_speakers()

    def load_speakers(self):
        """Loads team and speaker identities from the database into the buffer."""

        if not self.debate.sides_confirmed:
            return  # don't load if sides aren't confirmed

        speakerscores = self.ballotsub.speakerscore_set.filter(
            debate_team__side__in=self.sides,
            position__in=self.positions,
        ).select_related('speaker', 'speaker__team__tournament', 'debate_team')

        for ss in speakerscores:
            self.speakers[ss.debate_team.side][ss.position] = ss.speaker
            self.ghosts[ss.debate_team.side][ss.position] = ss.ghost

    def save(self):
        super().save()

        for side in self.sides:
            dt = self.debateteams[side]
            for pos in self.positions:
                speaker_score, _ = self.ballotsub.speakerscore_set.update_or_create(debate_team=dt,
                    position=pos, defaults=self.get_defaults_fields('speakerscore', side, pos))
                for criterion in self.criteria:
                    speaker_score.speakercriterionscore_set.update_or_create(
                        criterion=criterion, defaults=self.get_defaults_fields('speakercriterionscore', side, pos, criterion))

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def get_speaker(self, side, position):
        return self.speakers[side].get(position)

    def set_speaker(self, side, position, speaker):
        if self.debateteams[side] is None:
            raise TypeError("Set sides using self.set_sides() before setting speakers")
        team = self.debateteams[side].team
        if speaker is not None and speaker not in team.speakers:
            logger.error("Speaker %s isn't in team %s", speaker.name, team.short_name)
            return
        self.speakers[side][position] = speaker

    def get_ghost(self, side: str, position: int) -> bool:
        return self.ghosts[side].get(position, False)

    def set_ghost(self, side, position, is_ghost):
        self.ghosts[side][position] = is_ghost

    # --------------------------------------------------------------------------
    # Model fields
    # --------------------------------------------------------------------------

    speakerscore_field_speaker = get_speaker
    speakerscore_field_ghost = get_ghost

    def teamscore_field_margin(self, side):
        return self.calculate_full_margin(side)

    def teamscore_field_has_ghost(self, side):
        return any(self.ghosts[side].values())

    # --------------------------------------------------------------------------
    # Other common functionality (helper functions)
    # --------------------------------------------------------------------------

    def calculate_full_margin(self, side):
        if len(self.sides) > 2:
            return None

        aff_total = self.teamscore_field_score(DebateSide.AFF)
        neg_total = self.teamscore_field_score(DebateSide.NEG)
        return self.calculate_margin(side, aff_total, neg_total)

    def calculate_margin(self, side, aff_total, neg_total):
        if aff_total is None or neg_total is None:
            return None

        if side == DebateSide.AFF:
            return aff_total - neg_total
        elif side == DebateSide.NEG:
            return neg_total - aff_total
        else:
            raise ValueError("side must be DebateSide.AFF or DebateSide.NEG")

    # --------------------------------------------------------------------------
    # Method for UI display
    # --------------------------------------------------------------------------

    def side_as_dicts(self, sheet, side, side_name):
        return {
            **super().side_as_dicts(sheet, side, side_name),
            "total": sheet.get_total(side),
            "speakers": [],
        }

    def speakers_as_dicts(self, sheet, side_dict, side, pos_names):
        for pos, pos_name in zip(self.positions, pos_names):
            side_dict["speakers"].append({
                "pos": pos,
                "name": pos_name,
                "speaker": self.get_speaker(side, pos),
                "score": sheet.get_score(side, pos),
                "rank": sheet.get_speaker_rank(side, pos),
            })


class ConsensusDebateResult(BaseDebateResult):
    """Consensus debate result without scores"""

    def init_blank_buffer(self):
        super().init_blank_buffer()
        self.scoresheet = self.scoresheet_class(sides=self.sides, positions=getattr(self, 'positions', None), criteria=getattr(self, 'criteria', []))
        if self.scoresheet_class is PolyEliminationScoresheet and self.debate.round.is_last:
            self.scoresheet.number_winners = 1

    def is_complete(self):
        return super().is_complete() and self.scoresheet.is_complete()

    def is_valid(self):
        return super().is_valid() and self.scoresheet.is_valid()

    @property
    def scoresheet_class(self):
        if len(self.sides) == 2:
            return super().scoresheet_class
        else:
            return PolyEliminationScoresheet

    def load_scoresheets(self):
        super().load_scoresheets()

        if not self.scoresheet.uses_declared_winners:
            return

        winners = self.ballotsub.teamscore_set.filter(win=True).select_related('debate_team').values_list('debate_team__side', flat=True)
        self.set_winners(set(winners))

    def get_winner(self):
        return self.scoresheet.winners()

    def add_winner(self, winner):
        self.scoresheet.add_declared_winner(winner)

    def set_winners(self, winners):
        self.scoresheet.set_declared_winners(winners)

    def winning_side(self):
        if len(self.get_winner()) == 0:
            return None
        assert len(self.get_winner()) == 1, "Should not be called with BP"
        return next(iter(self.get_winner()))

    def winning_dt(self):
        return self.debateteams.get(self.winning_side())

    def winning_team(self):
        return self.winning_dt().team

    def losing_dt(self):
        return [dt for s, dt in self.debateteams.items() if s != self.winning_side()][0]

    # --------------------------------------------------------------------------
    # BP Elimination-specific methods
    # --------------------------------------------------------------------------

    @property
    def is_elimination(self):
        return not hasattr(self.scoresheet, 'ranked_sides')

    def advancing_dt(self):
        return [dt for s, dt in self.debateteams.items() if s in self.get_winner()]

    def advancing_teams(self):
        return [dt.team for dt in self.advancing_dt()]

    def eliminated_dt(self):
        return [dt for s, dt in self.debateteams.items() if s not in self.get_winner()]

    def get_ranked_dt(self):
        return [self.debateteams[s] for s in self.scoresheet.ranked_sides()]

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def identical(self, other):
        return super().identical(other) and hasattr(other, 'scoresheet') and self.scoresheet.identical(other.scoresheet)

    def populate_from_merge(self, *results) -> list[ResultError]:
        errors = []
        for result in results:
            errors.extend(self.merge_speaker_result(result))
            if self.scoresheet_class.uses_declared_winners:
                if self.get_winner() is None or len(self.get_winner()) == 0:
                    self.set_winners(result.scoresheet.winners())
                elif self.get_winner() != result.scoresheet.winners():
                    errors.append(ResultError("Winners are not identical", "winners", result.scoresheet.winners(), None))

        for error in errors:
            key, side, pos = error.args[1:]

            if key == 'winners':
                self.set_winners(set())

            # Clear ghosts for speaker order problems too
            if key == 'ghost':
                self.set_ghost(side, pos, False)

            if key == 'speaker':
                self.set_speaker(side, pos, None)

            if key == 'scores':
                self.set_score(side, pos, None)

            if key == 'speaker_ranks':
                self.set_speaker_rank(side, pos, None)

        return errors

    def merge_speaker_result(self, result) -> list[ResultError]:
        return []

    # --------------------------------------------------------------------------
    # Team score fields
    # --------------------------------------------------------------------------

    def teamscore_field_points(self, side):
        if not hasattr(self.scoresheet, 'rank'):
            return None
        return len(self.sides) - self.scoresheet.rank(side)

    def teamscore_field_win(self, side):
        return side in self.scoresheet.winners()

    def teamscore_field_score(self, side):
        return None  # Placeholder for subclasses with scores

    def teamscore_field_has_ghost(self, side):
        return False

    def as_dicts(self):
        yield {'teams': self.sheet_as_dicts(self.scoresheet)}


class ConsensusDebateResultWithScores(DebateResultWithScoresMixin, ConsensusDebateResult):
    """Consensus debate result including speaker scores"""

    @property
    def scoresheet_class(self):
        if len(self.sides) == 2:
            return super().scoresheet_class
        else:
            return PolyScoresheet

    def load_scoresheets(self):
        super().load_scoresheets()

        speakerscores = self.ballotsub.speakerscore_set.filter(
            debate_team__side__in=self.sides,
            position__in=self.positions,
        ).select_related('debate_team').prefetch_related('speakercriterionscore_set__criterion')

        for ss in speakerscores:
            if len(ss.speakercriterionscore_set.all()) > 0:
                for criterion_score in ss.speakercriterionscore_set.all():
                    integer_step = criterion_score.criterion.step
                    cs = int(criterion_score.score) if integer_step and int(criterion_score.score) == criterion_score.score else criterion_score.score
                    self.set_criterion_score(ss.debate_team.side, ss.position, criterion_score.criterion, cs)
            else:
                integer_step = is_integer_step(self.tournament, ss)

                score = int(ss.score) if integer_step and int(ss.score) == ss.score else ss.score
                self.set_score(ss.debate_team.side, ss.position, score)
            self.set_speaker_rank(ss.debate_team.side, ss.position, ss.rank)

    def set_score(self, side, position, score):
        self.scoresheet.set_score(side, position, score)

    def merge_speaker_result(self, result: BaseDebateResult) -> list[ResultError]:
        errors = self.merge_speaker_order(result)
        for side, pos in product(self.sides, self.positions):
            for criterion in self.criteria:
                if self.get_criterion_score(side, pos, criterion) is None:
                    self.set_criterion_score(side, pos, criterion, result.get_criterion_score(side, pos, criterion))
                elif self.get_criterion_score(side, pos, criterion) != result.get_criterion_score(side, pos, criterion):
                    errors.append(ResultError('Criterion scores are not identical', 'criterion', side, pos, criterion))

            if self.get_score(side, pos) is None:
                self.set_score(side, pos, result.get_score(side, pos))
            elif self.get_score(side, pos) != result.get_score(side, pos):
                errors.append(ResultError('Scores are not identical', 'scores', side, pos))

            if self.get_speaker_rank(side, pos) is None:
                self.set_speaker_rank(side, pos, result.get_speaker_rank(side, pos))
            elif self.get_speaker_rank(side, pos) != result.get_speaker_rank(side, pos):
                errors.append(ResultError('Speech ranks are not identical', 'speaker_ranks', side, pos))
        return errors

    def get_speaker_rank(self, side: str, position: int) -> int:
        return self.scoresheet.get_speaker_rank(side, position)

    def set_speaker_rank(self, side, position, rank):
        self.scoresheet.set_speaker_rank(side, position, rank)

    def get_criterion_score(self, side, pos, criterion):
        return self.scoresheet.get_criterion_score(side, pos, criterion)

    def set_criterion_score(self, side, pos, criterion, score):
        self.scoresheet.set_criterion_score(side, pos, criterion, score)

    # --------------------------------------------------------------------------
    # Model fields
    # --------------------------------------------------------------------------

    def speakerscore_field_score(self, side, position):
        return self.scoresheet.get_score(side, position)

    get_score = speakerscore_field_score
    speakerscore_field_rank = get_speaker_rank
    speakercriterionscore_field_score = get_criterion_score

    def teamscore_field_score(self, side):
        if self.tournament.pref('teamscore_includes_ghosts'):
            return self.scoresheet.get_total(side)
        return sum(self.get_score(side, pos) for pos in self.positions if not self.get_ghost(side, pos))

    def teamscore_field_has_ghost(self, side):
        return any(self.ghosts[side].values())


class DebateResultByAdjudicatorWithScores(DebateResultWithScoresMixin, DebateResultByAdjudicator):
    """Gives access to SpeakerScoreByAdj and scores of TeamScoreByAdj"""

    speakerscorebyadj_fields = ['score']
    speakercriterionscorebyadj_fields = ['score']

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def load_scoresheets(self):
        super().load_scoresheets()

        speakerscorebyadjs = self.ballotsub.speakerscorebyadj_set.filter(
            debate_adjudicator__in=self.debateadjs_query,
            debate_team__side__in=self.sides,
            position__in=self.positions,
        ).select_related('debate_adjudicator__adjudicator', 'debate_adjudicator__adjudicator__institution',
                         'debate_team').prefetch_related('speakercriterionscorebyadj_set__criterion')

        for ssba in speakerscorebyadjs:
            if len(ssba.speakercriterionscorebyadj_set.all()) > 0:
                for criterion_score in ssba.speakercriterionscorebyadj_set.all():
                    integer_step = criterion_score.criterion.step == int(criterion_score.criterion.step)
                    cs = int(criterion_score.score) if integer_step and int(criterion_score.score) == criterion_score.score else criterion_score.score
                    self.set_criterion_score(ssba.debate_adjudicator.adjudicator, ssba.debate_team.side, ssba.position, criterion_score.criterion, cs)
            else:
                integer_step = is_integer_step(self.tournament, ssba)
                score = int(ssba.score) if integer_step and int(ssba.score) == ssba.score else ssba.score
                self.set_score(ssba.debate_adjudicator.adjudicator,
                               ssba.debate_team.side, ssba.position, score)

    def merge_speaker_result(self, result: BaseDebateResult, adj: 'Adjudicator') -> list[ResultError]:
        errors = self.merge_speaker_order(result)
        for side, pos in product(self.sides, self.positions):
            if self.criteria:
                for criterion in self.criteria:
                    self.set_criterion_score(adj, side, pos, criterion, result.get_criterion_score(side, pos, criterion))
            else:
                self.set_score(adj, side, pos, result.get_score(side, pos))
        return errors

    def save(self):
        super().save()

        for adj, sheet in self.scoresheets.items():
            da = self.debateadjs[adj]
            for side in self.sides:
                dt = self.debateteams[side]
                for pos in self.positions:
                    speaker_score_by_adj, _ = self.ballotsub.speakerscorebyadj_set.update_or_create(
                        debate_team=dt, debate_adjudicator=da, position=pos,
                        defaults=self.get_defaults_fields('speakerscorebyadj', adj, side, pos))
                    for criterion in self.criteria:
                        speaker_score_by_adj.speakercriterionscorebyadj_set.update_or_create(
                            criterion=criterion, defaults=self.get_defaults_fields('speakercriterionscorebyadj', adj, side, pos, criterion))

    def set_score(self, adjudicator, side, position, score):
        try:
            self.scoresheets[adjudicator].set_score(side, position, score)
        except KeyError:
            logger.exception("Tried to set score by adjudicator %s, but this adjudicator "
                "doesn't have a scoresheet.", adjudicator)
            return

    def get_speaker_rank(self, adjudicator: 'Adjudicator', side: str, position: int) -> int:
        return self.scoresheets[adjudicator].get_speaker_rank(side, position)

    # --------------------------------------------------------------------------
    # Model fields
    # --------------------------------------------------------------------------

    def teamscorebyadj_field_margin(self, adj, side):
        if len(self.sides) > 2:
            return None
        return self.calculate_margin_by_adj(adj, side)

    def teamscorebyadj_field_score(self, adj, side):
        return self.scoresheets[adj].get_total(side)

    def _teamscore_score_component(self, adj, side):
        if self.tournament.pref('teamscore_includes_ghosts'):
            return self.scoresheets[adj].get_total(side)
        return sum(self.get_score(adj, side, pos) for pos in self.positions if not self.get_ghost(side, pos))

    def teamscore_field_score(self, side):
        # Should be decision-decorated
        if not self.is_complete():
            return None
        if not self._decision_calculated and len(self.sides) == 2:
            self._calculate_decision()
        return mean(self._teamscore_score_component(adj, side) for adj in self.relevant_adjudicators())

    def teamscore_field_has_ghost(self, side):
        return any(self.ghosts[side].values())

    def speakerscorebyadj_field_score(self, adjudicator, side, position):
        return self.scoresheets[adjudicator].get_score(side, position)
    get_score = speakerscorebyadj_field_score

    def speakerscore_field_score(self, side, position):
        # Should be decision-decorated
        if not self.is_complete():
            return None
        if not self._decision_calculated and len(self.sides) == 2:
            self._calculate_decision()
        return mean(self.scoresheets[adj].get_score(side, position) for adj in self.relevant_adjudicators())

    def speakercriterionscore_field_score(self, side, pos, criterion):
        # Should be decision-decorated
        if not self.is_complete():
            return None
        if not self._decision_calculated:
            self._calculate_decision()
        return mean(self.scoresheets[adj].get_criterion_score(side, pos, criterion) for adj in self.relevant_adjudicators())

    def speakercriterionscorebyadj_field_score(self, adjudicator, side, pos, criterion):
        return self.scoresheets[adjudicator].get_criterion_score(side, pos, criterion)
    get_criterion_score = speakercriterionscorebyadj_field_score

    def set_criterion_score(self, adj, side, pos, criterion, score):
        self.scoresheets[adj].set_criterion_score(side, pos, criterion, score)

    # --------------------------------------------------------------------------
    # Other common functionality (helper functions)
    # --------------------------------------------------------------------------

    def calculate_margin_by_adj(self, adj, side):
        # The purpose of this function is to prevent code duplication between
        # other functions that require a teamscore_field_margin() method.
        aff_total = self.teamscorebyadj_field_score(adj, DebateSide.AFF)
        neg_total = self.teamscorebyadj_field_score(adj, DebateSide.NEG)
        self.calculate_margin(side, aff_total, neg_total)
