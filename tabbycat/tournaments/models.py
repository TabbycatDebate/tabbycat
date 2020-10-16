import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from participants.models import Person
from utils.managers import LookupByNameFieldsMixin

logger = logging.getLogger(__name__)


PROHIBITED_TOURNAMENT_SLUGS = [
    'jet', 'database', 'admin', 'accounts', 'summernote',  # System
    'start', 'create', 'load-demo', # Setup Wizards
    'tournament', 'notifications', 'archive', 'api', # Cross-Tournament app's view roots
    'favicon.ico', 'robots.txt',  # Files that must be at top level
    '__debug__', 'static', 'donations', 'style', 'i18n', 'jsi18n']  # Misc


def validate_tournament_slug(value):
    if value in PROHIBITED_TOURNAMENT_SLUGS:
        raise ValidationError(_("You can't use this as a tournament slug, "
            "because it's reserved for a Tabbycat system URL. Please try "
            "another one."))


class Tournament(models.Model):
    name = models.CharField(max_length=100,
        verbose_name=_("name"),
        help_text=_("The full name, e.g. \"Australasian Intervarsity Debating Championships 2016\""))
    short_name = models.CharField(max_length=25, blank=True, default="",
        verbose_name=_("short name"),
        help_text=_("The name used in the menu, e.g. \"Australs 2016\""))
    seq = models.IntegerField(blank=True, null=True,
        verbose_name=_("sequence number"),
        help_text=_("A number that determines the relative order in which tournaments are displayed on the homepage."))
    slug = models.SlugField(unique=True, validators=[validate_tournament_slug],
        verbose_name=_("slug"),
        help_text=_("The sub-URL of the tournament, cannot have spaces, e.g. \"australs2016\""))
    active = models.BooleanField(verbose_name=_("active"), default=True)

    class Meta:
        verbose_name = _('tournament')
        verbose_name_plural = _('tournaments')
        ordering = ['seq']

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

    def ballots_per_debate(self, stage):
        """Returns the 'ballots per debate' setting for the stage of the
        tournament given. Callers can use this to avoid querying the round's
        tournament repeatedly."""
        if stage == Round.STAGE_PRELIMINARY:
            return self.pref('ballots_per_debate_prelim')
        elif stage == Round.STAGE_ELIMINATION:
            return self.pref('ballots_per_debate_elim')
        else:
            raise ValueError("Unrecognized stage: %r" % (stage,))

    def integer_scores(self, stage):
        """Returns True if all total speaker scores will be integers, at least
        according to tournament preferences. Callers should still check that
        the value in question is in fact an integer before casting."""
        if self.ballots_per_debate(stage) == 'per-adj':
            return False
        if not self.pref('score_step').is_integer():
            return False
        if (self.pref('reply_scores_enabled') and
                not self.pref('reply_score_step').is_integer()):
            return False
        return True

    # --------------------------------------------------------------------------
    # Permalinks
    # --------------------------------------------------------------------------

    def get_absolute_url(self):
        return reverse('tournament-admin-home', kwargs={'tournament_slug': self.slug})

    def get_public_url(self):
        return reverse('tournament-public-index', kwargs={'tournament_slug': self.slug})

    # --------------------------------------------------------------------------
    # Convenience querysets
    # --------------------------------------------------------------------------

    @property
    def relevant_adjudicators(self):
        """Convenience property for retrieving adjudicators relevant to the tournament.
        Returns a QuerySet."""
        return self.adjudicator_set.all()

    @property
    def relevant_venues(self):
        """Convenience property for retrieving venues relevant to the tournament.
        Returns a QuerySet."""
        return self.venue_set.all()

    @property
    def participants(self):
        """Convenience function for retrieving all participants. Returns a QuerySet."""
        return Person.objects.filter(Q(adjudicator__tournament=self) | Q(speaker__team__tournament=self))

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
        """Returns a Round QuerySet suitable for the admin nav bar.
        This annotates the QuerySet with information used to determine bubble
        colours in the admin nav bar."""

        rounds = self.round_set.order_by('-stage', 'seq').annotate(
            Count('motion'), Count('debate'),
        ).select_related('break_category')
        categories_where_current_found = []
        prelim_current_found = False

        # Do this in bulk for performance. This should be kept consistent with
        # Round.is_current and Tournament.current_rounds.
        for r in rounds:
            if r.completed or prelim_current_found:
                r._is_current = False
            elif not r.is_break_round:
                r._is_current = True
                prelim_current_found = True
            elif r.debate__count > 0 and r.break_category not in categories_where_current_found:
                categories_where_current_found.append(r.break_category)
                r._is_current = True
            else:
                r._is_current = False

        return rounds

    @cached_property
    def adj_feedback_questions(self):
        return self.adjudicatorfeedbackquestion_set.order_by("seq")

    def break_categories_nongeneral(self):
        return self.breakcategory_set.exclude(is_general=True)

    # --------------------------------------------------------------------------
    # Cached
    # --------------------------------------------------------------------------

    @cached_property
    def rounds_with_released_results(self):
        if self.pref('all_results_released'):
            return self.round_set.all()
        else:
            return self.round_set.filter(completed=True, silent=False)

    @cached_property
    def current_round(self):
        current = self.round_set.filter(completed=False).order_by('seq').first()
        if current is None:
            return self.round_set.order_by('seq').last()
        return current

    @cached_property
    def current_rounds(self):
        """List of all current rounds with existent draws. If a preliminary
        round is the earliest non-completed round, then that's the only current
        round. If all preliminary rounds are completed, then the earliest
        non-completed round with an existent draw in each category is a current
        round, and they're listed in the `seq` order of the break categories.

        This should be kept consistent with Tournament.rounds_for_nav and
        Round.is_current."""

        # For something this complicated it's easier just to get the entire
        # round set from the database, and process it in Python.
        rounds = getattr(self, 'current_round_set',
            self.round_set.filter(completed=False).annotate(Count('debate')).order_by('seq'))
        current_elim_rounds = {}
        for r in rounds:
            if not r.is_break_round:
                return [r]  # short-circuit everything else
            elif r.debate__count > 0:
                current_elim_rounds.setdefault(r.break_category_id, r)
        return [
            current_elim_rounds.get(category.pk)
            for category in self.breakcategory_set.order_by('seq')  # Order by break, then seq
            if category.pk in current_elim_rounds
        ]

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

    @cached_property
    def public_draws_available(self):
        """Returns True if draws are available for public viewing. Used in
        public navigation menus."""
        return any(r.draw_status == Round.STATUS_RELEASED for r in self.current_rounds)


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
    DRAW_CHOICES = (
        (DRAW_RANDOM, _('Random')),
        (DRAW_MANUAL, _('Manual')),
        (DRAW_ROUNDROBIN, _('Round-robin')),
        (DRAW_POWERPAIRED, _('Power-paired')),
        (DRAW_ELIMINATION, _('Elimination')),
    )

    STAGE_PRELIMINARY = 'P'
    STAGE_ELIMINATION = 'E'
    STAGE_CHOICES = (
        (STAGE_PRELIMINARY, _('Preliminary')),
        (STAGE_ELIMINATION, _('Elimination')),
    )

    STATUS_NONE = 'N'
    STATUS_DRAFT = 'D'
    STATUS_CONFIRMED = 'C'
    STATUS_RELEASED = 'R'
    # Translators: These are choices for the status of the draw for a round.
    STATUS_CHOICES = (
        (STATUS_NONE, _('None')),
        (STATUS_DRAFT, _('Draft')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_RELEASED, _('Released')),
    )

    objects = RoundManager()

    tournament = models.ForeignKey(Tournament, models.CASCADE, verbose_name=_("tournament"))
    seq = models.PositiveIntegerField(verbose_name=_("sequence number"),
        help_text=_("A number that determines the order of the round, should count consecutively from 1 for the first round"))
    completed = models.BooleanField(default=False,
        verbose_name=_("completed"),
        help_text=_("True if the round is over, which normally means all results have been entered and confirmed"))

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
        help_text=_("The extent to which each adjudicator's overall score depends on feedback vs their base score. At 0, it is 100% drawn from their base score, at 1 it is 100% drawn from feedback."))
    silent = models.BooleanField(default=False,
        # Translators: A silent round is a round for which results are not disclosed once the round is over.
        verbose_name=_("silent"),
        help_text=_("If marked silent, information about this round (such as its results) will not be shown publicly."))
    motions_released = models.BooleanField(default=False,
        verbose_name=_("motions released"),
        help_text=_("Whether motions will appear on the public website, assuming that feature is turned on"))
    starts_at = models.TimeField(verbose_name=_("starts at"), blank=True, null=True)

    weight = models.IntegerField(default=1,
        verbose_name=_("weight"),
        help_text=_("A factor for the points received in the round. For example, if 2, all points are doubled."))

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

    @cached_property
    def duplicate_panellists(self):
        """Returns a QuerySet of adjudicators who are allocated twice in the round."""
        from participants.models import Adjudicator
        return Adjudicator.objects.filter(debateadjudicator__debate__round=self).annotate(
                Count('debateadjudicator')).filter(debateadjudicator__count__gt=1)

    @cached_property
    def duplicate_venues(self):
        """Returns a QuerySet of venues that are allocated twice in the round."""
        from venues.models import Venue
        return Venue.objects.filter(debate__round=self).annotate(Count('debate')).filter(
                debate__count__gt=1)

    @cached_property
    def duplicate_team_names(self):
        """Returns a list of names of those teams allocated twice in the round."""
        from participants.models import Team
        return Team.objects.filter(debateteam__debate__round=self).annotate(
            Count('debateteam')).filter(debateteam__count__gt=1).values_list('short_name', flat=True)

    @cached_property
    def num_debates_without_chair(self):
        """Returns the number of debates in the round that lack a chair, or have
        more than one chair."""
        from adjallocation.models import DebateAdjudicator
        debates_in_round = self.debate_set.count()
        debates_with_one_chair = self.debate_set.filter(debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR).annotate(
                num_chairs=Count('debateadjudicator')).filter(num_chairs=1).count()
        return debates_in_round - debates_with_one_chair

    @cached_property
    def num_debates_with_even_panel(self):
        """Returns the number of debates in the round, in which there are an
        positive and even number of voting judges."""
        from adjallocation.models import DebateAdjudicator
        debateadj_filter = ~Q(debateadjudicator__type=DebateAdjudicator.TYPE_TRAINEE)
        debates_with_even_panel = self.debate_set.annotate(
            panellists=Count('debateadjudicator', filter=debateadj_filter),
            odd_panellists=Count('debateadjudicator', filter=debateadj_filter) % 2,
        ).filter(panellists__gt=0, odd_panellists=0).count()
        return debates_with_even_panel

    @cached_property
    def num_debates_without_venue(self):
        return self.debate_set.filter(venue__isnull=True).count()

    @cached_property
    def num_debates_with_sides_unconfirmed(self):
        return self.debate_set.filter(sides_confirmed=False).count()

    @cached_property
    def unavailable_adjudicators_allocated(self):
        """Returns the number of adjudicators who are allocated but not available."""
        from participants.models import Adjudicator
        return Adjudicator.objects.filter(debateadjudicator__debate__round=self).exclude(
            round_availabilities__round=self)

    @cached_property
    def num_available_adjudicators_not_allocated(self):
        """Returns the number of adjudicators who are available but not allocated."""
        from participants.models import Adjudicator
        return Adjudicator.objects.exclude(debateadjudicator__debate__round=self).filter(
            round_availabilities__round=self).count()

    # --------------------------------------------------------------------------
    # Draw retrieval methods
    # --------------------------------------------------------------------------

    def debate_set_with_prefetches(self, filter_kwargs=None, ordering=('venue__name',),
            teams=True, adjudicators=True, speakers=True, wins=False,
            results=False, venues=True, institutions=False, check_ins=False, iron=False):
        """Returns the debate set, with aff_team and neg_team populated.
        This is basically a prefetch-like operation, except that it also figures
        out which team is on which side, and sets attributes accordingly."""
        from adjallocation.models import DebateAdjudicator
        from draw.models import DebateTeam
        from participants.models import Speaker
        from results.prefetch import populate_confirmed_ballots, populate_wins, populate_checkins

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
        if venues:
            debates = debates.select_related('venue').prefetch_related('venue__venuecategory_set')
        if check_ins:
            debates = debates.select_related('checkin_identifier')

        if teams or wins or institutions or speakers or iron:
            debateteam_prefetch_queryset = DebateTeam.objects.select_related('team')
            if institutions:
                debateteam_prefetch_queryset = debateteam_prefetch_queryset.select_related('team__institution')
            if speakers:
                debateteam_prefetch_queryset = debateteam_prefetch_queryset.prefetch_related(
                    Prefetch('team__speaker_set', queryset=Speaker.objects.order_by('name')))
            if iron:
                debateteam_prefetch_queryset = debateteam_prefetch_queryset.annotate(
                    iron=Count('speakerscore', filter=Q(
                        speakerscore__ghost=True,
                        speakerscore__ballot_submission__confirmed=True,
                    ), distinct=True),
                    iron_prev=Count('team__debateteam__speakerscore', filter=Q(
                        team__debateteam__speakerscore__ghost=True,
                        team__debateteam__speakerscore__ballot_submission__confirmed=True,
                        team__debateteam__debate__round=self.prev,
                    ), distinct=True),
                )

            debates = debates.prefetch_related(
                Prefetch('debateteam_set', queryset=debateteam_prefetch_queryset))

        if ordering:
            debates = debates.order_by(*ordering)

        # These functions populate relevant attributes of each debate, operating in-place
        if results:
            populate_confirmed_ballots(debates, motions=True, results=True)
        if wins:
            populate_wins(debates)
        if check_ins:
            populate_checkins(debates, self.tournament)

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

    def _rounds_in_same_sequence(self):
        rounds = self.tournament.round_set.all()
        if self.is_break_round:
            rounds = rounds.filter(Q(stage=Round.STAGE_PRELIMINARY) | Q(break_category=self.break_category))
        return rounds

    @cached_property
    def prev(self):
        """Returns the round that comes before this round. If this is a break
        round, then it returns the latest preceding round that is either in the
        same break category or is a preliminary round."""
        return self._rounds_in_same_sequence().filter(seq__lt=self.seq).order_by('seq').last()

    @cached_property
    def next(self):
        """Returns the round that comes after this round. If this is a break
        round, then it returns the next round that is either in the same break
        category or is a preliminary round."""
        return self._rounds_in_same_sequence().filter(seq__gt=self.seq).order_by('seq').first()

    @cached_property
    def is_last(self):
        """Returns a boolean if no next round in the sequence exists."""
        return not self._rounds_in_same_sequence().filter(seq__gt=self.seq).order_by('seq').exists()

    @cached_property
    def is_break_round(self):
        return self.stage == self.STAGE_ELIMINATION

    @property
    def is_current(self):
        """Returns True if this round is a current round."""
        # For performance, self._is_current may be set by Tournament.rounds_for_nav,
        # which should be kept consistent with this implementation.
        # This should also be kept consistent with Tournament.current_rounds.
        if not hasattr(self, '_is_current'):
            if self.completed:
                self._is_current = False
            elif self._rounds_in_same_sequence().filter(seq__lt=self.seq, completed=False).exists():
                self._is_current = False
            elif self.is_break_round and not self.debate_set.exists():
                self._is_current = False
            else:
                self._is_current = True
        return self._is_current

    @property
    def motions_good_for_public(self):
        return self.motions_released or not self.motion_set.exists()

    @property
    def ballots_per_debate(self):
        return self.tournament.ballots_per_debate(self.stage)
