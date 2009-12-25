from django.db import models

from debate.utils import pair_list
from debate.draw import RandomDrawNoConflict
from debate.adjudicator import AdjAllocation, DumbAdjAllocator

class Tournament(object):
    def _get_teams(self):
        return Team.objects.all()
    teams = property(_get_teams)

    def _get_current_round(self):
        try:
            return Round.objects.order_by('-id')[0]
        except IndexError:
            return None
    current_round = property(_get_current_round)
    
class Institution(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=40)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.code, self.name)

class Team(models.Model):
    name = models.CharField(max_length=50)
    institution = models.ForeignKey(Institution)
    is_active = models.BooleanField()
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)
    
    def _get_points(self):
        # TODO
        return 0
    points = property(_get_points)
    
    def _get_aff_count(self):
        # TODO
        return 0
    aff_count = property(_get_aff_count)
    
    def _get_neg_count(self):
        # TODO
        return 0
    neg_count = property(_get_neg_count)

    def _get_debates(self, before_round=None):
        dts = DebateTeam.objects.select_related('debate').filter(team=self)
        if before_round is not None:
            dts = dts.filter(debate__round__seq__lt=before_round)
        if not hasattr(self, '_debates'):
            self._debates = [dt.debate for dt in dts]
        return self._debates
    debates = property(_get_debates)
    
    def seen(self, other, before_round=None):
        debates = self._get_debates(before_round)

        return len([1 for d in self.debates if other in d])

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

    def _get_speakers(self):
        if not hasattr(self, '_speakers'):
            self._speakers = self.speaker_set.all()
        return self._speakers
    speakers = property(_get_speakers)


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

class AdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('Adjudicator')
    team = models.ForeignKey('Team')

class Round(models.Model):
    TYPE_RANDOM = 'R'
    TYPE_PRELIM = 'P'
    TYPE_CHOICES = (
        (TYPE_RANDOM, 'Random'),
        (TYPE_PRELIM, 'Preliminary'),
        ('B', 'Break'),
    )

    DRAW_CLASS = {
        TYPE_RANDOM: RandomDrawNoConflict,
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
    
    tournament = Tournament()

    active_venues = models.ManyToManyField('Venue', through='ActiveVenue')
    active_adjudicators = models.ManyToManyField('Adjudicator',
                                                 through='ActiveAdjudicator')
    active_teams = models.ManyToManyField('Team', through='ActiveTeam')

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
        self.make_adj_allocation(allocator.get_allocation())
        self.adjudicator_status = self.STATUS_DRAFT
        self.save()

    def make_adj_allocation(self, allocation):
        def make(debate, adj, type):
            AdjudicatorAllocation(debate=debate, adjudicator=adj,
                                  type=type).save()

        for debate, alloc in allocation:
            make(debate, alloc.chair, AdjudicatorAllocation.TYPE_CHAIR)
            for adj in alloc.panel:
                make(debate, adj, AdjudicatorAllocation.TYPE_PANEL)
            for adj in alloc.trainees:
                make(debate, adj, AdjudicatorAllocation.TYPE_TRAINEE)

    def get_draw(self):
        return Debate.objects.filter(round=self)
        
    def make_debates(self, pairs):
        venues = list(self.active_venues.all())
        
        for pair in pairs:
            debate = Debate(round=self, venue=venues.pop(0))
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

    def adjudicator_availability(self):
        return self.base_availability(Adjudicator, 'debate_activeadjudicator', 
                                      'adjudicator_id',
                                      'debate_adjudicator')

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
    venue = models.ForeignKey(Venue)
    bracket = models.IntegerField(default=0)
    result_status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                                    default=STATUS_NONE)

    def _get_teams(self):
        if not hasattr(self, '_team_cache'):
            self._team_cache = {}

            for t in DebateTeam.objects.filter(debate=self):
                self._team_cache[t.position] = t

    def _get_aff_team(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_AFFIRMATIVE].team
    aff_team = property(_get_aff_team)

    def _get_neg_team(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_NEGATIVE].team
    neg_team = property(_get_neg_team)

    def _get_aff_dt(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_AFFIRMATIVE]
    aff_dt = property(_get_aff_dt)

    def _get_neg_dt(self):
        self._get_teams()
        return self._team_cache[DebateTeam.POSITION_NEGATIVE]
    neg_dt = property(_get_neg_dt)

    def _get_draw_conflicts(self):
        if not hasattr(self, '_draw_conflicts'):
            self._draw_conflicts = []
            history = self.aff_team.seen(self.neg_team, before_round=self.round.seq)
            if history:
                self._draw_conflicts.append("History (%d)" % history)
            if self.aff_team.institution == self.neg_team.institution:
                self._draw_conflicts.append("Institution")

        return ", ".join(self._draw_conflicts) 
    draw_conflicts = property(_get_draw_conflicts)

    def _get_adjudicators(self):
        if not hasattr(self, '_adjudicators'):
            adjs = AdjudicatorAllocation.objects.filter(debate=self)
            alloc = AdjAllocation()
            for a in adjs:
                if a.type == a.TYPE_CHAIR:
                    alloc.chair = a.adjudicator
                if a.type == a.TYPE_PANEL:
                    alloc.panel.append(a.adjudicator)
                if a.type == a.TYPE_TRAINEE:
                    alloc.trainees.append(a.adjudicator)
            self._adjudicators = alloc
        return self._adjudicators


    def _get_adjudicators_display(self):
        if not hasattr(self, '_adjudicators_display'):
            alloc = self._get_adjudicators()

            s = alloc.chair.name
            if alloc.panel:
                s += " (c), "
            elif alloc.trainees:
                s += ", "
            sd = [p.name for p in alloc.panel]
            sd.extend(["%s (t)" % t.name for t in alloc.trainees])
            s += ", ".join(sd)

            self._adjudicators_display = s
        return self._adjudicators_display
    adjudicators_display = property(_get_adjudicators_display)


    def __contains__(self, team):
        return team in (self.aff_team, self.neg_team) 

    def __unicode__(self):
        return u'%s vs %s' % (self.aff_team.name, self.neg_team.name)
    
class DebateResult(object):
    def __init__(self, debate):
        self.debate = debate

        self._init_team('aff')
        self._init_team('neg')

    def _init_team(self, team):
        speakers = dict((i, None) for i in range(1, 5))
        scores = dict((i, None) for i in range(1, 5))
        dt = getattr(self.debate, '%s_dt' % team)

        for sss in SpeakerScoreSheet.objects.filter(debate_team=dt):
            setattr(sss.speaker, 'score', sss.score)
            speakers[sss.position] = sss.speaker

        setattr(self, '%s_speakers' % team, speakers)

        try:
            team_score = TeamScoreSheet.objects.get(debate_team=dt).score
        except TeamScoreSheet.DoesNotExist:
            team_score = None

        setattr(self, '%s_score' % team, team_score)

    # adding these methods programmatically would require a bit too much
    # crazy black magic
    def _get_aff_speaker_1(self):
        return self.aff_speakers[1]
    aff_speaker_1 = property(_get_aff_speaker_1)

    def _get_aff_speaker_2(self):
        return self.aff_speakers[2]
    aff_speaker_2 = property(_get_aff_speaker_2)

    def _get_aff_speaker_3(self):
        return self.aff_speakers[3]
    aff_speaker_3 = property(_get_aff_speaker_3)

    def _get_aff_speaker_4(self):
        return self.aff_speakers[4]
    aff_speaker_4 = property(_get_aff_speaker_4)

    def _get_neg_speaker_1(self):
        return self.neg_speakers[1]
    neg_speaker_1 = property(_get_neg_speaker_1)

    def _get_neg_speaker_2(self):
        return self.neg_speakers[2]
    neg_speaker_2 = property(_get_neg_speaker_2)

    def _get_neg_speaker_3(self):
        return self.neg_speakers[3]
    neg_speaker_3 = property(_get_neg_speaker_3)

    def _get_neg_speaker_4(self):
        return self.neg_speakers[4]
    neg_speaker_4 = property(_get_neg_speaker_4)


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
    
class AdjudicatorAllocation(models.Model):
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
    
class TeamScoreSheet(models.Model):
    # TODO: review scoresheet for adjudicator
    # adjudicator_allocation = models.ForeignKey(AdjudicatorAllocation)
    debate_team = models.ForeignKey(DebateTeam)
    score = models.FloatField()

    def _get_debate(self):
        return self.debate_team.debate
    debate = property(_get_debate)
    
class SpeakerScoreSheet(models.Model):
    # TODO: review scoresheet for adjudicator
    # adjudicator_allocation = models.ForeignKey(AdjudicatorAllocation)
    debate_team = models.ForeignKey(DebateTeam)
    speaker = models.ForeignKey(Speaker)
    score = models.FloatField()
    position = models.IntegerField()

    def _get_debate(self):
        return self.debate_team.debate
    debate = property(_get_debate)
    
    

 
