import logging
from warnings import warn

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from utils.managers import LookupByNameFieldsMixin

from .emoji import EMOJI_FIELD_CHOICES

logger = logging.getLogger(__name__)


class Region(models.Model):
    name = models.CharField(db_index=True, max_length=100,
        verbose_name=_("name"))

    class Meta:
        verbose_name = _("region")
        verbose_name_plural = _("regions")

    def __str__(self):
        return '%s' % (self.name)


class InstitutionManager(LookupByNameFieldsMixin, models.Manager):
    name_fields = ['code', 'name']


class Institution(models.Model):
    name = models.CharField(max_length=100,
        verbose_name=_("name"),
        # Translators: Change the examples to institutions native to your language; keep consistent between strings
        help_text=_("The institution's full name, e.g., \"University of Cambridge\", \"Victoria University of Wellington\""))
    code = models.CharField(max_length=20,
        verbose_name=_("code"),
        # Translators: Change the examples to institutions native to your language; keep consistent between strings
        help_text=_("What the institution is typically called for short, e.g., \"Cambridge\", \"Vic Wellington\""))
    region = models.ForeignKey(Region, models.SET_NULL, blank=True, null=True,
        verbose_name=_("region"))

    venue_constraints = GenericRelation('venues.VenueConstraint', related_query_name='institution',
            content_type_field='subject_content_type', object_id_field='subject_id')

    objects = InstitutionManager()

    class Meta:
        unique_together = [('name', 'code')]
        ordering = ['name']
        verbose_name = _("institution")
        verbose_name_plural = _("institutions")

    def __str__(self):
        return str(self.name)


class SpeakerCategory(models.Model):
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    name = models.CharField(max_length=50,
        verbose_name=_("name"),
        # Translators: Translate ESL to the acronym for "<target language> as a second/foreign language", not "English"
        help_text=_("Name to be displayed, e.g., \"Novice\", \"ESL\""))
    slug = models.SlugField(
        verbose_name=_("slug"),
        # Translators: Translate esl to the acronym for "<target language> as a second/foreign language", not "English"
        help_text=_("Slug for URLs, e.g., \"novice\", \"esl\""))
    seq = models.IntegerField(
        verbose_name=_("sequence number"),
        help_text=_("The order in which the categories are displayed"))
    limit = models.IntegerField(default=0,
        verbose_name=_("limit"),
        help_text=_("At most this many speakers will be shown on the public tab for this category, or use 0 for no limit"))
    public = models.BooleanField(default=True,
        verbose_name=_("public"),
        help_text=_("If checked, this category will be included in the speaker category tabs shown to the public"))

    class Meta:
        unique_together = [('tournament', 'seq'), ('tournament', 'slug')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']
        verbose_name = _("speaker category")
        verbose_name_plural = _("speaker categories")

    def __str__(self):
        return "[{}] {}".format(self.tournament.slug, self.name)


class Person(models.Model):
    name = models.CharField(max_length=70, db_index=True,
        verbose_name=_("name"))
    email = models.EmailField(blank=True, null=True,
        verbose_name=_("email address"))
    phone = models.CharField(max_length=40, blank=True,
        verbose_name=_("phone"))
    anonymous = models.BooleanField(default=False,
        verbose_name=_("anonymous"),
        help_text=_("Anonymous persons will have their name and team redacted on public tab releases"))

    url_key = models.SlugField(blank=True, null=True, unique=True, max_length=24, # uses null=True to allow multiple people to have no URL key
        verbose_name=_("URL key"))

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = ((GENDER_MALE,   _("male")),
                      (GENDER_FEMALE, _("female")),
                      (GENDER_OTHER,  _("other")))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True,
        verbose_name=_("gender"),
        help_text=_("Gender is displayed in the adjudicator allocation interface, and nowhere else"))
    pronoun = models.CharField(max_length=10, blank=True,
        verbose_name=_("pronoun"),
        help_text=_("If printing ballots using Tabbycat, there is the option to pre-print pronouns"))

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self):
        return str(self.name)


class TeamManager(LookupByNameFieldsMixin, models.Manager):
    name_fields = ['short_name', 'long_name']

    def get_queryset(self):
        return super().get_queryset().select_related('institution')


class Team(models.Model):
    reference = models.CharField(blank=True, max_length=150,
        verbose_name=_("full name/suffix"),
        help_text=_("Do not include institution name (see \"uses institutional prefix\" below)"))
    short_reference = models.CharField(blank=True, max_length=35,
        verbose_name=_("short name/suffix"),
        help_text=_("The name shown in the draw. Do not include institution name (see \"uses institutional prefix\" below)"))
    code_name = models.CharField(blank=True, max_length=150,
        verbose_name=_("code name"),
        help_text=_("Name used to obscure institutional identity on public-facing pages"))

    short_name = models.CharField(editable=False, max_length=20+1+35,  # Max institution code + space + short_reference max
        verbose_name=_("short name"),
        help_text=_("The name shown in the draw, including institution name. (This is autogenerated.)"))
    long_name = models.CharField(editable=False, max_length=100+1+150,  # Max institution name + space + reference max
        verbose_name=_("long name"),
        help_text=_("The full name of the team, including institution name. (This is autogenerated.)"))

    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True,
        verbose_name=_("institution"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    use_institution_prefix = models.BooleanField(default=False,
        verbose_name=_("Uses institutional prefix"),
        help_text=_("If ticked, a team called \"1\" from Victoria will be shown as \"Victoria 1\""))
    break_categories = models.ManyToManyField('breakqual.BreakCategory', blank=True,
        verbose_name=_("break categories"))

    institution_conflicts = models.ManyToManyField('Institution',
        through='adjallocation.TeamInstitutionConflict',
        related_name='team_inst_conflicts',
        verbose_name=_("institution conflicts"))

    round_availabilities = GenericRelation('availability.RoundAvailability')
    venue_constraints = GenericRelation('venues.VenueConstraint', related_query_name='team',
            content_type_field='subject_content_type', object_id_field='subject_id')

    TYPE_NONE = 'N'
    TYPE_SWING = 'S'
    TYPE_COMPOSITE = 'C'
    TYPE_BYE = 'B'
    TYPE_CHOICES = (
        (TYPE_NONE, _("none")),
        (TYPE_SWING, _("swing")),
        (TYPE_COMPOSITE, _("composite")),
        (TYPE_BYE, _("bye")),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_NONE,
        verbose_name=_("type"))

    emoji = models.CharField(max_length=3, default=None, choices=EMOJI_FIELD_CHOICES,
        blank=True, null=True,   # uses null=True to allow multiple teams to have no emoji
        verbose_name=_("emoji"))

    class Meta:
        unique_together = [
            # Enforce for blank references also - two teams from the same
            # institution can't both be unlabelled. However, Django won't
            # enforce this for null institutions.
            ('reference', 'institution', 'tournament'),

            # Not enforced for blank emoji (null=True is set on emoji)
            ('emoji', 'tournament'),
        ]
        ordering = ['tournament', 'institution', 'short_reference']
        index_together = ['tournament', 'institution', 'short_reference']
        verbose_name = _("team")
        verbose_name_plural = _("teams")

    objects = TeamManager()

    def __str__(self):
        return "[{}] {}".format(self.tournament.slug, self.short_name)

    def _construct_short_name(self):
        institution = self.institution
        reference = self.short_reference or self.reference
        if self.use_institution_prefix and institution is not None:
            short_name = institution.code
            if reference:
                short_name += " " + str(reference)[:35]
            return short_name
        else:
            return str(reference)[:20+1+35]

    def _construct_long_name(self):
        institution = self.institution
        if self.use_institution_prefix and institution is not None:
            long_name = institution.name
            if self.reference:
                long_name += " " + self.reference
            return long_name
        else:
            return self.reference

    @property
    def region(self):
        return self.institution.region if self.institution else None

    def break_rank_for_category(self, category):
        from breakqual.models import BreakingTeam
        try:
            bt = BreakingTeam.objects.get(break_category=category, team=self)
        except BreakingTeam.DoesNotExist:
            return None
        return bt.break_rank

    def get_debates(self, before_round):
        dts = self.debateteam_set.select_related('debate').order_by(
            'debate__round__seq')
        if before_round is not None:
            dts = dts.filter(debate__round__seq__lt=before_round)
        return [dt.debate for dt in dts]

    @property
    def debates(self):
        return self.get_debates(None)

    @property
    def wins_count(self):
        """Callers using this property for many teams should prefetch them
        using `populate_win_counts()` in the `participants.prefetch` module."""
        try:
            return self._wins_count
        except AttributeError:
            from results.models import TeamScore
            self._wins_count = TeamScore.objects.filter(ballot_submission__confirmed=True,
                    debate_team__team=self, win=True).count()
            return self._wins_count

    @property
    def points_count(self):
        """Callers using this property for many teams should prefetch them
        using `populate_win_counts()` in the `participants.prefetch` module.
        (That's not a typo -- that function populates both `_wins_count` and
        `_points`.)"""
        try:
            return self._points
        except AttributeError:
            from results.models import TeamScore
            self._points = TeamScore.objects.filter(ballot_submission__confirmed=True,
                    debate_team__team=self).aggregate(Sum('points'))['points__sum']
            return self._points

    @cached_property
    def speakers(self):
        return self.speaker_set.all()

    def seen(self, other, before_round=None):
        queryset = self.debateteam_set.filter(debate__debateteam__team=other)
        if before_round:
            queryset = queryset.filter(debate__round__seq__lt=before_round)
        return queryset.count()

    def same_institution(self, other):
        """Returns True if this team and `other` are from the same institution.
        Always returns False if this team has no institution."""
        return self.institution_id is not None and self.institution_id == other.institution_id

    def prev_debate(self, round_seq):
        from draw.models import DebateTeam
        try:
            return DebateTeam.objects.filter(
                debate__round__seq__lt=round_seq,
                team=self).order_by('-debate__round__seq')[0].debate
        except IndexError:
            return None

    def clean(self):
        # Require reference and short_reference if use_institution_prefix is False
        errors = {}
        if self.use_institution_prefix and self.institution is None:
            errors['institution'] = _("Teams must have an institution if they are using the institutional prefix.")
        if not self.use_institution_prefix and not self.reference:
            errors['reference'] = _("Teams must have a full name if they don't use the institutional prefix.")
        if not self.use_institution_prefix and not self.short_reference:
            errors['short_reference'] = _("Teams must have a short name if they don't use the institutional prefix.")
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Override the short and long names before saving
        self.short_name = self._construct_short_name()
        self.long_name = self._construct_long_name()
        super().save(*args, **kwargs)


class Speaker(Person):
    team = models.ForeignKey(Team, models.CASCADE,
        verbose_name=_("team"))
    categories = models.ManyToManyField(SpeakerCategory, blank=True,
        verbose_name=_("speaker categories"))

    class Meta:
        verbose_name = _("speaker")
        verbose_name_plural = _("speakers")

    def __str__(self):
        return str(self.name)

    @property
    def tournament(self):
        return self.team.tournament


class AdjudicatorManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(AdjudicatorManager, self).get_queryset().select_related('institution')


class Adjudicator(Person):
    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True,
        verbose_name=_("institution"))
    # cascade to avoid unattached adjudicator pollution when deleting tournaments
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE, blank=True, null=True,
        verbose_name=_("tournament"),
        help_text=_("Adjudicators not assigned to any tournament can be shared between tournaments"))
    base_score = models.FloatField(default=0,
        verbose_name=_("base score"))

    institution_conflicts = models.ManyToManyField('Institution',
        through='adjallocation.AdjudicatorInstitutionConflict',
        related_name='adj_inst_conflicts',
        verbose_name=_("institution conflicts"))
    team_conflicts = models.ManyToManyField('Team',
        through='adjallocation.AdjudicatorTeamConflict',
        related_name='adj_team_conflicts',
        verbose_name=_("team conflicts"))
    adjudicator_conflicts = models.ManyToManyField('Adjudicator',
        through='adjallocation.AdjudicatorAdjudicatorConflict',
        related_name='adj_adj_conflicts',
        verbose_name=_("adjudicator conflicts"))

    trainee = models.BooleanField(default=False,
        verbose_name=_("always trainee"),
        help_text=_("If checked, this adjudicator will never be auto-allocated a voting position, regardless of their score"))
    breaking = models.BooleanField(default=False,
        verbose_name=_("breaking"))
    independent = models.BooleanField(default=False, blank=True,
        verbose_name=_("independent"))
    adj_core = models.BooleanField(default=False, blank=True,
        verbose_name=_("adjudication core"))

    round_availabilities = GenericRelation('availability.RoundAvailability')
    venue_constraints = GenericRelation('venues.VenueConstraint', related_query_name='adjudicator',
            content_type_field='subject_content_type', object_id_field='subject_id')

    objects = AdjudicatorManager()

    class Meta:
        verbose_name = _("adjudicator")
        verbose_name_plural = _("adjudicators")

    def __str__(self):
        if self.institution is None:
            return self.name
        else:
            return "%s (%s)" % (self.name, self.institution.code)

    @property
    def region(self):
        return self.institution.region if self.institution else None

    def weighted_score(self, feedback_weight):
        feedback_score = self._feedback_score()
        if feedback_score is None:
            feedback_score = 0
            feedback_weight = 0
        return self.base_score * (1 - feedback_weight) + (feedback_weight * feedback_score)

    @cached_property
    def score(self):
        warn("Adjudicator.score is inefficient; consider using Adjudicator.weighted_score() instead.", stacklevel=2)
        if self.tournament:
            weight = self.tournament.current_round.feedback_weight
        else:
            weight = 1  # For shared ajudicators
        return self.weighted_score(weight)

    def _feedback_score(self):
        try:
            return self._feedback_score_cache
        except AttributeError:
            from adjallocation.models import DebateAdjudicator
            self._feedback_score_cache = self.adjudicatorfeedback_set.filter(confirmed=True, ignored=False).exclude(
                source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE).aggregate(
                    avg=models.Avg('score'))['avg']
            return self._feedback_score_cache

    @property
    def feedback_score(self):
        return self._feedback_score() or None

    def get_feedback(self):
        return self.adjudicatorfeedback_set.all()
