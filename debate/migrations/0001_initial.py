# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tournament'
        db.create_table(u'debate_tournament', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('current_round', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tournament_', null=True, to=orm['debate.Round'])),
        ))
        db.send_create_signal(u'debate', ['Tournament'])

        # Adding model 'Institution'
        db.create_table(u'debate_institution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Tournament'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(default='', max_length=8)),
        ))
        db.send_create_signal(u'debate', ['Institution'])

        # Adding unique constraint on 'Institution', fields ['tournament', 'code']
        db.create_unique(u'debate_institution', ['tournament_id', 'code'])

        # Adding model 'Team'
        db.create_table(u'debate_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Institution'])),
            ('use_institution_prefix', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('cannot_break', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
        ))
        db.send_create_signal(u'debate', ['Team'])

        # Adding unique constraint on 'Team', fields ['reference', 'institution']
        db.create_unique(u'debate_team', ['reference', 'institution_id'])

        # Adding model 'Person'
        db.create_table(u'debate_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('barcode_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('checkin_message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'debate', ['Person'])

        # Adding model 'Checkin'
        db.create_table(u'debate_checkin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Person'])),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal(u'debate', ['Checkin'])

        # Adding model 'Speaker'
        db.create_table(u'debate_speaker', (
            (u'person_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['debate.Person'], unique=True, primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
        ))
        db.send_create_signal(u'debate', ['Speaker'])

        # Adding model 'Adjudicator'
        db.create_table(u'debate_adjudicator', (
            (u'person_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['debate.Person'], unique=True, primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Institution'])),
            ('test_score', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('is_trainee', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'debate', ['Adjudicator'])

        # Adding model 'AdjudicatorConflict'
        db.create_table(u'debate_adjudicatorconflict', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
        ))
        db.send_create_signal(u'debate', ['AdjudicatorConflict'])

        # Adding model 'AdjudicatorInstitutionConflict'
        db.create_table(u'debate_adjudicatorinstitutionconflict', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Institution'])),
        ))
        db.send_create_signal(u'debate', ['AdjudicatorInstitutionConflict'])

        # Adding model 'Round'
        db.create_table(u'debate_round', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rounds', to=orm['debate.Tournament'])),
            ('seq', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('draw_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('venue_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('adjudicator_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('feedback_weight', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'debate', ['Round'])

        # Adding unique constraint on 'Round', fields ['tournament', 'seq']
        db.create_unique(u'debate_round', ['tournament_id', 'seq'])

        # Adding model 'Venue'
        db.create_table(u'debate_venue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('group', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Tournament'])),
        ))
        db.send_create_signal(u'debate', ['Venue'])

        # Adding model 'ActiveVenue'
        db.create_table(u'debate_activevenue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Venue'])),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal(u'debate', ['ActiveVenue'])

        # Adding unique constraint on 'ActiveVenue', fields ['venue', 'round']
        db.create_unique(u'debate_activevenue', ['venue_id', 'round_id'])

        # Adding model 'ActiveTeam'
        db.create_table(u'debate_activeteam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal(u'debate', ['ActiveTeam'])

        # Adding unique constraint on 'ActiveTeam', fields ['team', 'round']
        db.create_unique(u'debate_activeteam', ['team_id', 'round_id'])

        # Adding model 'ActiveAdjudicator'
        db.create_table(u'debate_activeadjudicator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal(u'debate', ['ActiveAdjudicator'])

        # Adding unique constraint on 'ActiveAdjudicator', fields ['adjudicator', 'round']
        db.create_unique(u'debate_activeadjudicator', ['adjudicator_id', 'round_id'])

        # Adding model 'Debate'
        db.create_table(u'debate_debate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Venue'], null=True, blank=True)),
            ('bracket', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('room_rank', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('importance', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('result_status', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('ballot_in', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'debate', ['Debate'])

        # Adding model 'DebateTeam'
        db.create_table(u'debate_debateteam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Debate'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Team'])),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'debate', ['DebateTeam'])

        # Adding model 'DebateAdjudicator'
        db.create_table(u'debate_debateadjudicator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Debate'])),
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal(u'debate', ['DebateAdjudicator'])

        # Adding model 'AdjudicatorFeedback'
        db.create_table(u'debate_adjudicatorfeedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Adjudicator'])),
            ('score', self.gf('django.db.models.fields.FloatField')()),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source_adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateAdjudicator'], null=True, blank=True)),
            ('source_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'], null=True, blank=True)),
        ))
        db.send_create_signal(u'debate', ['AdjudicatorFeedback'])

        # Adding model 'BallotSubmission'
        db.create_table(u'debate_ballotsubmission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Debate'])),
            ('motion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Motion'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('submitter_type', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('copied_from', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.BallotSubmission'], null=True, blank=True)),
            ('discarded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'debate', ['BallotSubmission'])

        # Adding model 'SpeakerScoreByAdj'
        db.create_table(u'debate_speakerscorebyadj', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ballot_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.BallotSubmission'])),
            ('debate_adjudicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateAdjudicator'])),
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('score', self.gf('debate.models.ScoreField')()),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'debate', ['SpeakerScoreByAdj'])

        # Adding unique constraint on 'SpeakerScoreByAdj', fields ['debate_adjudicator', 'debate_team', 'position', 'ballot_submission']
        db.create_unique(u'debate_speakerscorebyadj', ['debate_adjudicator_id', 'debate_team_id', 'position', 'ballot_submission_id'])

        # Adding model 'TeamScore'
        db.create_table(u'debate_teamscore', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ballot_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.BallotSubmission'])),
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('points', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('score', self.gf('debate.models.ScoreField')()),
        ))
        db.send_create_signal(u'debate', ['TeamScore'])

        # Adding unique constraint on 'TeamScore', fields ['debate_team', 'ballot_submission']
        db.create_unique(u'debate_teamscore', ['debate_team_id', 'ballot_submission_id'])

        # Adding model 'SpeakerScore'
        db.create_table(u'debate_speakerscore', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ballot_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.BallotSubmission'])),
            ('debate_team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.DebateTeam'])),
            ('speaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Speaker'])),
            ('score', self.gf('debate.models.ScoreField')()),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'debate', ['SpeakerScore'])

        # Adding unique constraint on 'SpeakerScore', fields ['debate_team', 'speaker', 'position', 'ballot_submission']
        db.create_unique(u'debate_speakerscore', ['debate_team_id', 'speaker_id', 'position', 'ballot_submission_id'])

        # Adding model 'Motion'
        db.create_table(u'debate_motion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'])),
        ))
        db.send_create_signal(u'debate', ['Motion'])

        # Adding model 'ActionLog'
        db.create_table(u'debate_actionlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Debate'], null=True, blank=True)),
            ('adjudicator_feedback', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.AdjudicatorFeedback'], null=True, blank=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Round'], null=True, blank=True)),
            ('motion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Motion'], null=True, blank=True)),
        ))
        db.send_create_signal(u'debate', ['ActionLog'])

        # Adding model 'Config'
        db.create_table(u'debate_config', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['debate.Tournament'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'debate', ['Config'])


    def backwards(self, orm):
        # Removing unique constraint on 'SpeakerScore', fields ['debate_team', 'speaker', 'position', 'ballot_submission']
        db.delete_unique(u'debate_speakerscore', ['debate_team_id', 'speaker_id', 'position', 'ballot_submission_id'])

        # Removing unique constraint on 'TeamScore', fields ['debate_team', 'ballot_submission']
        db.delete_unique(u'debate_teamscore', ['debate_team_id', 'ballot_submission_id'])

        # Removing unique constraint on 'SpeakerScoreByAdj', fields ['debate_adjudicator', 'debate_team', 'position', 'ballot_submission']
        db.delete_unique(u'debate_speakerscorebyadj', ['debate_adjudicator_id', 'debate_team_id', 'position', 'ballot_submission_id'])

        # Removing unique constraint on 'ActiveAdjudicator', fields ['adjudicator', 'round']
        db.delete_unique(u'debate_activeadjudicator', ['adjudicator_id', 'round_id'])

        # Removing unique constraint on 'ActiveTeam', fields ['team', 'round']
        db.delete_unique(u'debate_activeteam', ['team_id', 'round_id'])

        # Removing unique constraint on 'ActiveVenue', fields ['venue', 'round']
        db.delete_unique(u'debate_activevenue', ['venue_id', 'round_id'])

        # Removing unique constraint on 'Round', fields ['tournament', 'seq']
        db.delete_unique(u'debate_round', ['tournament_id', 'seq'])

        # Removing unique constraint on 'Team', fields ['reference', 'institution']
        db.delete_unique(u'debate_team', ['reference', 'institution_id'])

        # Removing unique constraint on 'Institution', fields ['tournament', 'code']
        db.delete_unique(u'debate_institution', ['tournament_id', 'code'])

        # Deleting model 'Tournament'
        db.delete_table(u'debate_tournament')

        # Deleting model 'Institution'
        db.delete_table(u'debate_institution')

        # Deleting model 'Team'
        db.delete_table(u'debate_team')

        # Deleting model 'Person'
        db.delete_table(u'debate_person')

        # Deleting model 'Checkin'
        db.delete_table(u'debate_checkin')

        # Deleting model 'Speaker'
        db.delete_table(u'debate_speaker')

        # Deleting model 'Adjudicator'
        db.delete_table(u'debate_adjudicator')

        # Deleting model 'AdjudicatorConflict'
        db.delete_table(u'debate_adjudicatorconflict')

        # Deleting model 'AdjudicatorInstitutionConflict'
        db.delete_table(u'debate_adjudicatorinstitutionconflict')

        # Deleting model 'Round'
        db.delete_table(u'debate_round')

        # Deleting model 'Venue'
        db.delete_table(u'debate_venue')

        # Deleting model 'ActiveVenue'
        db.delete_table(u'debate_activevenue')

        # Deleting model 'ActiveTeam'
        db.delete_table(u'debate_activeteam')

        # Deleting model 'ActiveAdjudicator'
        db.delete_table(u'debate_activeadjudicator')

        # Deleting model 'Debate'
        db.delete_table(u'debate_debate')

        # Deleting model 'DebateTeam'
        db.delete_table(u'debate_debateteam')

        # Deleting model 'DebateAdjudicator'
        db.delete_table(u'debate_debateadjudicator')

        # Deleting model 'AdjudicatorFeedback'
        db.delete_table(u'debate_adjudicatorfeedback')

        # Deleting model 'BallotSubmission'
        db.delete_table(u'debate_ballotsubmission')

        # Deleting model 'SpeakerScoreByAdj'
        db.delete_table(u'debate_speakerscorebyadj')

        # Deleting model 'TeamScore'
        db.delete_table(u'debate_teamscore')

        # Deleting model 'SpeakerScore'
        db.delete_table(u'debate_speakerscore')

        # Deleting model 'Motion'
        db.delete_table(u'debate_motion')

        # Deleting model 'ActionLog'
        db.delete_table(u'debate_actionlog')

        # Deleting model 'Config'
        db.delete_table(u'debate_config')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'debate.actionlog': {
            'Meta': {'object_name': 'ActionLog'},
            'adjudicator_feedback': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.AdjudicatorFeedback']", 'null': 'True', 'blank': 'True'}),
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Debate']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'motion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Motion']", 'null': 'True', 'blank': 'True'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Round']", 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
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
        u'debate.ballotsubmission': {
            'Meta': {'object_name': 'BallotSubmission'},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'copied_from': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.BallotSubmission']", 'null': 'True', 'blank': 'True'}),
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Debate']"}),
            'discarded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'motion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Motion']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'submitter_type': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
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
            'ballot_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bracket': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'Meta': {'unique_together': "[('debate_team', 'speaker', 'position', 'ballot_submission')]", 'object_name': 'SpeakerScore'},
            'ballot_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.BallotSubmission']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Speaker']"})
        },
        u'debate.speakerscorebyadj': {
            'Meta': {'unique_together': "[('debate_adjudicator', 'debate_team', 'position', 'ballot_submission')]", 'object_name': 'SpeakerScoreByAdj'},
            'ballot_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.BallotSubmission']"}),
            'debate_adjudicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateAdjudicator']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('debate.models.ScoreField', [], {})
        },
        u'debate.team': {
            'Meta': {'unique_together': "[('reference', 'institution')]", 'object_name': 'Team'},
            'cannot_break': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.Institution']"}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'use_institution_prefix': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'debate.teamscore': {
            'Meta': {'unique_together': "[('debate_team', 'ballot_submission')]", 'object_name': 'TeamScore'},
            'ballot_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.BallotSubmission']"}),
            'debate_team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['debate.DebateTeam']"}),
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