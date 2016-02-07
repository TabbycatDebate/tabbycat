from django.db import models
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned

from tournaments.models import SRManager
from participants.models import Team
from .generator import DRAW_FLAG_DESCRIPTIONS


class DebateManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(DebateManager,
                     self).get_queryset().select_related('round')


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
    division = models.ForeignKey('tournaments.Division', blank=True, null=True)

    bracket = models.FloatField(default=0)
    room_rank = models.IntegerField(default=0)

    # comma-separated list of strings
    flags = models.CharField(max_length=100, blank=True, null=True)

    importance = models.IntegerField(default=2)
    result_status = models.CharField(max_length=1,
                                     choices=STATUS_CHOICES,
                                     default=STATUS_NONE)
    ballot_in = models.BooleanField(default=False)

    class Meta:
        verbose_name = "⚖ Debate"

    def __contains__(self, team):
        return team in (self.aff_team, self.neg_team)

    def __str__(self):
        try:
            return "[{}/{}] {} vs {}".format(
                self.round.tournament.slug, self.round.abbreviation,
                self.aff_team.short_name, self.neg_team.short_name)
        except DebateTeam.DoesNotExist:
            return "[{}/{}] {}".format(
                self.round.tournament.slug, self.round.abbreviation,
                ", ".join([x.short_name for x in self.teams]))

    @property
    def teams(self):
        return Team.objects.filter(debateteam__debate=self)

    @cached_property
    def aff_team(self):
        aff_dt = self.aff_dt
        return aff_dt.team

    @cached_property
    def neg_team(self):
        neg_dt = self.neg_dt
        return neg_dt.team

    def get_team(self, side):
        return getattr(self, '%s_team' % side)

    def get_dt(self, side):
        """dt = DebateTeam"""
        return getattr(self, '%s_dt' % side)

    @cached_property
    def aff_dt(self):
        aff_dt = DebateTeam.objects.select_related(
            'team', 'team__institution').get(
                debate=self,
                position=DebateTeam.POSITION_AFFIRMATIVE)
        return aff_dt

    @cached_property
    def neg_dt(self):
        neg_dt = DebateTeam.objects.select_related(
            'team', 'team__institution').get(
                debate=self,
                position=DebateTeam.POSITION_NEGATIVE)
        return neg_dt

    def get_side(self, team):
        if self.aff_team == team:
            return 'aff'
        if self.neg_team == team:
            return 'neg'
        return None

    @cached_property
    def draw_conflicts(self):
        d = []
        history = self.aff_team.seen(self.neg_team,
                                     before_round=self.round.seq)
        if history:
            d.append("History conflict (%d)" % history)
        if self.aff_team.institution == self.neg_team.institution:
            d.append("Institution conflict")

        return d

    @cached_property
    def confirmed_ballot(self):
        """Returns the confirmed BallotSubmission for this debate, or None if
        there is no such ballot submission."""
        try:
            return self.ballotsubmission_set.get(confirmed=True)
        except ObjectDoesNotExist:  # BallotSubmission isn't defined yet, so can't use BallotSubmission.DoesNotExist
            return None

    @property
    def ballotsubmission_set_by_version(self):
        return self.ballotsubmission_set.order_by('version')

    @property
    def ballotsubmission_set_by_version_except_discarded(self):
        return self.ballotsubmission_set.filter(
            discarded=False).order_by('version')

    @property
    def identical_ballotsubs_dict(self):
        """Returns a dict. Keys are BallotSubmissions, values are lists of
        version numbers of BallotSubmissions that are identical to the key's
        BallotSubmission. Excludes discarded ballots (always)."""
        ballotsubs = self.ballotsubmission_set_by_version_except_discarded
        result = {b: list() for b in ballotsubs}
        for ballotsub1 in ballotsubs:
            # Save a bit of time by avoiding comparisons already done.
            # This relies on ballots being ordered by version.
            for ballotsub2 in ballotsubs.filter(
                    version__gt=ballotsub1.version):
                if ballotsub1.is_identical(ballotsub2):
                    result[ballotsub1].append(ballotsub2.version)
                    result[ballotsub2].append(ballotsub1.version)
        for l in result.values():
            l.sort()
        return result

    @property
    def flags_all(self):
        if not self.flags:
            return []
        else:
            return [DRAW_FLAG_DESCRIPTIONS[f] for f in self.flags.split(",")]

    @property
    def all_conflicts(self):
        return self.draw_conflicts + self.adjudicator_conflicts

    @cached_property
    def adjudicator_conflicts(self):
        class Conflict(object):
            def __init__(self, adj, team):
                self.adj = adj
                self.team = team

            def __str__(self):
                return 'Adj %s + %s' % (self.adj, self.team)

        a = []
        for t, adj in self.adjudicators:
            for team in (self.aff_team, self.neg_team):
                if adj.conflict_with(team):
                    a.append(Conflict(adj, team))

        return a

    @cached_property
    def adjudicators(self):
        from adjallocation.models import DebateAdjudicator, AdjudicatorAllocation
        """Returns an AdjudicatorAllocation containing the adjudicators for this
        debate."""
        adjs = DebateAdjudicator.objects.filter(
            debate=self).select_related('adjudicator')
        alloc = AdjudicatorAllocation(self)
        for a in adjs:
            if a.type == a.TYPE_CHAIR:
                alloc.chair = a.adjudicator
            if a.type == a.TYPE_PANEL:
                alloc.panel.append(a.adjudicator)
            if a.type == a.TYPE_TRAINEE:
                alloc.trainees.append(a.adjudicator)
        return alloc

    @property
    def chair(self):
        from adjallocation.models import DebateAdjudicator
        da_adj = list(DebateAdjudicator.objects.filter(debate=self, type="C"))
        a_adj = da_adj[0].adjudicator
        return a_adj

    @property
    def matchup(self):
        return '%s vs %s' % (self.aff_team.short_name,
                             self.neg_team.short_name)

    @property
    def division_motion(self):
        from motions.models import Motion
        return Motion.objects.filter(round=self.round, divisions=self.division)


class DebateTeam(models.Model):
    POSITION_AFFIRMATIVE = 'A'
    POSITION_NEGATIVE = 'N'
    POSITION_UNALLOCATED = 'u'
    POSITION_CHOICES = ((POSITION_AFFIRMATIVE, 'Affirmative'),
                        (POSITION_NEGATIVE, 'Negative'),
                        (POSITION_UNALLOCATED, 'Unallocated'), )

    objects = SRManager()

    debate = models.ForeignKey(Debate, db_index=True)
    team = models.ForeignKey('participants.Team')
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)

    def __str__(self):
        return '{} in {}'.format(self.team.short_name, self.debate)

    @cached_property  # TODO: this slows down the standings pages reasonably heavily
    def opposition(self):
        try:
            return DebateTeam.objects.exclude(
                position=self.position).select_related(
                    'team', 'team__institution').get(debate=self.debate)
        except (DebateTeam.DoesNotExist, DebateTeam.MultipleObjectsReturned):
            logger.error("Error finding opposition: %s, %s", self.debate,
                         self.position)
            return None

    @cached_property
    def result(self):
        """Returns 'won' if won, 'lost' if lost, 'result unknown' if no result confirmed."""
        if self.debate.confirmed_ballot and self.debate.confirmed_ballot.ballot_set:
            ballotset = self.debate.confirmed_ballot.ballot_set
            if ballotset.aff_win and self.position == DebateTeam.POSITION_AFFIRMATIVE:
                return 'won'
            if ballotset.neg_win and self.position == DebateTeam.POSITION_NEGATIVE:
                return 'won'
            return 'lost'
        return 'result unknown'

    class Meta:
        verbose_name = "🙊 Debate Team"


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


class TeamVenuePreference(models.Model):
    team = models.ForeignKey('participants.Team', db_index=True)
    venue_group = models.ForeignKey('venues.VenueGroup')
    priority = models.IntegerField()

    class Meta:
        ordering = ['priority', ]
        verbose_name = "🏩 Team Venue Pref"

    def __str__(self):
        return '%s with priority %s for %s' % (self.team, self.priority,
                                               self.venue_group)


class InstitutionVenuePreference(models.Model):
    institution = models.ForeignKey('participants.Institution', db_index=True)
    venue_group = models.ForeignKey('venues.VenueGroup')
    priority = models.IntegerField()

    class Meta:
        ordering = ['priority', ]
        verbose_name = "🏩 Institutional Venue Pref"

    def __str__(self):
        return '%s with priority %s for %s' % (self.institution, self.priority,
                                               self.venue_group)
