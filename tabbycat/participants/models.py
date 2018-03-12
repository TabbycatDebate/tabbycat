import logging
from warnings import warn

from django.contrib.contenttypes.fields import GenericRelation
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from utils.managers import LookupByNameFieldsMixin

from .emoji import EMOJI_LIST

logger = logging.getLogger(__name__)


class Region(models.Model):
    name = models.CharField(db_index=True, max_length=100,
        verbose_name=_("name"))

    class Meta:
        verbose_name = _("region")
        verbose_name_plural = _("regions")

    def __str__(self):
        return '%s' % (self.name)

    @property
    def serialize(self):
        return {'name': self.name, 'id': self.id, 'class': None}


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

    @property
    def serialize(self):
        return {'name': self.name, 'id': self.id, 'code': self.code}


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

    @property
    def serialize(self):
        return {'id': self.id, 'name': self.name, 'seq': self.seq}


class Person(models.Model):
    name = models.CharField(max_length=70, db_index=True,
        verbose_name=_("name"))
    email = models.EmailField(blank=True, null=True,
        verbose_name=_("e-mail address"))
    phone = models.CharField(max_length=40, blank=True,
        verbose_name=_("phone"))
    anonymous = models.BooleanField(default=False,
        verbose_name=_("anonymous"),
        help_text=_("Anonymous persons will have their name and team redacted on public tab releases"))

    notes = models.TextField(blank=True, null=True,
        verbose_name=_("notes"))

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

    @property
    def has_contact(self):
        return bool(self.email or self.phone)


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

    short_name = models.CharField(editable=False, max_length=50,
        verbose_name=_("short name"),
        help_text=_("The name shown in the draw, including institution name. (This is autogenerated.)"))
    long_name = models.CharField(editable=False, max_length=200,
        verbose_name=_("long name"),
        help_text=_("The full name of the team, including institution name. (This is autogenerated.)"))

    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True,
        verbose_name=_("institution"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    division = models.ForeignKey('divisions.Division', models.SET_NULL, blank=True, null=True,
        verbose_name=_("division"))
    use_institution_prefix = models.BooleanField(default=False,
        verbose_name=_("Uses institutional prefix"),
        help_text=_("If ticked, a team called \"1\" from Victoria will be shown as \"Victoria 1\""))
    url_key = models.SlugField(blank=True, null=True, unique=True, max_length=24, # uses null=True to allow multiple teams to have no URL key
        verbose_name=_("URL key"))
    break_categories = models.ManyToManyField('breakqual.BreakCategory', blank=True,
        verbose_name=_("break categories"))

    round_availabilities = GenericRelation('availability.RoundAvailability')
    venue_constraints = GenericRelation('venues.VenueConstraint', related_query_name='team',
            content_type_field='subject_content_type', object_id_field='subject_id')

    TYPE_NONE = 'N'
    TYPE_SWING = 'S'
    TYPE_COMPOSITE = 'C'
    TYPE_BYE = 'B'
    TYPE_CHOICES = ((TYPE_NONE, _("none")),
                    (TYPE_SWING, _("swing")),
                    (TYPE_COMPOSITE, _("composite")),
                    (TYPE_BYE, _("bye")), )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_NONE,
        verbose_name=_("type"))

    emoji = models.CharField(max_length=2, blank=True, null=True, default=None, choices=EMOJI_LIST, # uses null=True to allow multiple teams to have no emoji
        verbose_name=_("emoji"))

    construct_emoji = None # historical reference for migration 0026_auto_20170416_2332

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
                short_name += " " + reference
            return short_name
        else:
            return reference

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
        institution = self.get_cached_institution()
        if institution is None:
            return None
        return institution.region

    @property
    def break_categories_nongeneral(self):
        return self.break_categories.exclude(is_general=True)

    @property
    def break_categories_str(self):
        categories = self.break_categories_nongeneral
        return ", ".join(c.name for c in categories) if categories else ""

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
        try:
            return self._wins_count
        except AttributeError:
            from results.models import TeamScore
            self._wins_count = TeamScore.objects.filter(ballot_submission__confirmed=True,
                    debate_team__team=self, win=True).count()
            return self._wins_count

    @property
    def points_count(self):
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
        Always returns False if this team has no instititution."""
        return self.institution_id is not None and self.institution_id == other.institution_id

    def prev_debate(self, round_seq):
        from draw.models import DebateTeam
        try:
            return DebateTeam.objects.filter(
                debate__round__seq__lt=round_seq,
                team=self, ).order_by('-debate__round__seq')[0].debate
        except IndexError:
            return None

    def get_cached_institution(self):
        cached_key = "%s_%s_%s" % ('teamid', self.id, '_institution__object')
        cached_value = cache.get(cached_key)
        if cached_value:
            return cache.get(cached_key)
        else:
            cached_value = self.institution
            cache.set(cached_key, cached_value, None)
            return cached_value

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

    def serialize(self):
        team = {'id': self.id, 'short_name': self.short_name, 'long_name': self.long_name}
        team['emoji'] = self.emoji
        team['conflicts'] = {'clashes': [], 'histories': []}
        team['institution'] = self.institution.serialize if self.institution else None
        team['region'] = self.region.serialize if self.region else None
        team['speakers'] = [{'name': s.name, 'id': s.id, 'gender': s.gender} for s in self.speakers]
        break_categories = self.break_categories.all()
        team['break_categories'] = [bc.serialize for bc in break_categories] if break_categories else None
        team['highlights'] = {'region': False, 'gender': False, 'category': False}
        team['wins'] = self.wins_count
        team['points'] = self.points_count
        return team


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

    def serialize(self):
        speaker = {'id': self.id, 'name': self.name, 'team': self.team.short_name}
        speaker['institution'] = self.institution.serialize if self.institution else None
        return speaker


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
    test_score = models.FloatField(default=0,
        verbose_name=_("test score"))
    url_key = models.SlugField(blank=True, null=True, unique=True, max_length=24, # uses null=True to allow multiple teams to have no URL key
        verbose_name=_("URL key"))

    institution_conflicts = models.ManyToManyField('Institution',
        through='adjallocation.AdjudicatorInstitutionConflict',
        related_name='adj_inst_conflicts',
        verbose_name=_("institution conflicts"))
    conflicts = models.ManyToManyField('Team',
        through='adjallocation.AdjudicatorConflict',
        related_name='adj_adj_conflicts',
        verbose_name=_("team conflicts"))

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

    def _populate_conflict_cache(self):
        if not getattr(self, '_conflicts_populated', False):
            logger.debug("Populating conflict cache for %s", self)
            self._team_conflict_cache = [c.team_id
                    for c in self.adjudicatorconflict_set.all()]
            self._adjudicator_conflict_cache = [c.conflict_adjudicator_id
                    for c in self.adjudicatoradjudicatorconflict_source_set.all()]
            self._institution_conflict_cache = [c.institution_id
                    for c in self.adjudicatorinstitutionconflict_set.all()]
            self._conflicts_populated = True

    def conflicts_with_team(self, team):
        self._populate_conflict_cache()
        return team.id in self._team_conflict_cache or team.institution_id in self._institution_conflict_cache

    def conflicts_with_adj(self, adj):
        self._populate_conflict_cache()
        adj._populate_conflict_cache()
        if adj.id in self._adjudicator_conflict_cache:
            return True
        if adj.institution_id in self._institution_conflict_cache:
            return True
        if self.id in adj._adjudicator_conflict_cache:
            return True
        if self.institution_id in adj._institution_conflict_cache:
            return True
        return False

    @property
    def is_unaccredited(self):
        return self.novice

    @property
    def region(self):
        return self.institution.region if self.institution else None

    def weighted_score(self, feedback_weight):
        feedback_score = self._feedback_score()
        if feedback_score is None:
            feedback_score = 0
            feedback_weight = 0
        return self.test_score * (1 - feedback_weight) + (feedback_weight * feedback_score)

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
            self._feedback_score_cache = self.adjudicatorfeedback_set.filter(confirmed=True).exclude(
                source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE).aggregate(
                    avg=models.Avg('score'))['avg']
            return self._feedback_score_cache

    @property
    def feedback_score(self):
        return self._feedback_score() or None

    def get_feedback(self):
        return self.adjudicatorfeedback_set.all()

    def seen_team(self, team, before_round=None):
        from draw.models import DebateTeam
        if not hasattr(self, '_seen_team_cache'):
            self._seen_team_cache = {}
        if before_round not in self._seen_team_cache:
            logger.debug("Populating seen team cache for %s", self)
            qs = DebateTeam.objects.filter(debate__debateadjudicator__adjudicator=self)
            if before_round is not None:
                qs = qs.filter(debate__round__seq__lt=before_round.seq)
            self._seen_team_cache[before_round] = [dt.team_id for dt in qs]
        return self._seen_team_cache[before_round].count(team.id)

    def seen_adjudicator(self, adj, before_round=None):
        from adjallocation.models import DebateAdjudicator
        if not hasattr(self, '_seen_adjudicator_cache'):
            self._seen_adjudicator_cache = {}
        if before_round not in self._seen_adjudicator_cache:
            logger.debug("Populating seen adjudicator cache for %s", self)
            qs = DebateAdjudicator.objects.filter(
                debate__debateadjudicator__adjudicator=self).exclude(adjudicator=self)
            if before_round is not None:
                qs = qs.filter(debate__round__seq__lt=before_round.seq)
            self._seen_adjudicator_cache[before_round] = [da.adjudicator_id for da in qs]
        return self._seen_adjudicator_cache[before_round].count(adj.id)

    def serialize(self, round):
        adj = {'id': self.id, 'name': self.name, 'gender': self.gender, 'locked': False}
        adj['conflicts'] = {'clashes': [], 'histories': []}
        adj['score'] = "{0:0.1f}".format(self.weighted_score(round.feedback_weight))
        adj['region'] = self.region.serialize if self.region else None
        adj['institution'] = self.institution.serialize if self.institution else None
        adj['highlights'] = {'region': False, 'gender': False, 'category': False}
        return adj
