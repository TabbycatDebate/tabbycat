"""Debate result classes.

Debate result classes aggregate scoresheets to produce results for an entire
debate, and interact with the database with respect to models recording scores
given in the debate. They do not deal with metadata (like motions), only scores
and results. These classes track team and speaker identities, so that they can
save them to the database.

These classes never read TeamScore objects. When loading existing results, they
rely on scoresheets, which in turn rely on SpeakerScoreByAdj (for voting
decisions) or SpeakerScore (for consensus decisions) to calculate results.
However, these classes do *save* TeamScore objects, overwriting existing objects
if necessary, so that other parts of Tabbycat (e.g., standings) don't have to
recalculate them.

A debate result class is associated with a ballot submission, not a debate. This
allows multiple versions of the result to be retained for a single debate, which
helps avoid data loss when multiple results are (presumably erroneously)
submitted.

Notes on terminology:
 - "Position" in this file always means speaker position as a number. Replies
   take the number one greater than the last substantive speaker.
 - "Side" means the team position, e.g. affirmative (in two-team) or opening
   government (in BP). By convention, these are represented as strings.
 - "Team" refers to the actual team (e.g. Auckland 1).

A few notes on error checking:
 - In general, the validity of 'side' and 'position' arguments aren't checked.
   It is the responsibility of the caller to comply with valid values.
 - When loading from the database, it filters for `self.side_db_values` and
   `self.positions` to prevent queries from returning instances with invalid
   side and position arguments.
 - When scores aren't being used, `self.positions` should be set to an empty
   list. It it assumed that this is sufficient to prevent it from calling
   methods specific to classes inheriting `ScoreMixin` (in scoresheet.py).
"""

import logging
from functools import wraps
from statistics import mean

from draw.models import DebateTeam
from adjallocation.models import DebateAdjudicator

from .scoresheet import SCORESHEET_CLASSES

logger = logging.getLogger(__name__)


class BaseDebateResult:
    """Base class for debate results.

    The base class implements management of side allocations, speaker identities
    and ghosts. Other functions are left to subclasses.

    The loading process calls three functions in turn:
      - First, it calls `self.init_blank_buffer()`, which should initialize
        "blank" buffers for all information that it stores to eventually be
        saved to the database.
      - Then, it calls `self.load_from_db()`, which reads the database and
        populates the buffers accordingly.
      - Finally, it calls, `self.assert_loaded()`, which verifies that the
        buffers are of the correct form, and raises an `AssertionError` if they
        are not. (It does not check for completeness, only form.)

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

    # These are exhaustive lists/dicts of all possible values that these are
    # allowed to take, in any format.
    SIDE_KEY_MAP = {
        DebateTeam.POSITION_AFFIRMATIVE: 'aff',
        DebateTeam.POSITION_NEGATIVE: 'neg',
        # exclude POSITION_UNALLOCATED: you can't assign scores until sides are allocated
    }
    SIDE_KEY_MAP_REVERSE = {v: k for k, v in SIDE_KEY_MAP.items()}
    TEAMSCORE_FIELDS = ['points', 'win', 'margin', 'score', 'votes_given', 'votes_possible']

    def __init__(self, ballotsub, load=True):
        """Constructor.
        `ballotsub` must be a BallotSubmission.

        If `load` is False, the constructor will not load any data from the
        database (at all). It is then the responsibility of the caller to do so;
        the instance will crash otherwise, as the relevant attributes will not
        be created. (For example, in prefetch.py, `populate_ballotsets()` uses
        this to load BallotSets in bulk.) Callers can use `.init_blank_buffer()`
        to initialize the correct buffers and `.assert_loaded()` to check that
        data was loaded correctly.
        """

        self.ballotsub = ballotsub
        self.debate = ballotsub.debate
        self.tournament = self.debate.round.tournament

        # side are to be extended to BP later
        self.sides = ['aff', 'neg']
        self.side_db_values = [self.SIDE_KEY_MAP_REVERSE[side] for side in self.sides]

        if load:
            self.positions = self.tournament.POSITIONS

            self.init_blank_buffer()
            self.load_from_db()
            self.assert_loaded()

    def __repr__(self):
        return "<{classname} at {id:#x} for {bsub!s}>".format(
            classname=self.__class__.__name__, id=id(self), bsub=self.ballotsub)

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        """Initialises the data attributes. External initialisers might find
        this helpful. The `self.sides` and `self.positions` attributes must be
        set prior to calling this function. Subclasses should extend this
        method as necessary."""

        try:
            self.debateteams = dict.fromkeys(self.sides, None)
            self.speakers = {side: dict.fromkeys(self.positions, None) for side in self.sides}
            self.ghosts = {side: dict.fromkeys(self.positions, False) for side in self.sides}

        except AttributeError:
            if not hasattr(self, 'sides') or not hasattr(self, 'positions'):
                raise AttributeError("The DebateResult instance must have sides and positions attributes before init_blank_buffer() is called.")
            else:
                raise

    def assert_loaded(self):
        """Raise an AssertionError if there is some problem with the data
        structure. External initialisers might find this helpful. Subclasses
        should extend this method as necessary."""

        assert set(self.debateteams) == set(self.sides)
        assert set(self.speakers) == set(self.sides)
        assert set(self.ghosts) == set(self.sides)
        for side in self.sides:
            assert set(self.speakers[side]) == set(self.positions)
            assert set(self.ghosts[side]) == set(self.positions)

    @property
    def is_complete(self):
        """Returns True if all elements of the results have been populated;
        False if any one is missing.  Logs (but does not raise) the exception if
        self.assert_loaded() fails.

        Subclasses should extend this method as necessary."""

        try:
            self.assert_loaded()
        except AssertionError:
            logger.exception("When checking for completeness, DebateResult.assert_loaded() failed.")

        if any(self.debateteams[side] is None for side in self.sides):
            return False
        if any(self.speakers[s][p] is None for s in self.sides for p in self.positions):
            return False

        return True

    def identical(self, other):
        """Returns True of all fields are the same as those in `other`."""
        if self.debateteams != other.debateteams:
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
        """Populates the buffer from the database. Subclasses should extend this
        method as necessary."""
        self.load_debateteams()
        self.load_speakers()

    def load_debateteams(self):
        debateteams = self.debate.debateteam_set.filter(
                position__in=self.side_db_values).select_related('team')

        for dt in debateteams:
            side = self.SIDE_KEY_MAP[dt.position]
            self.debateteams[side] = dt

    def load_speakers(self):
        """Loads team and speaker identities from the database into the buffer."""

        speakerscores = self.ballotsub.speakerscore_set.filter(
            debate_team__debate=self.debate,
            debate_team__position__in=self.side_db_values,
            position__in=self.positions,
        ).select_related('speaker')

        for ss in speakerscores:
            side = self.SIDE_KEY_MAP[ss.debate_team.position]
            self.speakers[side][ss.position] = ss.speaker
            self.ghosts[side][ss.position] = ss.ghost

    def save(self):
        """Saves to the database."""

        assert self.is_complete, "Tried to save an incomplete result"

        for side in self.sides:
            dt = self.debateteams[side]

            teamscorefields = {}
            for field in self.TEAMSCORE_FIELDS:
                get_field = getattr(self, 'teamscorefield_%s' % field, None)
                if get_field is not None:
                    teamscorefields[field] = get_field(side)
            self.ballotsub.teamscore_set.update_or_create(debate_team=dt,
                    defaults=teamscorefields)

            for pos in self.positions:
                speaker = self.speakers[side][pos]
                is_ghost = self.ghosts[side][pos]
                score = self.get_speaker_score(side, pos)
                self.ballotsub.speakerscore_set.update_or_create(debate_team=dt,
                    position=pos, defaults=dict(speaker=speaker, score=score, ghost=is_ghost))

    # --------------------------------------------------------------------------
    # Data setting and retrieval
    # --------------------------------------------------------------------------

    def set_sides(self, *teams):
        """Sets the sides, saving the sides to the database immediately.
        Arguments must be a list of Team instances, which each must relate to a
        DebateTeam instance in this debate. (Sides are saved immediately to
        enable the use of side keys to refer to teams.)"""

        debateteams_by_team = {dt.team: dt for dt in self.debateteams}
        for side, team in zip(self.sides, teams):
            debateteam = debateteams_by_team[team]
            debateteam.position = self.SIDE_KEY_MAP_REVERSE[side]
            debateteam.save()
        self.load_debateteams(self.debate.debateteam_set.select_related('team')) # refresh

    def get_speaker(self, side, position):
        return self.speakers[side].get(position)

    def set_speaker(self, side, position, speaker):
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


class VotingDebateResult(BaseDebateResult):

    def __init__(self, ballotsub, **kwargs):

        scoresheet_pref = kwargs.pop('scoresheet_pref', None)
        if scoresheet_pref is None:  # avoid cache hit if provided as kwarg
            # can't use self.tournament, it's created by the super constructor
            scoresheet_pref = ballotsub.debate.round.tournament.pref('scoresheet_type')
        self.scoresheet_class = SCORESHEET_CLASSES[scoresheet_pref]

        self._decision_calculated = False

        # super constructor performs the load
        super().__init__(ballotsub, **kwargs)

    # --------------------------------------------------------------------------
    # Management methods
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        super().init_blank_buffer()
        self.scoresheets = {}  # don't load adjudicators, it's a database hit

    def assert_loaded(self):
        super().assert_loaded()
        assert set(self.debate.adjudicators.voting()) == set(self.scoresheets)
        assert self.sides == ['aff', 'neg'], "VotingDebateResult can only be used for two-team formats."

    @property
    def is_complete(self):
        if not super().is_complete:
            return False
        if not self.debate.adjudicators.has_chair:
            return False
        if not all(sheet.is_complete for sheet in self.scoresheets.values()):
            return False
        return True

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
        debateadjs = self.debate.debateadjudicator_set.exclude(type=DebateAdjudicator.TYPE_TRAINEE)
        self.debateadjs = {da.adjudicator: da for da in debateadjs}
        self.scoresheets = {adj: self.scoresheet_class(self.positions) for adj in self.debateadjs.keys()}

        speakerscorebyadjs = self.ballotsub.speakerscorebyadj_set.filter(
            debate_adjudicator__in=debateadjs,
            debate_team__position__in=self.side_db_values,
            position__in=self.positions,
        )

        for ssba in speakerscorebyadjs:
            side = self.SIDE_KEY_MAP[ssba.debate_team.position]
            self.set_score(ssba.debate_adjudicator.adjudicator, side, ssba.position, ssba.score)

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
        return self.scoresheets[adjudicator].get_score(side, position)

    def set_score(self, adjudicator, side, position, score):
        scoresheet = self.scoresheets[adjudicator]
        scoresheet.set_score(side, position, score)

    # --------------------------------------------------------------------------
    # Calculated fields
    # --------------------------------------------------------------------------

    def _calc_decision(self):
        """Calculates the majority decision and puts the adjudicators for each
        team in self._adjs_by_side and the winning DebateTeam in self._winner.
        If the panel is evenly split, it awards the debate to the team for which
        the chair voted.

        Raises AssertionError if scores are incomplete.
        Raises ResultError there is a draw somewhere among the adjudicators.
        """

        assert self.is_complete, "Tried to calculate decision on an incomplete ballot set."

        self._adjs_by_side = {side: [] for side in self.sides} # group adjs by vote
        for adj, sheet in self.scoresheets.items():
            winner = sheet.winner()
            if winner is None:
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

    def _requires_decision(default): # flake8: noqa
        def wrap(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                if not self.is_complete:
                    return default
                if not self._decision_calculated:
                    self._calc_decision()
                return func(self, *args, **kwargs)
            return wrapped
        return wrap

    @property
    @_requires_decision([])
    def majority_adjudicators(self):
        return self._adjs_by_side[self._winner]

    @property
    def relevant_adjudicators(self):
        if self.tournament.pref('margin_includes_dissenters'):
            return self.scoresheets.keys()
        else:
            return self.majority_adjudicators

    # @property
    # @_requires_decision(None)
    # def winning_team(self):
    #     return self.debateteams[self._winner].team

    @_requires_decision(None)
    def get_speaker_score(self, side, position):
        return mean(self.scoresheets[adj].get_score(side, position) for adj in self.relevant_adjudicators)

    # --------------------------------------------------------------------------
    # Team score fields
    # --------------------------------------------------------------------------

    @_requires_decision(None)
    def teamscorefield_points(self, side):
        if side == self._winner:
            return 1
        else:
            return 0

    @_requires_decision(None)
    def teamscorefield_win(self, side):
        return side == self._winner

    @_requires_decision(None)
    def teamscorefield_score(self, side):
        return mean(self.scoresheets[adj].get_total(side) for adj in self.relevant_adjudicators)

    @_requires_decision(None)
    def teamscorefield_margin(self, side):
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

    @_requires_decision(None)
    def teamscorefield_votes_given(self, side):
        return len(self._adjs_by_side[side])

    def teamscorefield_votes_possible(self, side):
        return len(self.scoresheets)

    # CONTINUE HERE with methods for UI display
