# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Tournament'
        db.create_table('debate_tournament', (
            ('current_round', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tournament_', null=True, to=orm['debate.Round'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
        ))
        db.send_create_signal('debate', ['Tournament'])

        # Adding model 'Institution'
        db.create_table('debate_institution', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Tournament'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('debate', ['Institution'])

        # Adding model 'Team'
        db.create_table('debate_team', (
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Institution'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('debate', ['Team'])

        # Adding model 'Speaker'
        db.create_table('debate_speaker', (
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('debate', ['Speaker'])

        # Adding model 'Adjudicator'
        db.create_table('debate_adjudicator', (
            ('test_score', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Institution'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('debate', ['Adjudicator'])

        # Adding model 'AdjudicatorConflict'
        db.create_table('debate_adjudicatorconflict', (
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
        ))
        db.send_create_signal('debate', ['AdjudicatorConflict'])

        # Adding model 'Round'
        db.create_table('debate_round', (
            ('draw_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('seq', self.gf('django.db.models.fields.IntegerField')()),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rounds', to=orm['debate.Tournament'])),
            ('venue_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('adjudicator_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('feedback_weight', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['Round'])

        # Adding unique constraint on 'Round', fields ['tournament', 'seq']
        db.create_unique('debate_round', ['tournament_id', 'seq'])

        # Adding model 'Venue'
        db.create_table('debate_venue', (
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('debate', ['Venue'])

        # Adding model 'ActiveVenue'
        db.create_table('debate_activevenue', (
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Venue'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal('debate', ['ActiveVenue'])

        # Adding model 'ActiveTeam'
        db.create_table('debate_activeteam', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
        ))
        db.send_create_signal('debate', ['ActiveTeam'])

        # Adding model 'ActiveAdjudicator'
        db.create_table('debate_activeadjudicator', (
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal('debate', ['ActiveAdjudicator'])

        # Adding model 'Debate'
        db.create_table('debate_debate', (
            ('importance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('result_status', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Venue'], null=True, blank=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
            ('bracket', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['Debate'])

        # Adding model 'DebateTeam'
        db.create_table('debate_debateteam', (
            ('position', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Debate'])),
        ))
        db.send_create_signal('debate', ['DebateTeam'])

        # Adding model 'DebateAdjudicator'
        db.create_table('debate_debateadjudicator', (
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Debate'])),
        ))
        db.send_create_signal('debate', ['DebateAdjudicator'])

        # Adding model 'AdjudicatorFeedback'
        db.create_table('debate_adjudicatorfeedback', (
            ('source_adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateAdjudicator'], null=True, blank=True)),
            ('source_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'], null=True, blank=True)),
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('score', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['AdjudicatorFeedback'])

        # Adding model 'TeamScoreSheet'
        db.create_table('debate_teamscoresheet', (
            ('debate_adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateAdjudicator'])),
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('points', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['TeamScoreSheet'])

        # Adding model 'SpeakerScoreSheet'
        db.create_table('debate_speakerscoresheet', (
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('score', self.gf('debate.models.ScoreField')()),
            ('speaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Speaker'])),
            ('debate_adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateAdjudicator'])),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['SpeakerScoreSheet'])

        # Adding model 'TeamScore'
        db.create_table('debate_teamscore', (
            ('score', self.gf('debate.models.ScoreField')()),
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('points', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['TeamScore'])

        # Adding model 'SpeakerScore'
        db.create_table('debate_speakerscore', (
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('score', self.gf('debate.models.ScoreField')()),
            ('speaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Speaker'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('debate', ['SpeakerScore'])

        # Adding model 'Config'
        db.create_table('debate_config', (
            ('value', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Tournament'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('debate', ['Config'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Tournament'
        db.delete_table('debate_tournament')

        # Deleting model 'Institution'
        db.delete_table('debate_institution')

        # Deleting model 'Team'
        db.delete_table('debate_team')

        # Deleting model 'Speaker'
        db.delete_table('debate_speaker')

        # Deleting model 'Adjudicator'
        db.delete_table('debate_adjudicator')

        # Deleting model 'AdjudicatorConflict'
        db.delete_table('debate_adjudicatorconflict')

        # Deleting model 'Round'
        db.delete_table('debate_round')

        # Removing unique constraint on 'Round', fields ['tournament', 'seq']
        db.delete_unique('debate_round', ['tournament_id', 'seq'])

        # Deleting model 'Venue'
        db.delete_table('debate_venue')

        # Deleting model 'ActiveVenue'
        db.delete_table('debate_activevenue')

        # Deleting model 'ActiveTeam'
        db.delete_table('debate_activeteam')

        # Deleting model 'ActiveAdjudicator'
        db.delete_table('debate_activeadjudicator')

        # Deleting model 'Debate'
        db.delete_table('debate_debate')

        # Deleting model 'DebateTeam'
        db.delete_table('debate_debateteam')

        # Deleting model 'DebateAdjudicator'
        db.delete_table('debate_debateadjudicator')

        # Deleting model 'AdjudicatorFeedback'
        db.delete_table('debate_adjudicatorfeedback')

        # Deleting model 'TeamScoreSheet'
        db.delete_table('debate_teamscoresheet')

        # Deleting model 'SpeakerScoreSheet'
        db.delete_table('debate_speakerscoresheet')

        # Deleting model 'TeamScore'
        db.delete_table('debate_teamscore')

        # Deleting model 'SpeakerScore'
        db.delete_table('debate_speakerscore')

        # Deleting model 'Config'
        db.delete_table('debate_config')
    
    
    models = {
        'debate.activeadjudicator': {
            'Meta': {'object_name': 'ActiveAdjudicator'},
            'adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Adjudicator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"})
        },
        'debate.activeteam': {
            'Meta': {'object_name': 'ActiveTeam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Round']"}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Team']"})
        },
        'debate.activevenue': {
            'Meta': {'object_name': 'ActiveVenue'},
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
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
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
            'Meta': {'object_name': 'SpeakerScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Speaker']"})
        },
        'debate.speakerscoresheet': {
            'Meta': {'object_name': 'SpeakerScoreSheet'},
            'debate_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateAdjudicator']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Speaker']"})
        },
        'debate.team': {
            'Meta': {'object_name': 'Team'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.Institution']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'debate.teamscore': {
            'Meta': {'object_name': 'TeamScore'},
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debate.DebateTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        'debate.teamscoresheet': {
            'Meta': {'object_name': 'TeamScoreSheet'},
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
            'priority': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['debate']
