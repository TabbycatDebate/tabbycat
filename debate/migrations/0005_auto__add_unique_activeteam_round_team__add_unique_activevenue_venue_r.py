# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding unique constraint on 'ActiveTeam', fields ['round', 'team']
        db.create_unique('debate_activeteam', ['round_id', 'team_id'])

        # Adding unique constraint on 'ActiveVenue', fields ['venue', 'round']
        db.create_unique('debate_activevenue', ['venue_id', 'round_id'])

        # Adding unique constraint on 'TeamScoreSheet', fields ['debate_adjudicator', 'debate_team']
        db.create_unique('debate_teamscoresheet', ['debate_adjudicator_id', 'debate_team_id'])

        # Adding unique constraint on 'ActiveAdjudicator', fields ['adjudicator', 'round']
        db.create_unique('debate_activeadjudicator', ['adjudicator_id', 'round_id'])

        # Adding unique constraint on 'SpeakerScoreSheet', fields ['debate_adjudicator', 'speaker']
        db.create_unique('debate_speakerscoresheet', ['debate_adjudicator_id', 'speaker_id'])

        # Adding unique constraint on 'TeamScore', fields ['debate_team']
        db.create_unique('debate_teamscore', ['debate_team_id'])

        # Adding unique constraint on 'Institution', fields ['code']
        db.create_unique('debate_institution', ['code'])

        # Adding unique constraint on 'Institution', fields ['name']
        db.create_unique('debate_institution', ['name'])

        # Adding unique constraint on 'SpeakerScore', fields ['position', 'debate_team', 'speaker']
        db.create_unique('debate_speakerscore', ['position', 'debate_team_id', 'speaker_id'])

        # Adding unique constraint on 'Team', fields ['name', 'institution']
        db.create_unique('debate_team', ['name', 'institution_id'])
    
    
    def backwards(self, orm):
        
        # Removing unique constraint on 'ActiveTeam', fields ['round', 'team']
        db.delete_unique('debate_activeteam', ['round_id', 'team_id'])

        # Removing unique constraint on 'ActiveVenue', fields ['venue', 'round']
        db.delete_unique('debate_activevenue', ['venue_id', 'round_id'])

        # Removing unique constraint on 'TeamScoreSheet', fields ['debate_adjudicator', 'debate_team']
        db.delete_unique('debate_teamscoresheet', ['debate_adjudicator_id', 'debate_team_id'])

        # Removing unique constraint on 'ActiveAdjudicator', fields ['adjudicator', 'round']
        db.delete_unique('debate_activeadjudicator', ['adjudicator_id', 'round_id'])

        # Removing unique constraint on 'SpeakerScoreSheet', fields ['debate_adjudicator', 'speaker']
        db.delete_unique('debate_speakerscoresheet', ['debate_adjudicator_id', 'speaker_id'])

        # Removing unique constraint on 'TeamScore', fields ['debate_team']
        db.delete_unique('debate_teamscore', ['debate_team_id'])

        # Removing unique constraint on 'Institution', fields ['code']
        db.delete_unique('debate_institution', ['code'])

        # Removing unique constraint on 'Institution', fields ['name']
        db.delete_unique('debate_institution', ['name'])

        # Removing unique constraint on 'SpeakerScore', fields ['position', 'debate_team', 'speaker']
        db.delete_unique('debate_speakerscore', ['position', 'debate_team_id', 'speaker_id'])

        # Removing unique constraint on 'Team', fields ['name', 'institution']
        db.delete_unique('debate_team', ['name', 'institution_id'])
    
    
    models = {
        'debate.activeadjudicator': {
            'Meta': {'unique_together': "[('adjudicator', 'round')]", 'object_name': 'ActiveAdjudicator'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Adjudicator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"})
        },
        'debate.activeteam': {
            'Meta': {'unique_together': "[('team', 'round')]", 'object_name': 'ActiveTeam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Team']"})
        },
        'debate.activevenue': {
            'Meta': {'unique_together': "[('venue', 'round')]", 'object_name': 'ActiveVenue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Venue']"})
        },
        'debate.adjudicator': {
            'Meta': {'object_name': 'Adjudicator'},
            'conflicts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Team']", 'through': "orm['debate.AdjudicatorConflict']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Institution']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'test_score': ('django.db.models.fields.FloatField', [], {})
        },
        'debate.adjudicatorconflict': {
            'Meta': {'object_name': 'AdjudicatorConflict'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Adjudicator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Team']"})
        },
        'debate.adjudicatorfeedback': {
            'Meta': {'object_name': 'AdjudicatorFeedback'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Adjudicator']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'source_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateAdjudicator']", 'null': 'True', 'blank': 'True'}),
            'source_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']", 'null': 'True', 'blank': 'True'})
        },
        'debate.config': {
            'Meta': {'object_name': 'Config'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Tournament']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'debate.debate': {
            'Meta': {'object_name': 'Debate'},
            'bracket': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'result_status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Venue']", 'null': 'True', 'blank': 'True'})
        },
        'debate.debateadjudicator': {
            'Meta': {'object_name': 'DebateAdjudicator'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Adjudicator']"}),
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Debate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'debate.debateteam': {
            'Meta': {'object_name': 'DebateTeam'},
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Debate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Team']"})
        },
        'debate.institution': {
            'Meta': {'object_name': 'Institution'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Tournament']"})
        },
        'debate.round': {
            'Meta': {'unique_together': "(('tournament', 'seq'),)", 'object_name': 'Round'},
            'active_adjudicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Adjudicator']", 'through': "orm['debate.ActiveAdjudicator']", 'symmetrical': 'False'}),
            'active_teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Team']", 'through': "orm['debate.ActiveTeam']", 'symmetrical': 'False'}),
            'active_venues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Venue']", 'through': "orm['debate.ActiveVenue']", 'symmetrical': 'False'}),
            'adjudicator_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'draw_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feedback_weight': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'seq': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rounds'", 'to': "orm['debate.Tournament']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'venue_status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'debate.speaker': {
            'Meta': {'object_name': 'Speaker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Team']"})
        },
        'debate.speakerscore': {
            'Meta': {'unique_together': "[('debate_team', 'speaker', 'position')]", 'object_name': 'SpeakerScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Speaker']"})
        },
        'debate.speakerscoresheet': {
            'Meta': {'unique_together': "[('debate_adjudicator', 'speaker')]", 'object_name': 'SpeakerScoreSheet'},
            'debate_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateAdjudicator']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Speaker']"})
        },
        'debate.team': {
            'Meta': {'unique_together': "[('name', 'institution')]", 'object_name': 'Team'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Institution']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'debate.teamscore': {
            'Meta': {'object_name': 'TeamScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        'debate.teamscoresheet': {
            'Meta': {'unique_together': "[('debate_adjudicator', 'debate_team')]", 'object_name': 'TeamScoreSheet'},
            'debate_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateAdjudicator']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {})
        },
        'debate.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'current_round': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tournament_'", 'null': 'True', 'to': "orm['debate.Round']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'debate.venue': {
            'Meta': {'object_name': 'Venue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Tournament']"})
        }
    }
    
    complete_apps = ['debate']
