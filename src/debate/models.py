import random

from django.db import models

from debate.utils import pair_list

class Tournament(object):
    def _get_teams(self):
        return Team.objects.all()
    teams = property(_get_teams)

    def _get_current_round(self):
        return Round.objects.order_by('-id')[0]
    current_round = property(_get_current_round)
    
class Institution(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    
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
   
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.institution.code)

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

    active_venues = models.ManyToManyField('Venue')
    active_adjudicators = models.ManyToManyField('Adjudicator')

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
        
class Venue(models.Model):
    name = models.CharField(max_length=40)
    priority = models.IntegerField()
    
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
    
    

 
