# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Adjudicator.cv_score'
        db.delete_column('debate_adjudicator', 'cv_score')
    
    
    def backwards(self, orm):
        
        # Adding field 'Adjudicator.cv_score'
        db.add_column('debate_adjudicator', 'cv_score', self.gf('django.db.models.fields.FloatField')(default=0), keep_default=False)
    
    
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
            'Meta': {'object_name': 'Adjudicator', '_ormbases': ['debate.Person']},
            'conflicts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Team']", 'through': "orm['debate.AdjudicatorConflict']", 'symmetrical': 'False'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Institution']"}),
            'is_trainee': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['debate.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'test_score': ('django.db.models.fields.FloatField', [], {'default': '0'})
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
        'debate.checkin': {
            'Meta': {'object_name': 'Checkin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Person']"}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"})
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
            'room_rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'Meta': {'unique_together': "(('tournament', 'code'),)", 'object_name': 'Institution'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Tournament']"})
        },
        'debate.person': {
            'Meta': {'object_name': 'Person'},
            'barcode_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'debate.round': {
            'Meta': {'unique_together': "(('tournament', 'seq'),)", 'object_name': 'Round'},
            'active_adjudicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Adjudicator']", 'through': "orm['debate.ActiveAdjudicator']", 'symmetrical': 'False'}),
            'active_teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Team']", 'through': "orm['debate.ActiveTeam']", 'symmetrical': 'False'}),
            'active_venues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['debate.Venue']", 'through': "orm['debate.ActiveVenue']", 'symmetrical': 'False'}),
            'adjudicator_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'checkins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'checkedin_rounds'", 'symmetrical': 'False', 'through': "orm['debate.Checkin']", 'to': "orm['debate.Person']"}),
            'draw_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feedback_weight': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'seq': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rounds'", 'to': "orm['debate.Tournament']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'venue_status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'debate.speaker': {
            'Meta': {'object_name': 'Speaker', '_ormbases': ['debate.Person']},
            'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['debate.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Team']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'})
        },
        'debate.speakerscore': {
            'Meta': {'unique_together': "[('debate_team', 'speaker', 'position')]", 'object_name': 'SpeakerScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Speaker']"})
        },
        'debate.speakerscorebyadj': {
            'Meta': {'unique_together': "[('debate_adjudicator', 'debate_team', 'position')]", 'object_name': 'SpeakerScoreByAdj'},
            'debate_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateAdjudicator']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        'debate.team': {
            'Meta': {'unique_together': "[('name', 'institution')]", 'object_name': 'Team'},
            'cannot_break': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Institution']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'})
        },
        'debate.teamscore': {
            'Meta': {'object_name': 'TeamScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        'debate.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'current_round': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tournament_'", 'null': 'True', 'to': "orm['debate.Round']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'debate.venue': {
            'Meta': {'object_name': 'Venue'},
            'group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Tournament']"})
        }
    }
    
    complete_apps = ['debate']
