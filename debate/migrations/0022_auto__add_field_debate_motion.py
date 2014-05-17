# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Debate.motion'
        db.add_column(u'debate_debate', 'motion',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Motion'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Debate.motion'
        db.delete_column(u'debate_debate', 'motion_id')


    models = {
        u'debate.activeadjudicator': {
            'Meta': {'unique_together': "[('adjudicator', 'round')]", 'object_name': 'ActiveAdjudicator'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Adjudicator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']"})
        },
        u'debate.activeteam': {
            'Meta': {'unique_together': "[('team', 'round')]", 'object_name': 'ActiveTeam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']"}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Team']"})
        },
        u'debate.activevenue': {
            'Meta': {'unique_together': "[('venue', 'round')]", 'object_name': 'ActiveVenue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']"}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Venue']"})
        },
        u'debate.adjudicator': {
            'Meta': {'object_name': 'Adjudicator', '_ormbases': [u'debate.Person']},
            'conflicts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['debate.Team']", 'through': u"orm['debate.AdjudicatorConflict']", 'symmetrical': 'False'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Institution']"}),
            'institution_conflicts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'adjudicator_institution_conflicts'", 'symmetrical': 'False', 'through': u"orm['debate.AdjudicatorInstitutionConflict']", 'to': u"orm['debate.Institution']"}),
            'is_trainee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['debate.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'test_score': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'debate.adjudicatorconflict': {
            'Meta': {'object_name': 'AdjudicatorConflict'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Adjudicator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Team']"})
        },
        u'debate.adjudicatorfeedback': {
            'Meta': {'object_name': 'AdjudicatorFeedback'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Adjudicator']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'source_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateAdjudicator']", 'null': 'True', 'blank': 'True'}),
            'source_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']", 'null': 'True', 'blank': 'True'})
        },
        u'debate.adjudicatorinstitutionconflict': {
            'Meta': {'object_name': 'AdjudicatorInstitutionConflict'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Adjudicator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Institution']"})
        },
        u'debate.checkin': {
            'Meta': {'object_name': 'Checkin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Person']"}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']"})
        },
        u'debate.config': {
            'Meta': {'object_name': 'Config'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Tournament']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'debate.debate': {
            'Meta': {'object_name': 'Debate'},
            'bracket': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'motion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Motion']", 'null': 'True', 'blank': 'True'}),
            'result_status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'room_rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']"}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Venue']", 'null': 'True', 'blank': 'True'})
        },
        u'debate.debateadjudicator': {
            'Meta': {'object_name': 'DebateAdjudicator'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Adjudicator']"}),
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Debate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        u'debate.debateteam': {
            'Meta': {'object_name': 'DebateTeam'},
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Debate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Team']"})
        },
        u'debate.institution': {
            'Meta': {'unique_together': "(('tournament', 'code'),)", 'object_name': 'Institution'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Tournament']"})
        },
        u'debate.motion': {
            'Meta': {'object_name': 'Motion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'debate.person': {
            'Meta': {'object_name': 'Person'},
            'barcode_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'checkin_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'debate.round': {
            'Meta': {'unique_together': "(('tournament', 'seq'),)", 'object_name': 'Round'},
            'active_adjudicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['debate.Adjudicator']", 'through': u"orm['debate.ActiveAdjudicator']", 'symmetrical': 'False'}),
            'active_teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['debate.Team']", 'through': u"orm['debate.ActiveTeam']", 'symmetrical': 'False'}),
            'active_venues': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['debate.Venue']", 'through': u"orm['debate.ActiveVenue']", 'symmetrical': 'False'}),
            'adjudicator_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'checkins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'checkedin_rounds'", 'symmetrical': 'False', 'through': u"orm['debate.Checkin']", 'to': u"orm['debate.Person']"}),
            'draw_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feedback_weight': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'seq': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rounds'", 'to': u"orm['debate.Tournament']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'venue_status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'debate.speaker': {
            'Meta': {'object_name': 'Speaker', '_ormbases': [u'debate.Person']},
            u'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['debate.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Team']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'})
        },
        u'debate.speakerscore': {
            'Meta': {'unique_together': "[('debate_team', 'speaker', 'position')]", 'object_name': 'SpeakerScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Speaker']"})
        },
        u'debate.speakerscorebyadj': {
            'Meta': {'unique_together': "[('debate_adjudicator', 'debate_team', 'position')]", 'object_name': 'SpeakerScoreByAdj'},
            'debate_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateAdjudicator']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        u'debate.team': {
            'Meta': {'unique_together': "[('name', 'institution')]", 'object_name': 'Team'},
            'cannot_break': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Institution']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'})
        },
        u'debate.teamscore': {
            'Meta': {'object_name': 'TeamScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        u'debate.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'current_round': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tournament_'", 'null': 'True', 'to': u"orm['debate.Round']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'debate.venue': {
            'Meta': {'object_name': 'Venue'},
            'group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Tournament']"})
        }
    }

    complete_apps = ['debate']