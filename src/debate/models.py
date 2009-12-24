import random

from django.db import models

from debate.utils import pair_list

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
    
    def seen(self, other):
        # TODO
        return False
    
    def same_institution(self, other):
        return self.institution_id == other.institution_id


class Speaker(models.Model):
    name = models.CharField(max_length=40)
    team = models.ForeignKey(Team)

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
    TYPE_CHOICES = (
        ('R', 'Random'),
        ('P', 'Preliminary'),
        ('B', 'Break'),
    )
    
    STATUS_DRAFT = 0
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
    )
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT)
    #preceded
    
    tournament = Tournament()

    active_venues = models.ManyToManyField('Venue', through='ActiveVenue')
    active_adjudicators = models.ManyToManyField('Adjudicator')
    active_teams = models.ManyToManyField('Team')

    def __unicode__(self):
        return unicode(self.id)
    
    def debates(self):
        return Debate.objects.filter(round=self)
    
    def draw(self, drawer):
        d = drawer(self)
        self.make_debates(d.get_draw())
        
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
    round = models.ForeignKey(Round)
    venue = models.ForeignKey(Venue)
    
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
    TYPE_CHOICES = (
        ('C', 'Chair'),
        ('P1', 'Panel 1'),
    )
    
    debate = models.ForeignKey(Debate)
    adjudicator = models.ForeignKey(Adjudicator)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    
class TeamScoreSheet(models.Model):
    adjudicator_allocation = models.ForeignKey(AdjudicatorAllocation)
    debate_team = models.ForeignKey(DebateTeam)
    score = models.FloatField()
    
class SpeakerScoreSheet(models.Model):
    adjudicator_allocation = models.ForeignKey(AdjudicatorAllocation)
    debate_team = models.ForeignKey(DebateTeam)
    debater = models.ForeignKey(Speaker)
    score = models.FloatField()
    position = models.IntegerField()
    
    

 
