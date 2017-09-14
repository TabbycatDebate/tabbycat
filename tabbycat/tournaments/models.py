from warnings import warn

from django.db import models
from django.db.models import Count, Prefetch, Q
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from participants.emoji import EMOJI_LIST
from utils.managers import LookupByNameFieldsMixin

import logging
logger = logging.getLogger(__name__)


PROHIBITED_TOURNAMENT_SLUGS = [
    'jet', 'database', 'admin', 'accounts',   # System
    'start', 'create', 'donations', 'load-demo', # Setup Wizards
    'draw', 'participants', 'favicon.ico',  # Cross-Tournament app's view roots
    't', '__debug__', 'static']  # Misc


def validate_tournament_slug(value):
    if value in PROHIBITED_TOURNAMENT_SLUGS:
        raise ValidationError(
            _("You can't use any of the following as tournament slugs, because "
            "they're reserved for Tabbycat system URLs: %(prohibited_list)s."),
            params={'prohibited_list': ", ".join(PROHIBITED_TOURNAMENT_SLUGS)}
        )


class Tournament(models.Model):
    name = models.CharField(max_length=100,
        verbose_name=_("name"),
        help_text=_("The full name, e.g. \"Australasian Intervarsity Debating Championships 2016\""))
    short_name = models.CharField(max_length=25, blank=True, default="",
        verbose_name=_("short name"),
        help_text=_("The name used in the menu, e.g. \"Australs 2016\""))
    emoji = models.CharField(max_length=2, blank=True, null=True, unique=True, choices=EMOJI_LIST,
        verbose_name=_("emoji")) # uses null=True to allow multiple tournaments to have no emoji
    seq = models.IntegerField(blank=True, null=True,
        verbose_name=_("sequence number"),
        help_text=_("A number that determines the relative order in which tournaments are displayed on the homepage."))
    slug = models.SlugField(unique=True, validators=[validate_tournament_slug],
        verbose_name=_("slug"),
        help_text=_("The sub-URL of the tournament, cannot have spaces, e.g. \"australs2016\""))
    current_round = models.ForeignKey('Round', models.SET_NULL, null=True, blank=True, related_name='current_tournament',
        verbose_name=_("current round"),
        help_text=_("Must be set for the tournament to start! (Set after rounds are inputted)"))
    welcome_msg = models.TextField(blank=True, null=True, default="",
        verbose_name=_("welcome message"),
        help_text=_("Text/html entered here shows on the homepage for this tournament"))
    active = models.BooleanField(verbose_name=_("active"), default=True)

    class Meta:
        verbose_name = _('tournament')
        verbose_name_plural = _('tournaments')
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
        """Keep a record in this instance, to avoid hitting the cache
        unnecessarily. Note that this means that, if a tournament preference is
        changed, an instance of the Tournament (Python) object that has already
        queries that preference value won't pick up on the change."""
        try:
            return self._prefs[name]
        except KeyError:
            self._prefs[name] = self.preferences.get_by_name(name)
            return self._prefs[name]

    @property
    def sides(self):
        """Returns a list of side codes."""
        option = self.pref('teams_in_debate')
        if option == 'two':
            return ['aff', 'neg']
        elif option == 'bp':
            return ['og', 'oo', 'cg', 'co']
        else:
            logger.error("Invalid sides option: %s", option)
            return ['aff', 'neg']  # return default, just to keep it going

    @property
    def last_substantive_position(self):
        """Returns the number of substantive speakers."""
        return self.pref('substantive_speakers')

    @property
    def reply_position(self):
        """If there is a reply position, returns one more than the number of
        substantive speakers. If there is no reply position, returns None."""
        if self.pref('reply_scores_enabled'):
            return self.pref('substantive_speakers') + 1
        else:
            return None

    @property
    def positions(self):
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
            from participants.models import Adjudicator
            return Adjudicator.objects.filter(Q(tournament=self) | Q(tournament__isnull=True))
        else:
            return self.adjudicator_set.all()

    @property
    def relevant_venues(self):
        """Convenience property for retrieving venues relevant to the tournament.
        Returns a QuerySet."""
        if self.pref('share_venues'):
            from venues.models import Venue
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

    def rounds_for_nav(self):
        """Returns a round QuerySet suitable for the admin nav bar.
        This currently annotates with motion counts and sorts by stage (preliminary/elimination)."""
        return self.round_set.order_by('-stage', 'seq').annotate(Count('motion'))

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

    @cached_property
    def billable_teams(self):
        return self.team_set.count()


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
    DRAW_ELIMINATION = 'E'
    # Translators: These are choices for the type of draw a round should have.
    DRAW_CHOICES = ((DRAW_RANDOM, _('Random')),
                    (DRAW_MANUAL, _('Manual')),
                    (DRAW_ROUNDROBIN, _('Round-robin')),
                    (DRAW_POWERPAIRED, _('Power-paired')),
                    (DRAW_ELIMINATION, _('Elimination')), )

    STAGE_PRELIMINARY = 'P'
    STAGE_ELIMINATION = 'E'
    STAGE_CHOICES = ((STAGE_PRELIMINARY, _('Preliminary')),
                     (STAGE_ELIMINATION, _('Elimination')), )

    STATUS_NONE = 'N'
    STATUS_DRAFT = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_RELEASED = 'R'
    # Translators: These are choices for the status of the draw for a round.
    STATUS_CHOICES = ((STATUS_NONE, _('None')),
                      (STATUS_DRAFT, _('Draft')),
                      (STATUS_CONFIRMED, _('Confirmed')),
                      (STATUS_RELEASED, _('Released')), )

    objects = RoundManager()

    tournament = models.ForeignKey(Tournament, models.CASCADE, verbose_name=_("tournament"))
    seq = models.IntegerField(verbose_name=_("sequence number"),
        help_text=_("A number that determines the order of the round, should count consecutively from 1 for the first round"))
    name = models.CharField(max_length=40, verbose_name=_("name"), help_text=_("e.g. \"Round 1\""))
    abbreviation = models.CharField(max_length=10, verbose_name=_("abbreviation"), help_text=_("e.g. \"R1\""))
    stage = models.CharField(max_length=1, choices=STAGE_CHOICES, default=STAGE_PRELIMINARY,
        verbose_name=_("stage"),
        help_text=_("Preliminary = inrounds, elimination = outrounds"))
    draw_type = models.CharField(max_length=1, choices=DRAW_CHOICES,
        verbose_name=_("draw type"),
        help_text=_("Which draw method to use"))
    # cascade to avoid break rounds without break categories
    break_category = models.ForeignKey('breakqual.BreakCategory', models.CASCADE, blank=True, null=True,
        verbose_name=_("break category"),
        help_text=_("If elimination round, which break category"))

    draw_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_NONE,
        verbose_name=_("draw status"),
        help_text=_("The status of this round's draw"))

    feedback_weight = models.FloatField(default=0,
        verbose_name=_("feedback weight"),
        # Translator: xgettext:no-python-format
        help_text=_("The extent to which each adjudicator's overall score depends on feedback vs their test score. At 0, it is 100% drawn from their test score, at 1 it is 100% drawn from feedback."))
    silent = models.BooleanField(default=False,
        # Translators: A silent round is a round for which results are not disclosed once the round is over.
        verbose_name=_("silent"),
        help_text=_("If marked silent, information about this round (such as its results) will not be shown publicly."))
    motions_released = models.BooleanField(default=False,
        verbose_name=_("motions released"),
        help_text=_("Whether motions will appear on the public website, assuming that feature is turned on"))
    starts_at = models.TimeField(verbose_name=_("starts at"), blank=True, null=True)

    class Meta:
        verbose_name = _('round')
        verbose_name_plural = _('rounds')
        unique_together = [('tournament', 'seq')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']

    def __str__(self):
        return "[%s] %s" % (self.tournament, self.name)

    def clean(self):
        errors = {}

        # Draw type must be consistent with stage
        if self.stage == Round.STAGE_ELIMINATION and self.draw_type != Round.DRAW_ELIMINATION:
            errors['draw_type'] = ValidationError(_("A round in the elimination stage must have "
                "its draw type set to \"Elimination\"."))
        elif self.stage == Round.STAGE_PRELIMINARY and self.draw_type == Round.DRAW_ELIMINATION:
            errors['draw_type'] = ValidationError(_("A round in the preliminary stage cannot "
                "have its draw type set to \"Elimination\"."))

        # Break rounds must have a break category
        if self.stage == Round.STAGE_ELIMINATION and self.break_category is None:
            errors['break_category'] = ValidationError(_("Elimination rounds must have a break category."))

        if errors:
            raise ValidationError(errors)

    # --------------------------------------------------------------------------
    # Checks for potential errors
    # --------------------------------------------------------------------------

    def duplicate_panellists(self):
        """Returns a QuerySet of adjudicators who are allocated twice in the round."""
        from participants.models import Adjudicator
        return Adjudicator.objects.filter(debateadjudicator__debate__round=self).annotate(
                Count('debateadjudicator')).filter(debateadjudicator__count__gt=1)

    def duplicate_venues(self):
        from venues.models import Venue
        return Venue.objects.filter(debate__round=self).annotate(Count('debate')).filter(
                debate__count__gt=1)

    def num_debates_without_chair(self):
        """Returns the number of debates in the round that lack a chair, or have
        more than one chair."""
        from adjallocation.models import DebateAdjudicator
        debates_in_round = self.debate_set.count()
        debates_with_one_chair = self.debate_set.filter(debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR).annotate(
                num_chairs=Count('debateadjudicator')).filter(num_chairs=1).count()
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
        return debates_with_even_panel

    def num_debates_without_venue(self):
        return self.debate_set.filter(venue__isnull=True).count()

    def num_debates_with_sides_unconfirmed(self):
        return self.debate_set.filter(sides_confirmed=False).count()

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
            related += ('division', 'division__venue_category')
        return self.debate_set.order_by(*ordering).select_related(*related)

    def debate_set_with_prefetches(self, filter_kwargs=None, ordering=('venue__name',),
            teams=True, adjudicators=True, speakers=True, divisions=True, wins=False,
            results=False, venues=True, institutions=False):
        """Returns the debate set, with aff_team and neg_team populated.
        This is basically a prefetch-like operation, except that it also figures
        out which team is on which side, and sets attributes accordingly."""
        from adjallocation.models import DebateAdjudicator
        from draw.models import DebateTeam
        from participants.models import Speaker
        from results.prefetch import populate_confirmed_ballots, populate_wins

        debates = self.debate_set.all()
        if filter_kwargs:
            debates = debates.filter(**filter_kwargs)
        if results:
            debates = debates.prefetch_related('ballotsubmission_set', 'ballotsubmission_set__submitter')
        if adjudicators:
            debates = debates.prefetch_related(
                Prefetch('debateadjudicator_set',
                    queryset=DebateAdjudicator.objects.select_related('adjudicator__institution')),
            )
        if divisions and self.tournament.pref('enable_divisions'):
            debates = debates.select_related('division', 'division__venue_category')
        if venues:
            debates = debates.select_related('venue').prefetch_related('venue__venuecategory_set')

        if teams or wins or institutions or speakers:
            debateteam_prefetch_queryset = DebateTeam.objects.select_related('team')
            if institutions:
                debateteam_prefetch_queryset = debateteam_prefetch_queryset.select_related('team__institution')
            if speakers:
                debateteam_prefetch_queryset = debateteam_prefetch_queryset.prefetch_related(
                    Prefetch('team__speaker_set', queryset=Speaker.objects.order_by('name')))
            debates = debates.prefetch_related(
                Prefetch('debateteam_set', queryset=debateteam_prefetch_queryset))

        if ordering:
            debates = debates.order_by(*ordering)

        # These functions populate relevant attributes of each debate, operating in-place
        if results:
            populate_confirmed_ballots(debates, motions=True, results=True)
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
        """Returns the round that comes before this round. If this is a break
        round, then it returns the latest preceding round that is either in the
        same break category or is a preliminary round."""
        rounds = self.tournament.round_set.filter(seq__lt=self.seq).order_by('-seq')
        if self.is_break_round:
            rounds = rounds.filter(Q(stage=Round.STAGE_PRELIMINARY) | Q(break_category=self.break_category))
        try:
            return rounds.first()
        except Round.DoesNotExist:
            return None

    @property
    def motions_good_for_public(self):
        return self.motions_released or not self.motion_set.exists()
