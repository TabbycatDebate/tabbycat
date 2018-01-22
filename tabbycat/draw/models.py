import logging

from django.db import models
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from tournaments.utils import get_side_name

from .generator import DRAW_FLAG_DESCRIPTIONS

logger = logging.getLogger(__name__)


class DebateManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('round')


class Debate(models.Model):
    STATUS_NONE = 'N'
    STATUS_POSTPONED = 'P'
    STATUS_DRAFT = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_CHOICES = ((STATUS_NONE, _("none")),
                      (STATUS_POSTPONED, _("postponed")),
                      (STATUS_DRAFT, _("draft")),
                      (STATUS_CONFIRMED, _("confirmed")), )

    objects = DebateManager()

    round = models.ForeignKey('tournaments.Round', models.CASCADE, db_index=True,
        verbose_name=_("round"))
    venue = models.ForeignKey('venues.Venue', models.SET_NULL, blank=True, null=True,
        verbose_name=_("venue"))
    # cascade to keep draws clean in event of division deletion
    division = models.ForeignKey('divisions.Division', models.CASCADE, blank=True, null=True,
        verbose_name=_("division"))

    bracket = models.FloatField(default=0,
        verbose_name=_("bracket"))
    room_rank = models.IntegerField(default=0,
        verbose_name=_("room rank"))

    time = models.DateTimeField(blank=True, null=True,
        verbose_name=_("time"),
        help_text=_("The time/date of a debate if it is specifically scheduled"))

    # comma-separated list of strings
    flags = models.CharField(max_length=100, blank=True)

    importance = models.IntegerField(default=0, choices=[(i, i) for i in range(-2, 3)],
        verbose_name=_("importance"))
    result_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE,
        verbose_name=_("result status"))
    ballot_in = models.BooleanField(default=False,
        verbose_name=_("ballot in"))
    sides_confirmed = models.BooleanField(default=True,
        verbose_name=_("sides confirmed"),
        help_text=_("If unchecked, the sides assigned to teams in this debate are just placeholders."))

    class Meta:
        verbose_name = _("debate")
        verbose_name_plural = _("debates")

    def __str__(self):
        description = "[{}/{}/{}] ".format(self.round.tournament.slug, self.round.abbreviation, self.id)
        try:
            description += self.matchup
        except:
            logger.exception("Error rendering Debate.matchup in Debate.__str__")
            description += "<error showing teams>"
        return description

    @property
    def matchup(self):
        # This method is used by __str__, so it's not allowed to crash (ever)
        if not self.sides_confirmed:
            teams_list = ", ".join([dt.team.short_name for dt in self.debateteam_set.all()])
            # Translators: This is appended to a list of teams, e.g. "Auckland
            # 1, Vic Wellington 1 (sides not confirmed)". Mind the leading
            # space.
            return teams_list + ugettext(" (sides not confirmed)")
        try:
            # Translators: This goes between teams in a debate, e.g. "Auckland 1
            # vs Vic Wellington 1". Mind the leading and trailing spaces.
            return ugettext(" vs ").join(self.get_team(side).short_name for side in self.round.tournament.sides)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return self._teams_and_sides_display()

    def _teams_and_sides_display(self):
        return ", ".join(["%s (%s)" % (dt.team.short_name, dt.get_side_display())
                for dt in self.debateteam_set.all()])

    # --------------------------------------------------------------------------
    # Team properties
    # --------------------------------------------------------------------------
    # Team properties are stored in the dict `self._team_properties`, except for
    # the list of all teams, which is in `self._teams`. These are lazily
    # evaluated: on the first call of any team property,
    # `self._populate_teams()` is run to populate all team properties in a
    # single database query, then the appropriate value is returned.
    #
    # If the team in question doesn't exist or there is more than one, the
    # property in question will raise an ObjectDoesNotExist or
    # MultipleObjectsReturned exception, so that it behaves like a database
    # query. This exception raising is lazy: it does so only when the errant
    # property is called, rather than raising straight away in
    # `self._populate_teams()`.
    #
    # Callers that wish to retrieve the teams of many debates should add
    #   prefetch_related(Prefetch('debateteam_set', queryset=DebateTeam.objects.select_related('team'))
    # to their query set.

    def _populate_teams(self):
        """Populates the team attributes from self.debateteam_set."""
        dts = self.debateteam_set.all()
        if not dts._prefetch_done:  # uses internal undocumented flag of Django's QuerySet model
            dts = dts.select_related('team')

        self._teams = []
        self._multiple_found = []
        self._team_properties = {}

        for dt in dts:
            self._teams.append(dt.team)
            team_key = '%s_team' % dt.side
            dt_key = '%s_dt' % dt.side
            if team_key in self._team_properties:
                self._multiple_found.extend([team_key, dt_key])
            self._team_properties[team_key] = dt.team
            self._team_properties[dt_key] = dt

    def _team_property(attr):  # noqa: N805
        """Used to construct properties that rely on self._populate_teams()."""
        @property
        def _property(self):
            if not hasattr(self, '_team_properties'):
                self._populate_teams()
            if attr in self._multiple_found:
                raise MultipleDebateTeamsError("Multiple debate teams found for '%s' in debate ID %d. "
                    "Teams in debate are: %s." % (attr, self.id, self._teams_and_sides_display()))
            try:
                return self._team_properties[attr]
            except KeyError:
                raise NoDebateTeamFoundError("No debate team found for '%s' in debate ID %d. "
                    "Teams in debate are: %s." % (attr, self.id, self._teams_and_sides_display()))
        return _property

    @property
    def teams(self):
        # No need for _team_property overhead, this list is guaranteed to exist
        # (it just might be empty).
        if not hasattr(self, '_teams'):
            self._populate_teams()
        return self._teams

    def debateteams_ordered(self):
        for side in self.round.tournament.sides:
            yield self.get_dt(side)

    aff_team = _team_property('aff_team')
    neg_team = _team_property('neg_team')
    og_team = _team_property('og_team')
    oo_team = _team_property('oo_team')
    cg_team = _team_property('cg_team')
    co_team = _team_property('co_team')
    aff_dt = _team_property('aff_dt')
    neg_dt = _team_property('neg_dt')
    og_dt = _team_property('og_dt')
    oo_dt = _team_property('oo_dt')
    cg_dt = _team_property('cg_dt')
    co_dt = _team_property('co_dt')

    def get_team(self, side):
        return getattr(self, '%s_team' % side)

    def get_dt(self, side):
        """dt = DebateTeam"""
        return getattr(self, '%s_dt' % side)

    # --------------------------------------------------------------------------
    # Other properties
    # --------------------------------------------------------------------------

    @property
    def confirmed_ballot(self):
        """Returns the confirmed BallotSubmission for this debate, or None if
        there is no such ballot submission."""
        try:
            return self._confirmed_ballot
        except AttributeError:
            try:
                self._confirmed_ballot = self.ballotsubmission_set.get(confirmed=True)
            except ObjectDoesNotExist:
                self._confirmed_ballot = None
            return self._confirmed_ballot

    def get_flags_display(self):
        if not self.flags:
            return []  # don't return [""]
        else:
            # If the verbose description can't be found, just show the raw flag
            return [DRAW_FLAG_DESCRIPTIONS.get(f, f) for f in self.flags.split(",")]

    @property
    def history(self):
        try:
            return self._history
        except AttributeError:
            self._history = self.aff_team.seen(self.neg_team, before_round=self.round.seq)
            return self._history

    @property
    def adjudicators(self):
        """Returns an AdjudicatorAllocation containing the adjudicators for this
        debate."""
        try:
            return self._adjudicators
        except AttributeError:
            from adjallocation.allocation import AdjudicatorAllocation
            self._adjudicators = AdjudicatorAllocation(self, from_db=True)
            return self._adjudicators

    @property
    def division_motion(self):
        from motions.models import Motion
        try:
            # Pretty sure there should never be > 1
            return Motion.objects.filter(round=self.round, divisions=self.division).first()
        except ObjectDoesNotExist:
            # It's easiest to assume a division motion is always present, so
            # return a fake one if it is not
            return Motion(text='-', reference='-')

    # For the front end need to ensure that there are no gaps in the debateTeams
    def serial_debateteams_ordered(self):
        t = self.round.tournament
        for side in t.sides:
            sdt = {'side': side, 'team': None,
                   'position': get_side_name(t, side, 'full'),
                   'abbr': get_side_name(t, side, 'abbr')}
            try:
                debate_team = self.get_dt(side)
                sdt['team'] = debate_team.team.serialize()
            except ObjectDoesNotExist:
                pass

            yield sdt

    def serialize(self):
        round = self.round
        debate = {'id': self.id, 'bracket': self.bracket,
                  'importance': self.importance, 'locked': False}
        debate['venue'] = self.venue.serialize() if self.venue else None
        debate['debateTeams'] = list(self.serial_debateteams_ordered())
        debate['debateAdjudicators'] = [{
            'position': position,
            'adjudicator': adj.serialize(round=round),
        } for adj, position in self.adjudicators.with_debateadj_types()]
        debate['sidesConfirmed'] = self.sides_confirmed
        return debate


class DebateTeamManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('debate')


class DebateTeam(models.Model):
    SIDE_AFF = 'aff'
    SIDE_NEG = 'neg'
    SIDE_OG = 'og'
    SIDE_OO = 'oo'
    SIDE_CG = 'cg'
    SIDE_CO = 'co'
    SIDE_CHOICES = ((SIDE_AFF, _("affirmative")),
                    (SIDE_NEG, _("negative")),
                    (SIDE_OG, _("opening government")),
                    (SIDE_OO, _("opening opposition")),
                    (SIDE_CG, _("closing government")),
                    (SIDE_CO, _("closing opposition")))

    objects = DebateTeamManager()

    debate = models.ForeignKey(Debate, models.CASCADE, db_index=True,
        verbose_name=_("debate"))
    team = models.ForeignKey('participants.Team', models.PROTECT,
        verbose_name=_("team"))
    side = models.CharField(max_length=3, choices=SIDE_CHOICES,
        verbose_name=_("side"))

    # comma-separated list of strings
    flags = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _("debate team")
        verbose_name_plural = _("debate teams")

    def __str__(self):
        return '{} in {}'.format(self.team.short_name, self.debate)

    @property
    def opponent(self):
        try:
            return self._opponent
        except AttributeError:
            try:
                self._opponent = DebateTeam.objects.exclude(side=self.side).select_related(
                        'team', 'team__institution').get(debate=self.debate)
            except (DebateTeam.DoesNotExist, DebateTeam.MultipleObjectsReturned):
                logger.warning("No opponent found for %s", str(self))
                self._opponent = None
            return self._opponent

    def get_flags_display(self):
        if not self.flags:
            return []  # don't return [""]
        else:
            # If the verbose description can't be found, just show the raw flag
            return [DRAW_FLAG_DESCRIPTIONS.get(f, f) for f in self.flags.split(",")]

    def get_result_display(self):

        if self.win is None:
            if self.points is 3:
                return "Placed 1st"
            elif self.points is 2:
                return "Placed 2nd"
            elif self.points is 1:
                return "Placed 3rd"
            elif self.points is 0:
                return "Placed 4th"
            else:
                return ugettext("result unknown")
        elif self.win is True:
            return ugettext("Won")
        elif self.win is False:
            return ugettext("Lost")
        else:
            return ugettext("result unknown")

    @property
    def win(self):
        """Convenience function. Returns True if this team won, False if this
        team lost, or None if there isn't a confirmed result.

        This result is stored for the lifetime of the instance -- it won't
        update on the same instance if a result is entered."""
        try:
            return self._win
        except AttributeError:
            try:
                self._win = self.teamscore_set.get(ballot_submission__confirmed=True).win
            except ObjectDoesNotExist:
                self._win = None
            return self._win

    @property
    def points(self):
        """Convenience function. Returns the number of points this team received
        or None if there isn't a confirmed result.

        This result is stored for the lifetime of the instance -- it won't
        update on the same instance if a result is entered."""
        try:
            return self._points
        except AttributeError:
            try:
                self._points = self.teamscore_set.get(ballot_submission__confirmed=True).points
            except ObjectDoesNotExist:
                self._points = None
            return self._points

    def get_side_name(self, tournament=None, name_type='full'):
        """Should be used instead of get_side_display() on views.
        `tournament` can be passed in if known, for performance."""
        try:
            return get_side_name(tournament or self.debate.round.tournament,
                                 self.side, name_type)
        except KeyError:
            return self.get_side_display()  # fallback


class MultipleDebateTeamsError(DebateTeam.MultipleObjectsReturned):
    pass


class NoDebateTeamFoundError(DebateTeam.DoesNotExist):
    pass


class TeamSideAllocation(models.Model):
    """Model to store team side allocations for tournaments like Joynt
    Scroll (New Zealand). Each team-round combination should have one of these.
    In tournaments without team side allocations, just don't use this
    model."""

    round = models.ForeignKey('tournaments.Round', models.CASCADE,
        verbose_name=_("round"))
    team = models.ForeignKey('participants.Team', models.CASCADE,
        verbose_name=_("team"))
    side = models.CharField(max_length=3, choices=DebateTeam.SIDE_CHOICES,
        verbose_name=_("side"))

    class Meta:
        unique_together = [('round', 'team')]
        verbose_name = _("team side allocation")
        verbose_name_plural = _("team side allocations")
