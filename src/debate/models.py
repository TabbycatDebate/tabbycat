from django.db import models

from debate.utils import pair_list, memoize
from debate.draw import RandomDrawNoConflict, AidaDraw
from debate.adjudicator import DumbAdjAllocator

class ScoreField(models.FloatField):
    pass

class Tournament(object):
    @property
    def teams(self):
        return Team.objects.all()

    @property
    def current_round(self):
        try:
            return Round.objects.get(is_current=True)
        except IndexError:
            return None
    
class Institution(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=40)
    
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
            team_points = models.Sum('debateteam__teamscore__points'),
            team_score = models.Sum('debateteam__teamscore__score'),
            results_count = models.Count('debateteam__teamscore'),
        ).order_by('-team_points', '-team_score')

        return teams

class Team(models.Model):
    name = models.CharField(max_length=50)
    institution = models.ForeignKey(Institution)
    is_active = models.BooleanField()

    objects = TeamManager()
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)
    
    @property
    def aff_count(self):
        # TODO
        return 0
    
    @property
    def neg_count(self):
        # TODO
        return 0

    def get_debates(self, before_round):
        dts = DebateTeam.objects.select_related('debate').filter(team=self)
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

class Speaker(models.Model):
    name = models.CharField(max_length=40)
    team = models.ForeignKey(Team)

    def __unicode__(self):
        return unicode(self.name)

class ActiveManager(models.Manager):
    def __init__(self, status):
        super(ActiveManager, self).__init__()
        self.status = status
        
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(is_active=self.status)

class Adjudicator(models.Model):
    name = models.CharField(max_length=40)
    institution = models.ForeignKey(Institution)
    test_score = models.FloatField()

    conflicts = models.ManyToManyField('Team', through='AdjudicatorConflict')
   
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)
    
    def conflict_with(self, team):
        return AdjudicatorConflict.objects.filter(adjudicator=self,
                                                  team=team).count()

class AdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('Adjudicator')
    team = models.ForeignKey('Team')

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

    seq = models.IntegerField()
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    draw_status = models.IntegerField(choices=STATUS_CHOICES,
                                      default=STATUS_NONE)
    venue_status = models.IntegerField(choices=STATUS_CHOICES,
                                       default=STATUS_NONE)
    adjudicator_status = models.IntegerField(choices=STATUS_CHOICES,
                                             default=STATUS_NONE)
    is_current = models.BooleanField()
    
    tournament = Tournament()

    active_venues = models.ManyToManyField('Venue', through='ActiveVenue')
    active_adjudicators = models.ManyToManyField('Adjudicator',
                                                 through='ActiveAdjudicator')
    active_teams = models.ManyToManyField('Team', through='ActiveTeam')

    feedback_weight = models.FloatField(default=1)

    def __unicode__(self):
        return unicode(self.id)
    
    def debates(self):
        return Debate.objects.filter(round=self)
    
    def _drawer(self):
        return self.DRAW_CLASS[self.type]

    def draw(self):
        if self.draw_status != self.STATUS_NONE:
            raise

        drawer = self._drawer()
        d = drawer(self)
        self.make_debates(d.get_draw())
        self.draw_status = self.STATUS_DRAFT
        self.save()

    def allocate_adjudicators(self):
        if self.draw_status != self.STATUS_CONFIRMED:
            raise

        allocator = DumbAdjAllocator(self)
        for alloc in allocator.get_allocation():
            alloc.save()
        self.adjudicator_status = self.STATUS_DRAFT
        self.save()

    def get_draw(self):
        return Debate.objects.filter(round=self)
        
    def make_debates(self, pairs):
        import random

        venues = list(self.active_venues.all())[:len(pairs)]
        random.shuffle(venues)
        
        for pair in pairs:
            debate = Debate(round=self, venue=venues.pop(0))
            debate.bracket = max(pair[0].team_points, pair[1].team_points)
            debate.save()
            
            aff = DebateTeam(debate=debate, team=pair[0], position=DebateTeam.POSITION_AFFIRMATIVE)
            neg = DebateTeam(debate=debate, team=pair[1], position=DebateTeam.POSITION_NEGATIVE)
            
            aff.save()
            neg.save()

    def base_availability(self, model, active_table, active_column, model_table):
        d = {
            'active_table' : active_table,
            'active_column' : active_column,
            'model_table': model_table,
            'id' : self.id
        }
        return model.objects.all().extra(select={'is_active': """EXISTS (Select 1
                                                 from %(active_table)s 
                                                 drav where
                                                 drav.%(active_column)s =
                                                 %(model_table)s.id and
                                                 drav.round_id=%(id)d)""" % d })

    def venue_availability(self):
        return self.base_availability(Venue, 'debate_activevenue', 'venue_id',
                                      'debate_venue')
    def unused_venues(self):
        return self.venue_availability().extra(
            select = {'is_used': """EXISTS (SELECT 1 
                      FROM debate_debate da 
                      WHERE da.round_id=%d AND
                      da.venue_id = debate_venue.id)""" % self.id},
            where = ['is_active AND NOT is_used'])


    def adjudicator_availability(self):
        return self.base_availability(Adjudicator, 'debate_activeadjudicator', 
                                      'adjudicator_id',
                                      'debate_adjudicator')

    def unused_adjudicators(self):
        return self.adjudicator_availability().extra(
            select = {'is_used': """EXISTS (SELECT 1
                      FROM debate_debateadjudicator da
                      LEFT JOIN debate_debate d ON da.debate_id = d.id
                      WHERE d.round_id = %d AND
                      da.adjudicator_id = debate_adjudicator.id)""" % self.id },
            where = ['is_active AND NOT is_used'])

    def team_availability(self):
        return self.base_availability(Team, 'debate_activeteam', 'team_id',
                                      'debate_team')

    def set_available_base(self, ids, model, active_model, get_active,
                             id_column):
        ids = set(ids)
        all_ids = set(a['id'] for a in model.objects.values('id'))
        exclude_ids = all_ids.difference(ids)
        existing_ids = set(a['id'] for a in get_active.values('id'))

        remove_ids = existing_ids.intersection(exclude_ids)
        add_ids = ids.difference(existing_ids)

        active_model.objects.filter(round=self, id__in=remove_ids).delete()
        for id in add_ids:
            m = active_model(round=self)
            setattr(m, id_column, id)
            m.save()

    def set_available_venues(self, ids):
        return self.set_available_base(ids, Venue, ActiveVenue,
                                       self.active_venues, 'venue_id')

    def set_available_adjudicators(self, ids):
        return self.set_available_base(ids, Adjudicator, ActiveAdjudicator,
                                       self.active_adjudicators, 'adjudicator_id')

    def set_available_teams(self, ids):
        return self.set_available_base(ids, Team, ActiveTeam,
                                       self.active_teams, 'team_id')

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
    priority = models.IntegerField()

    def __unicode__(self):
        return u'%s (%d)' % (self.name, self.priority)

class ActiveVenue(models.Model):
    venue = models.ForeignKey(Venue)
    round = models.ForeignKey(Round)

class ActiveTeam(models.Model):
    team = models.ForeignKey(Team)
    round = models.ForeignKey(Round)

class ActiveAdjudicator(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    round = models.ForeignKey(Round)
    
class Debate(models.Model):
    STATUS_NONE = 'N' 
    STATUS_DRAFT = 'D' 
    STATUS_CONFIRMED = 'C' 
    STATUS_CHOICES = (
        (STATUS_NONE, 'None'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
    )
    round = models.ForeignKey(Round)
    venue = models.ForeignKey(Venue, blank=True, null=True)
    bracket = models.IntegerField(default=0)
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
        return DebateResult(self)

    def get_side(self, team):
        if self.aff_team == team:
            return 'aff'
        if self.neg_team == team:
            return 'neg'
        return None
 
    def __contains__(self, team):
        return team in (self.aff_team, self.neg_team) 

    def __unicode__(self):
        return u'%s vs %s' % (self.aff_team.name, self.neg_team.name)
    
class DebateResult(object):
    def __init__(self, debate):
        self.debate = debate

        aff_speakers = dict((i, None) for i in range(1, 5))
        neg_speakers = dict((i, None) for i in range(1, 5))

        self.teams = {
            'aff': aff_speakers,
            'neg': neg_speakers,
        }

        self.points = {
            'aff': None,
            'neg': None,
        }

        self._other = {
            'aff': 'neg',
            'neg': 'aff',
        }

        self._init_side('aff')
        self._init_side('neg')

    def _init_side(self, side):
        dt = self.debate.get_dt(side)

        for sss in SpeakerScore.objects.filter(
            debate_team = dt,
        ):

            self.set_speaker_entry(side, sss.position,
                                   sss.speaker, sss.score)
            
        try:
            ts = TeamScore.objects.get(debate_team=dt)
            points = ts.points
        except TeamScore.DoesNotExist:
            points = None


        self.points[side] = points

    def save(self):
        self._save('aff')
        self._save('neg')

    def _save(self, side):
        dt = self.debate.get_dt(side)
        total = self._score(side)
        points = self._points(side)

        TeamScore.objects.filter(debate_team=dt).delete()
        TeamScore(debate_team=dt, score=total, points=points).save()

        SpeakerScore.objects.filter(debate_team=dt).delete()
        for i in range(1, 5):
            speaker, score = self.teams[side][i]
            SpeakerScore(
                debate_team = dt,
                speaker = speaker,
                score = score,
                position = i,
            ).save()

        
    def get_speaker(self, side, position):
        return self.teams[side][position][0]

    def get_speaker_score(self, side, position):
        return self.teams[side][position]

    def set_speaker_entry(self, side, pos, speaker, score):
        self.teams[side][pos] = (speaker, score)

    def _score(self, side):
        if None in self.teams[side].values():
            return None
        return sum(score for (sp, score) in self.teams[side].values())

    @property
    def aff_score(self):
        return self._score('aff')

    @property
    def neg_score(self):
        return self._score('neg')

    def _points(self, side):
        if self._score(side):
            if self._score(side) > self._score(self._other[side]):
                return 1
            return 0
        return None

    @property
    def aff_points(self):
        return self._points('aff')

    @property
    def neg_points(self):
        return self._points('neg')

    @property
    def aff_win(self):
        return self.aff_points

    @property
    def neg_win(self):
        return self.neg_points

class DebateTeam(models.Model):
    POSITION_AFFIRMATIVE = 'A'
    POSITION_NEGATIVE = 'N'
    POSITION_CHOICES = (
        (POSITION_AFFIRMATIVE, 'Affirmative'),
        (POSITION_NEGATIVE, 'Negative'),
    )
    
    debate = models.ForeignKey(Debate)
    team = models.ForeignKey(Team)
    position = models.CharField(max_length=1, choices=POSITION_CHOICES)
    
class DebateAdjudicator(models.Model):
    TYPE_CHAIR = 'C'
    TYPE_PANEL = 'P'
    TYPE_TRAINEE = 'T'

    TYPE_CHOICES = (
        (TYPE_CHAIR, 'Chair'),
        (TYPE_PANEL, 'Panel'),
        (TYPE_TRAINEE, 'Trainee'),
    )
    
    debate = models.ForeignKey(Debate)
    adjudicator = models.ForeignKey(Adjudicator)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)

class AdjudicatorFeedback(models.Model):
    adjudicator = models.ForeignKey(Adjudicator)
    score = models.FloatField()

    source_adjudicator = models.ForeignKey(DebateAdjudicator, blank=True,
                                           null=True)
    source_team = models.ForeignKey(DebateTeam, blank=True, null=True)
    

class AdjudicatorAllocation(object):
    def __init__(self, debate=None):
        self.debate = debate
        self.chair = None
        self.panel = []
        self.trainees = []

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

        if not self.debate:
            raise
        DebateAdjudicator.objects.filter(debate=self.debate).delete()
        self.chair = None
        self.panel = []
        self.trainees = []

    def save(self):
        if not self.debate:
            raise
        DebateAdjudicator.objects.filter(debate=self.debate).delete()
        for t, adj in self:
            if isinstance(adj, Adjudicator):
                adj = adj.id
            DebateAdjudicator(
                debate = self.debate,
                adjudicator_id = adj,
                type = t,
            ).save()

class TeamScoreSheet(models.Model):
    # unused
    debate_adjudicator = models.ForeignKey(DebateAdjudicator)
    debate_team = models.ForeignKey(DebateTeam)
    points = models.IntegerField()

    @property
    def debate(self):
        return self.debate_team.debate
    
class SpeakerScoreSheet(models.Model):
    # unused 
    debate_adjudicator = models.ForeignKey(DebateAdjudicator)
    debate_team = models.ForeignKey(DebateTeam)
    speaker = models.ForeignKey(Speaker)
    score = ScoreField()
    position = models.IntegerField()

    @property
    def debate(self):
        return self.debate_team.debate
    
class TeamScore(models.Model):
    debate_team = models.ForeignKey(DebateTeam)
    points = models.PositiveSmallIntegerField()
    score = ScoreField()

class SpeakerScore(models.Model):
    debate_team = models.ForeignKey(DebateTeam)
    speaker = models.ForeignKey(Speaker)
    score = ScoreField()
    position = models.IntegerField()

