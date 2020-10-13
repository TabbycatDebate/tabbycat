import logging

from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from tournaments.utils import get_side_name
from utils.fields import ChoiceArrayField

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
    STATUS_CHOICES = (
        (STATUS_NONE, _("none")),
        (STATUS_POSTPONED, _("postponed")),
        (STATUS_DRAFT, _("draft")),
        (STATUS_CONFIRMED, _("confirmed")),
    )
    STATUS_CHOICES_RESTRICTED = (  # If postponements are disabled - used in forms
        (STATUS_NONE, _("none")),
        (STATUS_DRAFT, _("draft")),
        (STATUS_CONFIRMED, _("confirmed")),
    )

    objects = DebateManager()

    round = models.ForeignKey('tournaments.Round', models.CASCADE, db_index=True,
        verbose_name=_("round"))
    venue = models.ForeignKey('venues.Venue', models.SET_NULL, blank=True, null=True,
        verbose_name=_("room"))

    bracket = models.FloatField(default=0,
        verbose_name=_("bracket"))
    room_rank = models.IntegerField(default=0,
        verbose_name=_("room rank"))

    flags = ChoiceArrayField(blank=True, default=list,
        base_field=models.CharField(max_length=15, choices=DRAW_FLAG_DESCRIPTIONS))

    importance = models.IntegerField(default=0, choices=[(i, i) for i in range(-2, 3)],
        verbose_name=_("importance"))
    result_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE,
        verbose_name=_("result status"))
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
        except Exception:
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
            return teams_list + gettext(" (sides not confirmed)")

        try:
            # This can sometimes arise during the call to self.round.tournament.sides
            # if preferences aren't loaded correctly, which happens in `manage.py shell`.
            sides = self.round.tournament.sides
        except IndexError:
            return self._teams_and_sides_display()  # fallback

        try:
            # Translators: This goes between teams in a debate, e.g. "Auckland 1
            # vs Vic Wellington 1". Mind the leading and trailing spaces.
            return gettext(" vs ").join(self.get_team(side).short_name for side in sides)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return self._teams_and_sides_display()

    def _teams_and_sides_display(self):
        return ", ".join(["%s (%s)" % (dt.team.short_name, dt.get_side_display())
                for dt in self.debateteam_set.all()])

    @property
    def matchup_codes(self):
        # Like matchup, but uses team codes. It is not as protected.
        if not self.sides_confirmed:
            teams_list = ", ".join([dt.team.code_name for dt in self.debateteam_set.all()])
            return teams_list + gettext(" (sides not confirmed)")

        try:
            sides = self.round.tournament.sides
            return gettext(" vs ").join(self.get_team(side).code_name for side in sides)
        except (IndexError, ObjectDoesNotExist, MultipleObjectsReturned):
            return ", ".join(["%s (%s)" % (dt.team.code_name, dt.get_side_display())
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
    #   prefetch_related(Prefetch('debateteam_set',
    #       queryset=DebateTeam.objects.select_related('team'))
    # to their query set.

    def _populate_teams(self):
        """Populates the team attributes from self.debateteam_set."""
        dts = self.debateteam_set.all()
        if not dts._prefetch_done:  # uses internal undocumented flag of Django's QuerySet class
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

    @property
    def history(self):
        try:
            return self._history
        except AttributeError:
            self._history = self.aff_team.seen(self.neg_team, before_round=self.round.seq)
            return self._history

    @property
    def related_adjudicator_set(self):
        """Used by objects that work with both Debate and PreformedPanel."""
        return self.debateadjudicator_set

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

    flags = ChoiceArrayField(base_field=models.CharField(max_length=15, choices=DRAW_FLAG_DESCRIPTIONS), blank=True, default=list)

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

    def get_result_display(self):
        if self.team.tournament.pref('teams_in_debate') == 'bp':
            if self.points is not None:
                return gettext("placed %(place)s") % {'place': ordinal(4 - self.points)}
            else:
                return gettext("result unknown")
        else:
            if self.win is True:
                return gettext("won")
            elif self.win is False: # not None
                return gettext("lost")
            else:
                return gettext("result unknown")

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

    def get_side_abbr(self, tournament=None):
        """Convenience function, mainly for use in templates."""
        return self.get_side_name(tournament, 'abbr')


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
