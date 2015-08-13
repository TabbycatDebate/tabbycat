from django.db import models
from django.utils.functional import cached_property
from django.db.models import signals
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from django.core.cache import cache
from django.utils.functional import cached_property

class Region(models.Model):
    name = models.CharField(db_index=True, max_length=100)
    tournament = models.ForeignKey('debate.Tournament')

    def __unicode__(self):
        return u'%s' % (self.name)

class InstitutionManager(models.Manager):

    def lookup(self, name, **kwargs):
        """Queries for an institution with matching name in any of the three
        name fields."""
        for field in ('code', 'name', 'abbreviation'):
            try:
                kwargs[field] = name
                return self.get(**kwargs)
            except ObjectDoesNotExist:
                kwargs.pop(field)
        raise self.model.DoesNotExist("No institution matching '%s'" % name)

class Institution(models.Model):
    name = models.CharField(db_index=True, max_length=100, help_text="The institution's full name, e.g., \"University of Cambridge\", \"Victoria University of Wellington\"")
    code = models.CharField(max_length=20, help_text="What the institution is typically called for short, e.g., \"Cambridge\", \"Vic Wellington\"")
    abbreviation = models.CharField(max_length=8, default="", help_text="For extremely confined spaces, e.g., \"Camb\", \"VicWgtn\"")
    region = models.ForeignKey(Region, blank=True, null=True)

    objects = InstitutionManager()

    class Meta:
        unique_together = [('name', 'code')]
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    @property
    def short_code(self):
        if self.abbreviation:
            return self.abbreviation
        else:
            return self.code[:5]



class Person(models.Model):
    name = models.CharField(max_length=40, db_index=True)
    barcode_id = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    novice = models.BooleanField(default=False)

    checkin_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = (
        (GENDER_MALE,     'Male'),
        (GENDER_FEMALE,   'Female'),
        (GENDER_OTHER,    'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    pronoun = models.CharField(max_length=10, blank=True, null=True)

    @property
    def has_contact(self):
        return bool(self.email or self.phone)

    class Meta:
        ordering = ['name']




class TeamManager(models.Manager):

    def get_queryset(self):
        return super(TeamManager, self).get_queryset().select_related('institution')

    def lookup(self, name, **kwargs):
        """Queries for a team with a matching name."""
        # TODO could be improved to take in a better range of fields
        try:
            institution_name, reference = name.rsplit(None, 1)
        except:
            print "Error in", repr(name)
            raise
        institution_name = institution_name.strip()
        institution = Institution.objects.lookup(institution_name)
        return self.get(institution=institution, reference=reference, **kwargs)

    def _teams_for_standings(self, round):
        return self.filter(debateteam__debate__round__seq__lte=round.seq,
            tournament=round.tournament).select_related('institution')

    def standings(self, round):
        from standings.standings import annotate_team_standings
        """Returns a list."""
        teams = self._teams_for_standings(round)
        return annotate_team_standings(teams, round)

    def ranked_standings(self, round):
        from standings.standings import ranked_team_standings
        """Returns a list."""
        teams = self._teams_for_standings(round)
        return ranked_team_standings(teams, round)

    def division_standings(self, round):
        from standings.standings import division_ranked_team_standings
        """Returns a list."""
        teams = self._teams_for_standings(round)
        return division_ranked_team_standings(teams, round)

    def subrank_standings(self, round):
        from standings.standings import subranked_team_standings
        """Returns a list."""
        teams = self._teams_for_standings(round)
        return subranked_team_standings(teams, round)



class Team(models.Model):
    reference = models.CharField(max_length=150, verbose_name="Full name or suffix", help_text="Do not include institution name (see \"uses institutional prefix\" below)")
    short_reference = models.CharField(max_length=35, verbose_name="Short name/suffix", help_text="The name shown in the draw. Do not include institution name (see \"uses institutional prefix\" below)")
    institution = models.ForeignKey(Institution)
    tournament = models.ForeignKey('debate.Tournament', db_index=True)
    emoji_seq = models.IntegerField(blank=True, null=True, help_text="Emoji number to use for this team")
    division = models.ForeignKey('debate.Division', blank=True, null=True, on_delete=models.SET_NULL)
    use_institution_prefix = models.BooleanField(default=False, verbose_name="Uses institutional prefix", help_text="If ticked, a team called \"1\" from Victoria will be shown as \"Victoria 1\" ")
    url_key = models.SlugField(blank=True, null=True, unique=True, max_length=24)
    break_categories = models.ManyToManyField('breaking.BreakCategory', blank=True)

    venue_preferences = models.ManyToManyField('venues.VenueGroup',
        through = 'draws.TeamVenuePreference',
        related_name = 'venue_preferences',
        verbose_name = 'Venue group preference'
    )

    TYPE_NONE = 'N'
    TYPE_SWING = 'S'
    TYPE_COMPOSITE = 'C'
    TYPE_BYE = 'B'
    TYPE_CHOICES = (
        (TYPE_NONE, 'None'),
        (TYPE_SWING, 'Swing'),
        (TYPE_COMPOSITE, 'Composite'),
        (TYPE_BYE, 'Bye'),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES,
                            default=TYPE_NONE)

    class Meta:
        unique_together = [('reference', 'institution', 'tournament'),('emoji_seq', 'tournament')]
        ordering = ['tournament', 'institution', 'short_reference']
        index_together = ['tournament', 'institution', 'short_reference']

    objects = TeamManager()

    def __unicode__(self):
        return u"%s - %s" % (self.tournament, self.short_name)

    @property
    def short_name(self):
        institution = self.get_cached_institution()
        if self.short_reference:
            name = self.short_reference
        else:
            name = self.reference
        if self.use_institution_prefix is True:
            if self.institution.code:
                return unicode(institution.code + " " + name)
            else:
                return unicode(institution.abbreviation + " " + name)
        else:
            return unicode(name)

    @property
    def long_name(self):
        institution = self.get_cached_institution()
        if self.use_institution_prefix is True:
            return unicode(institution.name + " " + self.reference)
        else:
            return unicode(self.reference)

    @property
    def region(self):
        return self.get_cached_institution().region

    @property
    def break_categories_nongeneral(self):
        return self.break_categories.exclude(is_general=True)

    @property
    def break_categories_str(self):
        categories = self.break_categories_nongeneral
        return "(" + ", ".join(c.name for c in categories) + ")" if categories else ""

    def get_aff_count(self, seq=None):
        from draws.models import DebateTeam
        return self._get_count(DebateTeam.POSITION_AFFIRMATIVE, seq)

    def get_neg_count(self, seq=None):
        from draws.models import DebateTeam
        return self._get_count(DebateTeam.POSITION_NEGATIVE, seq)

    def _get_count(self, position, seq):
        dts = self.debateteam_set.filter(position=position, debate__round__stage=Round.STAGE_PRELIMINARY)
        if seq is not None:
            dts = dts.filter(debate__round__seq__lte=seq)
        return dts.count()

    def get_debates(self, before_round):
        dts = self.debateteam_set.select_related('debate').order_by('debate__round__seq')
        if before_round is not None:
            dts = dts.filter(debate__round__seq__lt=before_round)
        return [dt.debate for dt in dts]

    @property
    def get_preferences(self):
        return self.teamvenuepreference_set.objects.all()

    @property
    def debates(self):
        return self.get_debates(None)

    @cached_property
    def wins_count(self):
        from results.models import TeamScore
        wins = TeamScore.objects.filter(ballot_submission__confirmed=True, debate_team__team=self, win=True).count()
        return wins

    @cached_property
    def speakers(self):
        return self.speaker_set.all().select_related('person_ptr')

    def seen(self, other, before_round=None):
        debates = self.get_debates(before_round)
        return len([1 for d in debates if other in d])

    def same_institution(self, other):
        return self.institution_id == other.institution_id

    def prev_debate(self, round_seq):
        from draws.models import DebateTeam
        try:
            return DebateTeam.objects.filter(
                debate__round__seq__lt=round_seq,
                team=self,
            ).order_by('-debate__round__seq')[0].debate
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

def update_team_cache(sender, instance, created, **kwargs):
    cached_key = "%s_%s_%s" % ('teamid', instance.id, '_institution__object')
    cache.delete(cached_key)
    cached_key = "%s_%s_%s" % ('teamid', instance.id, '_speaker__objects')
    cache.delete(cached_key)

# Update the cached tournament object when model is changed)
signals.post_save.connect(update_team_cache, sender=Team)

class Speaker(Person):
    team = models.ForeignKey(Team)

    def __unicode__(self):
        return unicode(self.name)


class AdjudicatorManager(models.Manager):
    use_for_related_fields = True

    def accredited(self):
        return self.filter(novice=False)

    def get_queryset(self):
        return super(AdjudicatorManager, self).get_queryset().select_related('institution')

class Adjudicator(Person):
    institution = models.ForeignKey(Institution)
    tournament = models.ForeignKey('debate.Tournament', blank=True, null=True)
    test_score = models.FloatField(default=0)
    url_key = models.SlugField(blank=True, null=True, unique=True, max_length=24)

    institution_conflicts = models.ManyToManyField('Institution', through='allocations.AdjudicatorInstitutionConflict', related_name='adj_inst_conflicts')
    conflicts = models.ManyToManyField('Team', through='allocations.AdjudicatorConflict', related_name='adj_adj_conflicts')

    breaking = models.BooleanField(default=False)
    independent = models.BooleanField(default=False, blank=True)
    adj_core = models.BooleanField(default=False, blank=True)

    objects = AdjudicatorManager()

    class Meta:
        ordering = ['tournament', 'institution', 'name']

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)

    def conflict_with(self, team):
        if not hasattr(self, '_conflict_cache'):
            from allocations.models import AdjudicatorConflict, AdjudicatorInstitutionConflict
            self._conflict_cache = set(c['team_id'] for c in
                AdjudicatorConflict.objects.filter(adjudicator=self).values('team_id')
            )
            self._institution_conflict_cache = set(c['institution_id'] for c in
                AdjudicatorInstitutionConflict.objects.filter(adjudicator=self).values('institution_id')
            )
        return team.id in self._conflict_cache or team.institution_id in self._institution_conflict_cache

    @property
    def is_unaccredited(self):
        return self.novice

    @property
    def region(self):
        return self.institution.region

    @cached_property
    def score(self):
        if self.tournament:
            weight = self.tournament.current_round.feedback_weight
        else:
            # For shared ajudicators
            weight = 1

        feedback_score = self._feedback_score()
        if feedback_score is None:
            feedback_score = 0
            weight = 0

        return self.test_score * (1 - weight) + (weight * feedback_score)


    def _feedback_score(self):
        from allocations.models import DebateAdjudicator
        return self.adjudicatorfeedback_set.filter(confirmed=True).exclude(
                source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE).aggregate(
                avg=models.Avg('score'))['avg']

    @property
    def feedback_score(self):
        return self._feedback_score() or None

    def get_feedback(self):
        return self.adjudicatorfeedback_set.all()

    def seen_team(self, team, before_round=None):
        from draws.models import DebateTeam
        if not hasattr(self, '_seen_cache'):
            self._seen_cache = {}
        if before_round not in self._seen_cache:
            qs = DebateTeam.objects.filter(
                allocations__debateadjudicator__adjudicator=self
            )
            if before_round is not None:
                qs = qs.filter(
                    debate__round__seq__lt = before_round.seq
                )
            self._seen_cache[before_round] = set(dt.team.id for dt in qs)
        return team.id in self._seen_cache[before_round]

    def seen_adjudicator(self, adj, before_round=None):
        from allocations.models import DebateAdjudicator
        d = DebateAdjudicator.objects.filter(
            adjudicator = self,
            allocations__debateadjudicator__adjudicator = adj,
        )
        if before_round is not None:
            d = d.filter(
                debate__round__seq__lt = before_round.seq
            )
        return d.count()
