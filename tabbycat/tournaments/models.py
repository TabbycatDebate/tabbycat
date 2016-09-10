from warnings import warn

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import cached_property

from participants.emoji import EMOJI_LIST
from utils.managers import LookupByNameFieldsMixin

import logging
logger = logging.getLogger(__name__)


PROHIBITED_TOURNAMENT_SLUGS = [
    'jet', 'database', 'admin', 'accounts',   # System
    'start', 'create',  # Setup Wizards
    'draw', 'participants', 'favicon.ico',  # Cross-Tournament app's view roots
    't', '__debug__', 'static']  # Misc

def validate_tournament_slug(value):
    if value in PROHIBITED_TOURNAMENT_SLUGS:
        raise ValidationError(
            "You can't use any of the following as tournament slugs, because "
            "they're reserved for Tabbycat system URLs: %(prohibited_list)s.",
            params={'prohibited_list': ", ".join(PROHIBITED_TOURNAMENT_SLUGS)}
        )


class Tournament(models.Model):
    name = models.CharField(max_length=100,
        help_text="The full name used on the homepage, e.g. \"Australasian Intervarsity Debating Championships 2016\"")
    short_name = models.CharField(max_length=25, blank=True, null=True, default="",
        help_text="The name used in the menu, e.g. \"Australs 2016\"")
    emoji = models.CharField(max_length=2, blank=True, null=True, unique=True, choices=EMOJI_LIST)
    seq = models.IntegerField(blank=True, null=True,
        help_text="A number that determines the relative order in which tournaments are displayed on the homepage.")
    slug = models.SlugField(unique=True, validators=[validate_tournament_slug],
        help_text="The sub-URL of the tournament, cannot have spaces, e.g. \"australs2016\"")
    current_round = models.ForeignKey('Round', models.SET_NULL, null=True, blank=True, related_name='tournament_',
        help_text="Must be set for the tournament to start! (Set after rounds are inputted)")
    welcome_msg = models.TextField(blank=True, null=True, default="",
        help_text="Text/html entered here shows on the homepage for this tournament")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['seq', ]

    def __init__(self, *args, **kwargs):
        self._prefs = {}
        return super().__init__(*args, **kwargs)

    def __str__(self):
        if self.short_name:
            return str(self.short_name)
        else:
            return str(self.name)

    # --------------------------------------------------------------------------
    # Properties related to preferences
    # --------------------------------------------------------------------------

    def pref(self, name):
        try:
            return self._prefs[name]
        except KeyError:
            self._prefs[name] = self.preferences.get_by_name(name)
            return self._prefs[name]

    @property
    def LAST_SUBSTANTIVE_POSITION(self):  # flake8: noqa
        """Returns the number of substantive speakers."""
        return self.pref('substantive_speakers')

    @property
    def REPLY_POSITION(self):  # flake8: noqa
        """If there is a reply position, returns one more than the number of
        substantive speakers. If there is no reply position, returns None."""
        if self.pref('reply_scores_enabled'):
            return self.pref('substantive_speakers') + 1
        else:
            return None

    @property
    def POSITIONS(self):  # flake8: noqa
        """Guaranteed to be consecutive numbers starting at one. Includes the
        reply speaker."""
        speaker_positions = 1 + self.pref('substantive_speakers')
        if self.pref('reply_scores_enabled') is True:
            speaker_positions = speaker_positions + 1
        return list(range(1, speaker_positions))

    # --------------------------------------------------------------------------
    # Permalinks
    # --------------------------------------------------------------------------

    @models.permalink
    def get_absolute_url(self):
        return ('tournament-admin-home', [self.slug])

    @models.permalink
    def get_public_url(self):
        return ('tournament-public-index', [self.slug])

    # --------------------------------------------------------------------------
    # Convenience querysets
    # --------------------------------------------------------------------------

    @cached_property
    def teams(self):
        warn('Tournament.teams is deprecated, use Tournament.team_set instead.', stacklevel=2)
        return self.team_set

    @property
    def relevant_adjudicators(self):
        """Convenience property for retrieving adjudicators relevant to the tournament.
        Returns a QuerySet."""
        if self.pref('share_adjs'):
            return Adjudicator.objects.filter(Q(tournament=self) | Q(tournament__isnull=True))
        else:
            return self.adjudicator_set.all()

    @property
    def relevant_venues(self):
        """Convenience property for retrieving venues relevant to the tournament.
        Returns a QuerySet."""
        if self.pref('share_adjs'):
            return Venue.objects.filter(Q(tournament=self) | Q(tournament__isnull=True))
        else:
            return self.venue_set.all()

    def prelim_rounds(self, before=None, until=None):
        """Convenience function for retrieving preliminary rounds. Returns a QuerySet."""
        qs = self.round_set.filter(stage=Round.STAGE_PRELIMINARY)
        if until:
            qs = qs.filter(seq__lte=until.seq)
        if before:
            qs = qs.filter(seq__lt=before.seq)
        return qs

    def break_rounds(self):
        """Convenience function for retrieving break rounds. Returns a QuerySet."""
        return self.round_set.filter(stage=Round.STAGE_ELIMINATION)

    @cached_property
    def adj_feedback_questions(self):
        return self.adjudicatorfeedbackquestion_set.order_by("seq")

    # --------------------------------------------------------------------------
    # Cached
    # --------------------------------------------------------------------------

    @cached_property
    def get_current_round_cached(self):
        cached_key = "%s_current_round_object" % self.slug
        if self.current_round:
            cache.get_or_set(cached_key, self.current_round, None)
            return cache.get(cached_key)
        else:
            return None

    # --------------------------------------------------------------------------
    # Operations that modify the instance
    # --------------------------------------------------------------------------

    def advance_round(self):
        next_round_seq = self.current_round.seq + 1
        next_round = Round.objects.get(seq=next_round_seq, tournament=self)
        self.current_round = next_round
        self.save()


class RoundManager(LookupByNameFieldsMixin, models.Manager):
    use_for_related_fields = True
    name_fields = ['name', 'abbreviation']

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').order_by('seq')


class Round(models.Model):
    DRAW_RANDOM = 'R'
    DRAW_MANUAL = 'M'
    DRAW_ROUNDROBIN = 'D'
    DRAW_POWERPAIRED = 'P'
    DRAW_FIRSTBREAK = 'F'
    DRAW_BREAK = 'B'
    DRAW_CHOICES = ((DRAW_RANDOM, 'Random'),
                    (DRAW_MANUAL, 'Manual'),
                    (DRAW_ROUNDROBIN, 'Round-robin'),
                    (DRAW_POWERPAIRED, 'Power-paired'),
                    (DRAW_FIRSTBREAK, 'First elimination'),
                    (DRAW_BREAK, 'Subsequent elimination'), )

    STAGE_PRELIMINARY = 'P'
    STAGE_ELIMINATION = 'E'
    STAGE_CHOICES = ((STAGE_PRELIMINARY, 'Preliminary'),
                     (STAGE_ELIMINATION, 'Elimination'), )

    VALID_DRAW_TYPES_BY_STAGE = {
        STAGE_PRELIMINARY: [DRAW_RANDOM, DRAW_MANUAL, DRAW_ROUNDROBIN, DRAW_POWERPAIRED],
        STAGE_ELIMINATION: [DRAW_FIRSTBREAK, DRAW_BREAK],
    }

    STATUS_NONE = 'N'
    STATUS_DRAFT = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_RELEASED = 'R'
    STATUS_CHOICES = ((STATUS_NONE, 'None'),
                      (STATUS_DRAFT, 'Draft'),
                      (STATUS_CONFIRMED, 'Confirmed'),
                      (STATUS_RELEASED, 'Released'), )

    objects = RoundManager()

    tournament = models.ForeignKey(Tournament, models.CASCADE)
    seq = models.IntegerField(help_text="A number that determines the order of the round, should count consecutively from 1 for the first round")
    name = models.CharField(max_length=40, help_text="e.g. \"Round 1\"")
    abbreviation = models.CharField(max_length=10, help_text="e.g. \"R1\"")
    stage = models.CharField(max_length=1, choices=STAGE_CHOICES, default=STAGE_PRELIMINARY,
        help_text="Preliminary = inrounds, elimination = outrounds")
    draw_type = models.CharField(max_length=1, choices=DRAW_CHOICES,
        help_text="Which draw method to use")
    break_category = models.ForeignKey('breakqual.BreakCategory', models.CASCADE, blank=True, null=True,
        help_text="If elimination round, which break category")

    draw_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE,
       help_text="The status of this round's draw")

    feedback_weight = models.FloatField(default=0,
        help_text="The extent to which each adjudicator's overall score depends on feedback vs their test score. At 0, it is 100% drawn from their test score, at 1 it is 100% drawn from feedback.")
    silent = models.BooleanField(default=False,
        help_text="If marked silent, information about this round (such as it's results) will not be shown publicly.")
    motions_released = models.BooleanField(default=False,
        help_text="Whether motions will appear on the public website, assuming that feature is turned on")
    starts_at = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = [('tournament', 'seq')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']

    def __str__(self):
        return "[%s] %s" % (self.tournament, self.name)

    def clean(self):
        errors = {}

        # Draw type must be consistent with stage
        valid_draw_types = Round.VALID_DRAW_TYPES_BY_STAGE[self.stage]
        if self.draw_type not in valid_draw_types:
            display_names = [name for value, name in Round.DRAW_CHOICES if value in valid_draw_types]
            errors['draw_type'] = ValidationError("A round in the {stage} stage must have a "
                "draw type that is one of: {valid}".format(
                    stage=self.get_stage_display().lower(),
                    valid=", ".join(display_names)
                ))

        # Break rounds must have a break category
        if self.stage == Round.STAGE_ELIMINATION and self.break_category is None:
            errors['break_category'] = ValidationError("Elimination rounds must have a break category.")

        if errors:
            raise ValidationError(errors)

    def num_debates_without_chair(self):
        """Returns the number of debates in the round that lack a chair, or have
        more than one chair."""
        from adjallocation.models import DebateAdjudicator
        debates_in_round = self.debate_set.count()
        debates_with_one_chair = self.debate_set.filter(debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR).annotate(
                num_chairs=Count('debateadjudicator')).filter(num_chairs=1).count()
        logger.debug("%d debates without chair", debates_in_round - debates_with_one_chair)
        return debates_in_round - debates_with_one_chair

    def num_debates_with_even_panel(self):
        """Returns the number of debates in the round, in which there are an
        positive and even number of voting judges."""
        from adjallocation.models import DebateAdjudicator
        debates_with_even_panel = self.debate_set.exclude(
                debateadjudicator__type=DebateAdjudicator.TYPE_TRAINEE
            ).annotate(
                panellists=Count('debateadjudicator'),
                odd_panellists=Count('debateadjudicator') % 2
            ).filter(panellists__gt=0, odd_panellists=0).count()
        logger.debug("%d debates with even panel", debates_with_even_panel)
        return debates_with_even_panel

    def num_debates_without_venue(self):
        debates_without_venue = self.debate_set.filter(venue__isnull=True).count()
        logger.debug("%d debates without venue", debates_without_venue)
        return debates_without_venue

    @cached_property
    def is_break_round(self):
        return self.stage == self.STAGE_ELIMINATION

    # --------------------------------------------------------------------------
    # Draw retrieval methods
    # --------------------------------------------------------------------------

    def get_draw(self, ordering=('venue__name',)):
        warn("Round.get_draw() is deprecated, use Round.debate_set or Round.debate_set_with_prefetches() instead.", stacklevel=2)
        related = ('venue',)
        if self.tournament.pref('enable_divisions'):
            related += ('division', 'division__venue_group')
        return self.debate_set.order_by(*ordering).select_related(*related)

    def debate_set_with_prefetches(self, filter_kwargs=None, ordering=('venue__name',),
            teams=True, adjudicators=True, speakers=True, divisions=True, ballotsubs=False,
            wins=False, ballotsets=False, venues=True, institutions=False):
        """Returns the debate set, with aff_team and neg_team populated.
        This is basically a prefetch-like operation, except that it also figures
        out which team is on which side, and sets attributes accordingly."""
        from draw.prefetch import populate_teams
        from results.prefetch import populate_confirmed_ballots, populate_wins

        debates = self.debate_set.all()
        if filter_kwargs:
            debates = debates.filter(**filter_kwargs)
        if ballotsubs or ballotsets:
            debates = debates.prefetch_related('ballotsubmission_set', 'ballotsubmission_set__submitter')
        if adjudicators:
            debates = debates.prefetch_related('debateadjudicator_set__adjudicator')
        if divisions and self.tournament.pref('enable_divisions'):
            debates = debates.select_related('division', 'division__venue_group')
        if venues:
            debates = debates.select_related('venue', 'venue__group')

        if ordering:
            debates = debates.order_by(*ordering)

        # These functions populate relevant attributes of each debate, operating in-place
        if teams or speakers or wins or institutions:
            populate_teams(debates, speakers=speakers, institutions=institutions)  # _aff_team, _aff_dt, _neg_team, _neg_dt
        if ballotsubs or ballotsets:
            populate_confirmed_ballots(debates, motions=True, ballotsets=ballotsets)
        if wins:
            populate_wins(debates)

        return debates

    # --------------------------------------------------------------------------
    # Convenience querysets
    # --------------------------------------------------------------------------

    @property
    def active_teams(self):
        return self.tournament.team_set.filter(round_availabilities__round=self)

    @property
    def active_adjudicators(self):
        return self.tournament.relevant_adjudicators.filter(round_availabilities__round=self)

    @property
    def active_venues(self):
        return self.tournament.relevant_venues.filter(round_availabilities__round=self)

    def unused_venues(self):
        return self.active_venues.exclude(debate__round=self)

    def unused_adjudicators(self):
        return self.active_adjudicators.exclude(debateadjudicator__debate__round=self)

    def unused_teams(self):
        return self.active_teams.exclude(debateteam__debate__round=self)

    # --------------------------------------------------------------------------
    # Other convenience properties
    # --------------------------------------------------------------------------

    @cached_property
    def prev(self):
        try:
            return self.tournament.round_set.filter(seq__lt=self.seq).order_by('-seq').first()
        except Round.DoesNotExist:
            return None

    @property
    def motions_good_for_public(self):
        return self.motions_released or not self.motion_set.exists()
