import logging
from warnings import warn

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from participants.models import Team

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
    STATUS_CHOICES = ((STATUS_NONE, 'None'),
                      (STATUS_POSTPONED, 'Postponed'),
                      (STATUS_DRAFT, 'Draft'),
                      (STATUS_CONFIRMED, 'Confirmed'), )

    objects = DebateManager()

    round = models.ForeignKey('tournaments.Round', db_index=True)
    venue = models.ForeignKey('venues.Venue', blank=True, null=True)
    division = models.ForeignKey('divisions.Division', blank=True, null=True)

    bracket = models.FloatField(default=0)
    room_rank = models.IntegerField(default=0)

    time = models.DateTimeField(
        blank=True, null=True,
        help_text="The time/date of a debate if it is specifically scheduled")

    # comma-separated list of strings
    flags = models.CharField(max_length=100, blank=True, null=True)

    importance = models.IntegerField(default=0)
    result_status = models.CharField(max_length=1,
                                     choices=STATUS_CHOICES,
                                     default=STATUS_NONE)
    ballot_in = models.BooleanField(default=False)

    def __contains__(self, team):
        return team in (self.aff_team, self.neg_team)

    def __str__(self):
        description = "[{}/{}/{}] ".format(self.round.tournament.slug, self.round.abbreviation, self.id)
        try:
            description += self.matchup
        except:
            logger.critical("Error rendering Debate.matchup in Debate.__str__", exc_info=True)
            description += "<error showing teams>"
        return description

    @property
    def matchup(self):
        # This method is used by __str__, so it's not allowed to crash (ever)
        try:
            return "%s vs %s" % (self.aff_team.short_name, self.neg_team.short_name)
        except (Team.DoesNotExist, Team.MultipleObjectsReturned):
            dts = self.debateteam_set.all()
            if all(dt.position == DebateTeam.POSITION_UNALLOCATED for dt in dts):
                return ", ".join([dt.team.short_name for dt in dts])
            else:
                return ", ".join(["%s (%s)" % (dt.team.short_name, dt.get_position_display().lower())
                    for dt in dts])

    @property
    def teams(self):
        """Returns an iterable object containing the teams in the debate in
        arbitrary order. The iterable may be a list or a QuerySet."""
        try:
            return [self._aff_team, self._neg_team]
        except AttributeError:
            return Team.objects.filter(debateteam__debate=self)

    @property
    def aff_team(self):
        try:
            return self._aff_team # may be populated by Round.debate_set_with_prefetches
        except AttributeError:
            self._aff_team = Team.objects.select_related('institution').get(
                debateteam__debate=self, debateteam__position=DebateTeam.POSITION_AFFIRMATIVE)
            return self._aff_team

    @property
    def neg_team(self):
        try:
            return self._neg_team
        except AttributeError:
            self._neg_team = Team.objects.select_related('institution').get(
                debateteam__debate=self, debateteam__position=DebateTeam.POSITION_NEGATIVE)
            return self._neg_team

    @property
    def aff_dt(self):
        try:
            return self._aff_dt # may be populated by Round.debate_set_with_prefetches
        except AttributeError:
            self._aff_dt = self.debateteam_set.select_related('team', 'team__institution').get(
                position=DebateTeam.POSITION_AFFIRMATIVE)
            return self._aff_dt

    @property
    def neg_dt(self):
        try:
            return self._neg_dt # may be populated by Round.debate_set_with_prefetches
        except AttributeError:
            self._neg_dt = self.debateteam_set.select_related('team', 'team__institution').get(
                position=DebateTeam.POSITION_NEGATIVE)
            return self._neg_dt # may be populated by Round.debate_set_with_prefetches

    def get_team(self, side):
        return getattr(self, '%s_team' % side)

    def get_dt(self, side):
        """dt = DebateTeam"""
        return getattr(self, '%s_dt' % side)

    def get_side(self, team):
        # Deprecated 25/7/2016, does not appear to be used anywhere, remove after 25/8/2016.
        warn("Debate.get_side() is deprecated", stacklevel=2)
        if self.aff_team == team:
            return 'aff'
        if self.neg_team == team:
            return 'neg'
        return None

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
    def flags_all(self):
        if not self.flags:
            return []
        else:
            return [DRAW_FLAG_DESCRIPTIONS[f] for f in self.flags.split(",")]

    @property
    def history(self):
        try:
            return self._history
        except AttributeError:
            self._history = self.aff_team.seen(self.neg_team, before_round=self.round.seq)
            return self._history

    @property
    def draw_conflicts(self):
        # Deprecated 14/9/2016, remove after 14/10/2016
        raise RuntimeError("Debate.draw_conflicts is deprecated.")

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
    def get_division_motions(self):
        from motions.models import Motion
        motions = Motion.objects.filter(round=self.round, divisions=self.division)
        if motions.count() > 0:
            return motions[0] # Pretty sure this should never be > 1
        else:
            # Its easiest to assume a division motion is always present, so
            # return a fake one if it is not
            from motions.models import Motion
            return Motion(text='-', reference='-')


class DebateTeamManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('debate')


class DebateTeam(models.Model):
    POSITION_AFFIRMATIVE = 'A'
    POSITION_NEGATIVE = 'N'
    POSITION_UNALLOCATED = 'u'
    POSITION_CHOICES = ((POSITION_AFFIRMATIVE, 'Affirmative'),
                        (POSITION_NEGATIVE, 'Negative'),
                        (POSITION_UNALLOCATED, 'Unallocated'), )

    objects = DebateTeamManager()

    debate = models.ForeignKey(Debate, db_index=True)
    team = models.ForeignKey('participants.Team')
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)

    def __str__(self):
        return '{} in {}'.format(self.team.short_name, self.debate)

    @property
    def opponent(self):
        try:
            return self._opponent
        except AttributeError:
            try:
                self._opponent = DebateTeam.objects.exclude(position=self.position).select_related(
                        'team', 'team__institution').get(debate=self.debate)
            except (DebateTeam.DoesNotExist, DebateTeam.MultipleObjectsReturned):
                logger.warning("No opponent found for %s", str(self))
                self._opponent = None
            return self._opponent

    @property
    def opposition(self):
        # Added 11/7/2016, convert to RuntimeError after 1.1.2 release, then remove a month after that
        warn("DebateTeam.opposition is deprecated, use DebateTeam.opponent instead.", stacklevel=2)
        return self.opponent

    @property
    def result(self):
        # Added 12/9/2016, convert to RuntimeError after 1.1.2 release, then remove a month after that
        warn("DebateTeam.result is deprecated, use DebateTeam.get_result_display() instead.", stacklevel=2)
        return self.get_result_display()

    def get_result_display(self):
        if self.win is True:
            return 'won'
        elif self.win is False:
            return 'lost'
        else:
            return 'result unknown'

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


class TeamPositionAllocation(models.Model):
    """Model to store team position allocations for tournaments like Joynt
    Scroll (New Zealand). Each team-round combination should have one of these.
    In tournaments without team position allocations, just don't use this
    model."""

    POSITION_AFFIRMATIVE = DebateTeam.POSITION_AFFIRMATIVE
    POSITION_NEGATIVE = DebateTeam.POSITION_NEGATIVE
    POSITION_UNALLOCATED = DebateTeam.POSITION_UNALLOCATED
    POSITION_CHOICES = DebateTeam.POSITION_CHOICES

    round = models.ForeignKey('tournaments.Round')
    team = models.ForeignKey('participants.Team')
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)

    class Meta:
        unique_together = [('round', 'team')]
