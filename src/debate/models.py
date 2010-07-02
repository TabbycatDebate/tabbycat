from django.db import models

from debate.utils import pair_list, memoize
from debate.draw import RandomDrawNoConflict, AidaDraw
from debate.adjudicator.anneal import SAAllocator

from debate.result import DebateResult

class ScoreField(models.FloatField):
    pass

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^debate\.models\.ScoreField"])

class Tournament(models.Model):

    slug = models.SlugField(unique=True)
    current_round = models.ForeignKey('Round', null=True, blank=True,
                                     related_name='tournament_')

    @models.permalink
    def get_absolute_url(self):
        return ('tournament_home', [self.slug])

    @property
    def teams(self):
        return Team.objects.filter(institution__tournament=self)

    def create_next_round(self):
        curr = self.current_round
        next = curr.seq + 1
        r = Round(name="Round %d" % next, seq=next, type=Round.TYPE_PRELIM,
                  tournament=self)
        r.save()
        r.activate_all()

    @property
    def config(self):
        if not hasattr(self, '_config'):
            from debate.config import Config
            self._config = Config(self)
        return self._config

    def __unicode__(self):
        return unicode(self.slug)

class Institution(models.Model):
    tournament = models.ForeignKey(Tournament)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('tournament', 'code')
    
    def __unicode__(self):
        return unicode(self.name) 

class TeamManager(models.Manager):
    def standings(self, round=None):
        if round is None:
            teams = self.all()
        else:
            teams = self.filter(
                debateteam__debate__round__seq__lte = round.seq,
            )

        teams = teams.annotate(
            points = models.Sum('debateteam__teamscore__points'),
            speaker_score = models.Sum('debateteam__teamscore__score'),
            results_count = models.Count('debateteam__teamscore'),
        ).order_by('-points', '-speaker_score')

        return teams

class Team(models.Model):
    name = models.CharField(max_length=50)
    institution = models.ForeignKey(Institution)

    # set to True if a team is ineligible to break (other than being
    # swing/composite)
    cannot_break = models.BooleanField(default=False)

    TYPE_NORMAL = 'N'
    TYPE_ESL = 'E'
    TYPE_SWING = 'S'
    TYPE_COMPOSITE = 'C'
    TYPE_CHOICES = (
        (TYPE_NORMAL, 'Normal'),
        (TYPE_ESL, 'ESL'),
        (TYPE_SWING, 'Swing'),
        (TYPE_COMPOSITE, 'Composite'),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES,
                            default=TYPE_NORMAL)

    class Meta:
        unique_together = [('name', 'institution')]

    objects = TeamManager()
    
    def __unicode__(self):
        return unicode(self.name)

    def get_aff_count(self, seq=None):
        return self._get_count(DebateTeam.POSITION_AFFIRMATIVE, seq)

    def get_neg_count(self, seq=None):
        return self._get_count(DebateTeam.POSITION_NEGATIVE, seq)

    def _get_count(self, position, seq):
        dts = DebateTeam.objects.filter(team=self, position=position)
        if seq is not None:
            dts = dts.filter(debate__round__seq__lte=seq)
        return dts.count()
    
    def get_debates(self, before_round):
        dts = DebateTeam.objects.select_related('debate').filter(team=self).order_by('debate__round__seq')
        if before_round is not None:
            dts = dts.filter(debate__round__seq__lt=before_round)
        return [dt.debate for dt in dts]

    @property
    def debates(self):
        return self.get_debates(None)
    
    def seen(self, other, before_round=None):
        debates = self.get_debates(before_round)

        return len([1 for d in debates if other in d])

    def same_institution(self, other):
        return self.institution_id == other.institution_id

    def prev_debate(self, round_seq):
        try:
            return DebateTeam.objects.filter(
                debate__round__seq__lt=round_seq,
                team=self,
            ).order_by('-debate__round__seq')[0].debate
        except IndexError:
            return None

    @property
    def speakers(self):
        return self.speaker_set.all()

def TeamAtRound(team, round):
    t = Team.objects.standings(round).get(id=team.id)
    if round:
        setattr(t, 'aff_count', t.get_aff_count(round.seq))
        setattr(t, 'neg_count', t.get_neg_count(round.seq))
    return t


class SpeakerManager(models.Manager):
    def standings(self, tournament, round=None):
        # only include scoresheets for up to this round, exclude replies
        if round:
            speakers = self.filter(
                team__institution__tournament=tournament,
                speakerscore__position__lte=3,
                speakerscore__debate_team__debate__round__seq__lte =
                round.seq,
            )
        else:
            speakers = self.filter(
                team__institution__tournament=tournament,
                speakerscore__position__lte=3,
            )

        speakers = speakers.annotate(
            total = models.Sum('speakerscore__score'),
        ).order_by('-total', 'name')

        return speakers

class Person(models.Model):
    name = models.CharField(max_length=40)
    barcode_id = models.IntegerField(blank=True, null=True)

class Checkin(models.Model):
    person = models.ForeignKey('Person')
    round = models.ForeignKey('Round')

class Speaker(Person):
    team = models.ForeignKey(Team)

    TYPE_NORMAL = 'N'
    TYPE_ESL = 'E'
    TYPE_CHOICES = (
        (TYPE_NORMAL, 'Normal'),
        (TYPE_ESL, 'ESL'),
    )

    type = models.CharField(max_length=1, choices=TYPE_CHOICES,
                            default=TYPE_NORMAL)

    objects = SpeakerManager()

    def __unicode__(self):
        return unicode(self.name)


class AdjudicatorManager(models.Manager):
    use_for_related_fields = True

    def accredited(self):
        return self.filter(is_trainee=False)

class Adjudicator(Person):
    institution = models.ForeignKey(Institution)
    test_score = models.FloatField(default=0)

    conflicts = models.ManyToManyField('Team', through='AdjudicatorConflict')

    is_trainee = models.BooleanField(default=False)

    objects = AdjudicatorManager()
   
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)
    
    def conflict_with(self, team):
        if not hasattr(self, '_conflict_cache'):
            self._conflict_cache = set(c['team_id'] for c in
                AdjudicatorConflict.objects.filter(adjudicator=self).values('team_id')
            )
        return team.id in self._conflict_cache

    @property
    def tournament(self):
        return self.institution.tournament

    @property
    def score(self):
        weight = self.tournament.current_round.feedback_weight

        feedback_score = self._feedback_score()
        if feedback_score is None:
            feedback_score = 0
            weight = 0

        return self.test_score * (1 - weight) + (weight *
    feedback_score)


    def _feedback_score(self):
        return AdjudicatorFeedback.objects.filter(
            adjudicator = self,
        ).aggregate(avg=models.Avg('score'))['avg']

    @property
    def feedback_score(self):
        return self._feedback_score() or 0


    def get_feedback(self):
        return AdjudicatorFeedback.objects.filter(adjudicator=self)

    def seen_team(self, team, before_round=None):
        if not hasattr(self, '_seen_cache'):
            self._seen_cache = {}
        if before_round not in self._seen_cache:
            qs = DebateTeam.objects.filter(
                debate__debateadjudicator__adjudicator=self
            )
            if before_round is not None:
                qs = qs.filter(
                    debate__round__seq__lt = before_round.seq
                )
            self._seen_cache[before_round] = set(dt.team.id for dt in qs)
        return team.id in self._seen_cache[before_round] 

    def seen_adjudicator(self, adj, before_round=None):
        d = DebateAdjudicator.objects.filter(
            adjudicator = self,
            debate__debateadjudicator__adjudicator = adj,
        )
        if before_round is not None:
            d = d.filter(
                debate__round__seq__lt = before_round.seq
            )
        return d.count()

class AdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('Adjudicator')
    team = models.ForeignKey('Team')

class RoundManager(models.Manager):
    use_for_related_Fields = True

    def get_query_set(self):
        return super(RoundManager,
                     self).get_query_set().select_related('tournament').order_by('seq')


class Round(models.Model):
    TYPE_RANDOM = 'R'
    TYPE_PRELIM = 'P'
    TYPE_BREAK = 'B'
    TYPE_CHOICES = (
        (TYPE_RANDOM, 'Random'),
        (TYPE_PRELIM, 'Preliminary'),
        (TYPE_BREAK, 'Break'),
    )

    DRAW_CLASS = {
        TYPE_RANDOM: RandomDrawNoConflict,
        TYPE_PRELIM: AidaDraw,
    }
    
    STATUS_NONE = 0
    STATUS_DRAFT = 1
    STATUS_CONFIRMED = 10
    STATUS_CHOICES = (
        (STATUS_NONE, 'None'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
    )

    objects = RoundManager()

    tournament = models.ForeignKey(Tournament, related_name='rounds')
    seq = models.IntegerField()
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    draw_status = models.IntegerField(choices=STATUS_CHOICES,
                                      default=STATUS_NONE)
    venue_status = models.IntegerField(choices=STATUS_CHOICES,
                                       default=STATUS_NONE)
    adjudicator_status = models.IntegerField(choices=STATUS_CHOICES,
                                             default=STATUS_NONE)

    checkins = models.ManyToManyField('Person', through='Checkin',
                                      related_name='checkedin_rounds')

    active_venues = models.ManyToManyField('Venue', through='ActiveVenue')
    active_adjudicators = models.ManyToManyField('Adjudicator',
                                                 through='ActiveAdjudicator')
    active_teams = models.ManyToManyField('Team', through='ActiveTeam')

    feedback_weight = models.FloatField(default=0)

    class Meta:
        unique_together = ('tournament', 'seq')

    def __unicode__(self):
        return unicode(self.seq)
    
    def _drawer(self):
        return self.DRAW_CLASS[self.type]

    def draw(self):
        if self.draw_status != self.STATUS_NONE:
            raise
        # delete all existing debates for this round
        Debate.objects.filter(round=self).delete()

        drawer = self._drawer()
        d = drawer(self)
        self.make_debates(d.draw())
        self.draw_status = self.STATUS_DRAFT
        self.save()

        from debate.draw import assign_importance
        #assign_importance(self)

    def allocate_adjudicators(self, alloc_class=SAAllocator):
        if self.draw_status != self.STATUS_CONFIRMED:
            raise

        debates = self.get_draw()
        adjs = list(self.active_adjudicators.accredited().filter(test_score__gt=0))
        allocator = alloc_class(debates, adjs)

        for alloc in allocator.allocate():
            alloc.save()
        self.adjudicator_status = self.STATUS_DRAFT
        self.save()

    def get_draw(self):
        # -bracket is included for ateneo data, which doesn't have room_rank
        return Debate.objects.filter(round=self).order_by('room_rank',
                                                          '-bracket')

    def get_unordered_draw(self):
        return Debate.objects.filter(round=self).order_by('venue__name')
        
    def make_debates(self, pairs):

        import random
        venues = list(self.active_venues.all())[:len(pairs)]
        random.shuffle(venues)

        for i, pair in enumerate(pairs):
            debate = Debate(round=self, venue=venues.pop(0))
            debate.bracket = max(0, pair[0].points, pair[1].points)
            debate.room_rank = i+1
            debate.save()
            
            aff = DebateTeam(debate=debate, team=pair[0], position=DebateTeam.POSITION_AFFIRMATIVE)
            neg = DebateTeam(debate=debate, team=pair[1], position=DebateTeam.POSITION_NEGATIVE)
            
            aff.save()
            neg.save()

    def base_availability(self, model, active_table, active_column, model_table,
                         id_field='id'):
        d = {
            'active_table' : active_table,
            'active_column' : active_column,
            'model_table': model_table,
            'id_field': id_field,
            'id' : self.id,
        }
        return model.objects.all().extra(select={'is_active': """EXISTS (Select 1
                                                 from %(active_table)s 
                                                 drav where
                                                 drav.%(active_column)s =
                                                 %(model_table)s.%(id_field)s and
                                                 drav.round_id=%(id)d)""" % d })

    def person_availability(self):
        return self.base_availability(Person, 'debate_checkin', 'person_id',
                                      'debate_person')



    def venue_availability(self):
        return self.base_availability(Venue, 'debate_activevenue', 'venue_id',
                                      'debate_venue')
    def unused_venues(self):
        result = self.venue_availability().extra(
            select = {'is_used': """EXISTS (SELECT 1 
                      FROM debate_debate da 
                      WHERE da.round_id=%d AND
                      da.venue_id = debate_venue.id)""" % self.id},
        )
        # if we wanted to do this with sql we'd need to use a subselect, this is much
        # easier
        return [v for v in result if v.is_active and not v.is_used]

    def adjudicator_availability(self):
        return self.base_availability(Adjudicator, 'debate_activeadjudicator', 
                                      'adjudicator_id',
                                      'debate_adjudicator', id_field='person_ptr_id')

    def unused_adjudicators(self):
        result =  self.adjudicator_availability().extra(
            select = {'is_used': """EXISTS (SELECT 1
                      FROM debate_debateadjudicator da
                      LEFT JOIN debate_debate d ON da.debate_id = d.id
                      WHERE d.round_id = %d AND
                      da.adjudicator_id = debate_adjudicator.person_ptr_id)""" % self.id },
        )
        return [a for a in result if a.is_active and not a.is_used]

    def team_availability(self):
        return self.base_availability(Team, 'debate_activeteam', 'team_id',
                                      'debate_team')

    def set_available_base(self, ids, model, active_model, get_active,
                             id_column, active_id_column, remove=True):
        ids = set(ids)
        all_ids = set(a['id'] for a in model.objects.values('id'))
        exclude_ids = all_ids.difference(ids)
        existing_ids = set(a['id'] for a in get_active.values('id'))

        remove_ids = existing_ids.intersection(exclude_ids)
        add_ids = ids.difference(existing_ids)

        if remove:
            active_model.objects.filter(**{
                '%s__in' % active_id_column: remove_ids, 
                'round': self,
            }).delete()

        for id in add_ids:
            m = active_model(round=self)
            setattr(m, id_column, id)
            m.save()

    def set_available_people(self, ids):
        return self.set_available_base(ids, Person, Checkin,
                                      self.checkins, 'person_id',
                                      'person__id', remove=False)

    def set_available_venues(self, ids):
        return self.set_available_base(ids, Venue, ActiveVenue,
                                       self.active_venues, 'venue_id',
                                       'venue__id')

    def set_available_adjudicators(self, ids):
        return self.set_available_base(ids, Adjudicator, ActiveAdjudicator,
                                       self.active_adjudicators,
                                       'adjudicator_id', 'adjudicator__id')

    def set_available_teams(self, ids):
        return self.set_available_base(ids, Team, ActiveTeam,
                                       self.active_teams, 'team_id',
                                      'team__id')

    def activate_adjudicator(self, adj, state=True):
        if state:
            ActiveAdjudicator.objects.get_or_create(round=self, adjudicator=adj)
        else:
            ActiveAdjudicator.objects.filter(round=self,
                                             adjudicator=adj).delete()

    def activate_venue(self, venue, state=True):
        if state:
            ActiveVenue.objects.get_or_create(round=self, venue=venue)
        else:
            ActiveVenue.objects.filter(round=self, venue=venue).delete()

    def activate_team(self, team, state=True):
        if state:
            ActiveTeam.objects.get_or_create(round=self, team=team)
        else:
            ActiveTeam.objects.filter(round=self, team=team).delete()

    def activate_all(self):
        self.set_available_venues([v.id for v in Venue.objects.all()])
        self.set_available_adjudicators([a.id for a in
                                         Adjudicator.objects.all()])
        self.set_available_teams([t.id for t in Team.objects.all()])

    @property
    @memoize
    def prev(self):
        try:
            return Round.objects.get(seq=self.seq-1)
        except Round.DoesNotExist:
            return None

class Venue(models.Model):
    name = models.CharField(max_length=40)
    group = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField()
    tournament = models.ForeignKey(Tournament)

    def __unicode__(self):
        return u'%s (%d)' % (self.name, self.priority)

class ActiveVenue(models.Model):
    venue = models.ForeignKey(Venue)
    round = models.ForeignKey(Round)

    class Meta:
        unique_together = [('venue', 'round')]

class ActiveTeam(models.Model):
    team = models.ForeignKey(Team)
    round = models.ForeignKey(Round)

    class Meta:
        unique_together = [('team', 'round')]

class ActiveAdjudicator(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    round = models.ForeignKey(Round)
    
    class Meta:
        unique_together = [('adjudicator', 'round')]

class DebateManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(DebateManager, self).get_query_set().select_related(
        'round', 'venue')

class Debate(models.Model):
    STATUS_NONE = 'N' 
    STATUS_DRAFT = 'D' 
    STATUS_CONFIRMED = 'C' 
    STATUS_CHOICES = (
        (STATUS_NONE, 'None'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
    )
    objects = DebateManager()

    round = models.ForeignKey(Round)
    venue = models.ForeignKey(Venue, blank=True, null=True)
    bracket = models.IntegerField(default=0)
    room_rank = models.IntegerField(default=0)
    importance = models.IntegerField(blank=True, null=True)
    result_status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                                    default=STATUS_NONE)

    def _get_teams(self):
        if not hasattr(self, '_team_cache'):
            self._team_cache = {}

            for t in DebateTeam.objects.filter(debate=self):
                self._team_cache[t.position] = t

    @property
    def aff_team(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_AFFIRMATIVE].team

    @property
    def neg_team(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_NEGATIVE].team

    def get_team(self, side):
        return getattr(self, '%s_team' % side)

    def get_dt(self, side):
        return getattr(self, '%s_dt' % side)

    @property
    def aff_dt(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_AFFIRMATIVE]

    @property
    def neg_dt(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_NEGATIVE]

    @property
    def draw_conflicts(self):
        d = []
        history = self.aff_team.seen(self.neg_team, before_round=self.round.seq)
        if history:
            d.append("History (%d)" % history)
        if self.aff_team.institution == self.neg_team.institution:
            d.append("Institution")

        return d

    @property
    def all_conflicts(self):
        return self.draw_conflicts + self.adjudicator_conflicts

    @property
    def adjudicator_conflicts(self):
        class Conflict(object):
            def __init__(self, adj, team):
                self.adj = adj
                self.team = team
            def __unicode__(self):
                return u'Adj %s + %s' % (self.adj, self.team)

        a = []
        for t, adj in self.adjudicators:
            for team in (self.aff_team, self.neg_team):
                if adj.conflict_with(team):
                    a.append(Conflict(adj, team))
        return a

    @property
    def adjudicators(self):
        adjs = DebateAdjudicator.objects.filter(debate=self)
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
    def adjudicators_display(self):
        alloc = self.adjudicators

        s = alloc.chair.name
        if alloc.panel:
            s += " (c), "
        elif alloc.trainees:
            s += ", "
        sd = [p.name for p in alloc.panel]
        sd.extend(["%s (t)" % t.name for t in alloc.trainees])
        s += ", ".join(sd)

        return s

    @property
    def result(self):
        if not hasattr(self, '_result'):
            from debate.result import DebateResult
            self._result = DebateResult(self)
        return self._result

    def get_side(self, team):
        if self.aff_team == team:
            return 'aff'
        if self.neg_team == team:
            return 'neg'
        return None
 
    def __contains__(self, team):
        return team in (self.aff_team, self.neg_team) 

    def __unicode__(self):
        return u'[%s] %s vs %s (%s)' % (self.round.seq, self.aff_team.name, self.neg_team.name,
                                   self.venue)

    @property
    def matchup(self):
        return u'%s vs %s' % (self.aff_team.name, self.neg_team.name)
    
class SRManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return super(SRManager, self).get_query_set().select_related(depth=1)

class DebateTeam(models.Model):
    POSITION_AFFIRMATIVE = 'A'
    POSITION_NEGATIVE = 'N'
    POSITION_CHOICES = (
        (POSITION_AFFIRMATIVE, 'Affirmative'),
        (POSITION_NEGATIVE, 'Negative'),
    )

    objects = SRManager()
    
    debate = models.ForeignKey(Debate)
    team = models.ForeignKey(Team)
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)

    def __unicode__(self):
        return u'%s %s' % (self.debate, self.team)
        
    
class DebateAdjudicator(models.Model):
    TYPE_CHAIR = 'C'
    TYPE_PANEL = 'P'
    TYPE_TRAINEE = 'T'

    TYPE_CHOICES = (
        (TYPE_CHAIR, 'Chair'),
        (TYPE_PANEL, 'Panel'),
        (TYPE_TRAINEE, 'Trainee'),
    )

    objects = SRManager()
    
    debate = models.ForeignKey(Debate)
    adjudicator = models.ForeignKey(Adjudicator)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)

    def __unicode__(self):
        return u'%s %s' % (self.adjudicator, self.debate)

class AdjudicatorFeedback(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    score = models.FloatField()
    comments = models.TextField(blank=True)

    source_adjudicator = models.ForeignKey(DebateAdjudicator, blank=True,
                                           null=True)
    source_team = models.ForeignKey(DebateTeam, blank=True, null=True)

    @property
    def source(self):
        if self.source_adjudicator:
            return self.source_adjudicator.adjudicator
        if self.source_team:
            return self.source_team.team

    @property
    def debate(self):
        if self.source_adjudicator:
            return self.source_adjudicator.debate
        if self.source_team:
            return self.source_team.debate


    @property
    def round(self):
        return self.debate.round

    @property
    def feedback_weight(self):
        if self.round:
            return self.round.feedback_weight
        return 1
    

class AdjudicatorAllocation(object):
    def __init__(self, debate, chair=None, panel=None):
        self.debate = debate
        self.chair = chair
        self.panel = panel or []
        self.trainees = []

    @property
    def list(self):
        a = [self.chair]
        a.extend(self.panel)
        return a

    def __iter__(self):
        yield DebateAdjudicator.TYPE_CHAIR, self.chair
        for a in self.panel:
            yield DebateAdjudicator.TYPE_PANEL, a
        for a in self.trainees:
            yield DebateAdjudicator.TYPE_TRAINEE, a

    def delete(self):
        """
        Delete existing, current allocation
        """

        DebateAdjudicator.objects.filter(debate=self.debate).delete()
        self.chair = None
        self.panel = []
        self.trainees = []

    def save(self):
        DebateAdjudicator.objects.filter(debate=self.debate).delete()
        for t, adj in self:
            if isinstance(adj, Adjudicator):
                adj = adj.id
            if adj:
                DebateAdjudicator(
                    debate = self.debate,
                    adjudicator_id = adj,
                    type = t,
                ).save()

class SpeakerScoreByAdj(models.Model):
    """
    Holds score given by a particular adjudicator in a debate
    """
    debate_adjudicator = models.ForeignKey(DebateAdjudicator)
    debate_team = models.ForeignKey(DebateTeam)
    score = ScoreField()
    position = models.IntegerField()

    class Meta:
        unique_together = [('debate_adjudicator', 'debate_team', 'position')]

    @property
    def debate(self):
        return self.debate_team.debate
    
class TeamScore(models.Model):
    """
    Holds a teams total score and points in a debate
    """
    debate_team = models.ForeignKey(DebateTeam, unique=True)
    points = models.PositiveSmallIntegerField()
    score = ScoreField()

class SpeakerScoreManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(SpeakerScoreManager,
                     self).get_query_set().select_related('speaker')

class SpeakerScore(models.Model):
    """
    Represents a speaker's score in a debate
    """
    debate_team = models.ForeignKey(DebateTeam)
    speaker = models.ForeignKey(Speaker)
    score = ScoreField()
    position = models.IntegerField()

    objects = SpeakerScoreManager()

    class Meta:
        unique_together = [('debate_team', 'speaker', 'position')]

class ConfigManager(models.Manager):
    def set(self, tournament, key, value):
        obj, created = self.get_or_create(tournament=tournament, key=key)
        obj.value = value
        obj.save()

    def get_(self, tournament, key, default=None):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            return self.get(tournament=tournament, key=key).value
        except ObjectDoesNotExist:
            return default
            

class Config(models.Model):
    tournament = models.ForeignKey(Tournament)
    key = models.CharField(max_length=40)
    value = models.CharField(max_length=40)

    objects = ConfigManager()

