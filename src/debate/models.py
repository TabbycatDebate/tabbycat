import random

from django.db import models

from debate.utils import pair_list

class Tournament(object):
    def get_teams(self):
        return Team.objects.all()
    teams = property(get_teams)
    
    def get_active_venues(self):
        return Venue.active.all()
    active_venues = property(get_active_venues)
    

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

class Speaker(models.Model):
    name = models.CharField(max_length=40)
    team = models.ForeignKey(Team)

class AdjudicatorManager(models.Manager):
    def activate_all(self):
        self.update(is_active=True)
    def deactivate_all(self):
        self.update(is_active=False)

class ActiveManager(models.Manager):
    def __init__(self, status):
        super(ActiveManager, self).__init__()
        self.status = status
        
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(is_active=self.status)

class AdjudicatorActiveManager(AdjudicatorManager, ActiveManager):
    def __init__(self, status):
        super(AdjudicatorActiveManager, self).__init__(status)
    
class Adjudicator(models.Model):
    name = models.CharField(max_length=40)
    institution = models.ForeignKey(Institution)
    is_active = models.BooleanField()
    
    objects = AdjudicatorManager()
    active = AdjudicatorActiveManager(True)
    inactive = AdjudicatorActiveManager(False)
    
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
    
    def debates(self):
        return Debate.objects.filter(round=self)
    
    class DrawError(Exception):
        pass
    
    def _draw_get_teams(self):
        if not self.status == self.STATUS_DRAFT:
            raise DrawError()
        
        teams = list(self.tournament.teams)
        
        if not len(teams) % 2 == 0:
            raise DrawError()
        return teams
    
    def draw_random(self):
        teams = self._draw_get_teams()
        
        random.shuffle(teams)
        pairs = pair_list(teams)
        self.make_debates(pairs)
        
    def draw_bracketed(self):
        teams = self._draw_get_teams()
        
        # create bracket data structure
        max_points = teams[0].total_points
        brackets = ([],) * (max_points + 1)
        for team in teams:
            brackets[team.total_points].append(team)
        # balance brackets from top down
        for i in range(max_points, -1, -1):
            if len(brackets[i]) % 2 != 0:
                # find next non-empty bracket
                idx = i - 1
                while len(brackets[idx]) == 0:
                    idx -= 1
                brackets[i].append(brackets[idx].pop(0))
                
        pairs = pair_list(teams)
        self.make_debates(pairs)
        
        
    def make_debates(self, pairs):
        venues = list(self.tournament.active_venues)
        
        for pair in pairs:
            debate = Debate(round=self, venue=venues.pop(0))
            debate.save()
            
            aff = DebateTeam(debate=debate, team=pair[0], position=DebateTeam.POSITION_AFFIRMATIVE)
            neg = DebateTeam(debate=debate, team=pair[1], position=DebateTeam.POSITION_NEGATIVE)
            
            aff.save()
            neg.save()
        
class Venue(models.Model):
    name = models.CharField(max_length=40)
    is_active = models.BooleanField()
    priority = models.IntegerField()
    
    objects = models.Manager()
    active = ActiveManager(True)
    inactive = ActiveManager(False)

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
    
    

 
