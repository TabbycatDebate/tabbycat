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
"""

from draw.models import DebateTeam


class BaseDebateResult:
    """Base class for debate results.

    Subclasses should implement a `_get_<field>` method for each field of
    TeamScore that is relevant to them, for example, `_get_win(side)` or
    `get_margin(side)`. These methods take one argument, a side string, e.g.
    `'aff'` or `'og'`. When saving TeamScore objects to the database, the base
    class calls these methods to get the value it should save to that field. If
    the method does not exist, it does not write to that field, which normally
    means that the field will be left as null.
    """

    SIDE_KEYS = {
        DebateTeam.POSITION_AFFIRMATIVE: 'aff',
        DebateTeam.POSITION_NEGATIVE: 'neg',
    }
    SIDE_KEYS_REVERSE = {v: k for k, v in SIDE_KEYS.items()}
    TEAMSCORE_FIELDS = ['points', 'win', 'margin', 'score', 'votes_given', 'votes_possible']

    def __init__(self, ballotsub, load=True):
        """Constructor.
        `ballotsub` must be a BallotSubmission.

        If `load` is False, the constructor will not load any data from the
        database (at all). It is then the responsibility of the caller to do so;
        the instance will crash otherwise, as the relevant attributes will not
        be created. (For example, in prefetch.py, populate_ballotsets() uses
        this to load BallotSets in bulk.) Callers can use
        BallotSet.assert_load() to check that data was loaded correctly.
        """

        self.ballotsub = ballotsub
        self.debate = ballotsub.debate

        if load:
            self.SIDES = ['aff', 'neg']  # to be extended to BP later
            self.POSITIONS = self.debate.round.tournament.POSITIONS

            self.init_blank_buffer()
            self.load_debateteams()
            self.load_speakers()
            self.assert_loaded()

    def __repr__(self):
        return "<DebateResult at {id:#x for {bsub!s}>".format(id=id(self), bsub=self.ballotsub)

    # --------------------------------------------------------------------------
    # Initialisation methods (external initialisers may find these helpful)
    # --------------------------------------------------------------------------

    def init_blank_buffer(self):
        """Initialises the data attributes. External initialisers might find
        this helpful. The `self.SIDES` and `self.POSITIONS` attributes must be set
        prior to calling this function."""

        try:
            self.debateteams = dict.fromkeys(self.SIDES, None)
            self.speakers = {side: dict.fromkeys(self.POSITIONS, None) for side in self.SIDES}
            self.ghosts = {side: dict.fromkeys(self.POSITIONS, False) for side in self.SIDES}

        except AttributeError:
            if not hasattr(self, 'SIDES') or not hasattr(self, 'POSITIONS'):
                raise AttributeError("The DebateResult instance must have dts and POSITIONS attributes before init_blank_buffer() is called.")
            else:
                raise

    def assert_loaded(self):
        assert len(self.debateteams) == 2
        assert len(self.speakers) == 2
        assert len(self.ghosts) == 2
        for side in self.SIDES:
            assert side in self.debateteams
            assert side in self.speakers
            assert side in self.ghosts
            assert len(self.speakers[side]) == len(self.POSITIONS)
            assert all(pos in self.speakers[side] for pos in self.POSITIONS)
            assert len(self.ghosts[side]) == len(self.POSITIONS)
            assert all(pos in self.ghosts[side] for pos in self.POSITIONS)

    # --------------------------------------------------------------------------
    # Load and save methods
    # --------------------------------------------------------------------------

    def _side(self, debateteam):
        """Returns the side string for the given debateteam."""
        side = self.SIDE_KEYS[debateteam.position]
        if side not in self.SIDES:
            raise KeyError
        return side

    def load_debateteams(self):
        for dt in self.debate.debateteam_set.select_related('team'):
            try:
                side = self._side(dt)
            except KeyError:
                continue
            self.debateteams[side] = dt

    def load_speakers(self):
        """Loads team and speaker identities from the database into the buffer."""
        for ss in self.ballotsub.speakerscore_set.filter(debate_team__debate=self.debate,
                position__in=self.POSITIONS).select_related('speaker'):
            try:
                side = self._side(dt)
            except KeyError:
                continue
            self.speakers[side][ss.position] = ss.speaker
            self.ghosts[side][ss.position] = ss.ghost

    def save(self):
        """Saves to the database."""
        for side in self.SIDES:
            dt = self.debateteams[side]

            teamscore_fields = {}
            for field in self.TEAMSCORE_FIELDS:
                get_field = getattr(self, '_get_%s' % field, None)
                if get_field is not None:
                    teamscore_fields[field] = get_field(side)
            self.ballotsub.teamscore_set.update_or_create(debate_team=dt,
                    defaults=teamscore_fields)

            for pos in self.POSITIONS:
                speaker = self.speakers[side][pos]
                is_ghost = self.ghosts[side][pos]
                score = self._get_speaker_score(side, pos)
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
        debateteams_by_team = {dt.team: dt for dt in debateteams}
        for side, team in zip(self.SIDES, teams):
            debateteam = debateteams_by_team[team]
            debateteam.position = self.SIDE_KEYS_REVERSE[side]
            debateteam.save()
        self.load_debateteams(self.debate.debateteam_set.select_related('team')) # refresh self.dts


class VotingDebateResult(BaseDebateResult):
    pass
