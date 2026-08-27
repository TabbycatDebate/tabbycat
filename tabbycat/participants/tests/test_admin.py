from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from adjallocation.models import AdjudicatorInstitutionConflict, TeamInstitutionConflict
from participants.admin import AdjudicatorAdmin, AdjudicatorForm, TeamAdmin, TeamForm
from participants.models import Adjudicator, Institution, Team
from utils.tests import BaseMinimalTournamentTestCase


class TestInstitutionConflictForms(BaseMinimalTournamentTestCase):
    def _admin_request(self):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        return request

    def test_team_form_defaults_to_creating_institution_conflict_after_institution_field(self):
        form = TeamForm()

        self.assertTrue(form.fields['create_institution_conflict'].initial)
        self.assertEqual(
            list(form.fields).index('institution') + 1,
            list(form.fields).index('create_institution_conflict'),
        )
        admin_fields = TeamAdmin(Team, admin.site).get_fields(self._admin_request())
        self.assertEqual(
            admin_fields.index('institution') + 1,
            admin_fields.index('create_institution_conflict'),
        )

    def test_adjudicator_form_defaults_to_creating_institution_conflict_after_institution_field(self):
        form = AdjudicatorForm()

        self.assertTrue(form.fields['create_institution_conflict'].initial)
        self.assertEqual(
            list(form.fields).index('institution') + 1,
            list(form.fields).index('create_institution_conflict'),
        )
        admin_fields = AdjudicatorAdmin(Adjudicator, admin.site).get_fields(self._admin_request())
        self.assertEqual(
            admin_fields.index('institution') + 1,
            admin_fields.index('create_institution_conflict'),
        )

    def test_team_form_creates_institution_conflict_only_when_institution_changes(self):
        team = Team.objects.first()
        institutions = list(Institution.objects.exclude(pk=team.institution_id)[:2])
        data = {
            'reference': team.reference,
            'short_reference': team.short_reference,
            'code_name': team.code_name,
            'institution': team.institution_id,
            'create_institution_conflict': 'on',
            'tournament': team.tournament_id,
            'use_institution_prefix': team.use_institution_prefix,
            'institution_conflicts': [],
            'seed': team.seed or '',
            'type': team.type,
            'emoji': team.emoji or '',
            'registration_status': team.registration_status,
        }
        form = TeamForm(data=data, instance=team)
        form.fields['institution_conflicts'].required = False

        self.assertTrue(form.is_valid(), form.errors)
        form.save(commit=False).save()
        TeamAdmin(Team, admin.site).save_related(None, form, [], False)
        self.assertFalse(TeamInstitutionConflict.objects.exists())

        data['institution'] = institutions[0].pk
        form = TeamForm(data=data, instance=team)
        form.fields['institution_conflicts'].required = False

        self.assertTrue(form.is_valid(), form.errors)
        form.save(commit=False).save()
        TeamAdmin(Team, admin.site).save_related(None, form, [], False)
        self.assertTrue(TeamInstitutionConflict.objects.filter(
            team=team, institution=institutions[0],
        ).exists())

        TeamInstitutionConflict.objects.all().delete()
        data['institution'] = institutions[1].pk
        data.pop('create_institution_conflict')
        form = TeamForm(data=data, instance=team)
        form.fields['institution_conflicts'].required = False

        self.assertTrue(form.is_valid(), form.errors)
        form.save(commit=False).save()
        TeamAdmin(Team, admin.site).save_related(None, form, [], False)
        self.assertFalse(TeamInstitutionConflict.objects.exists())

    def test_adjudicator_form_creates_institution_conflict_when_institution_changes(self):
        adjudicator = Adjudicator.objects.first()
        form = AdjudicatorForm(data={
            'name': adjudicator.name,
            'last_name': adjudicator.last_name,
            'email': adjudicator.email,
            'phone': adjudicator.phone,
            'anonymous': adjudicator.anonymous,
            'code_name': adjudicator.code_name,
            'url_key': adjudicator.url_key,
            'gender': adjudicator.gender,
            'pronoun': adjudicator.pronoun,
            'institution': Institution.objects.exclude(pk=adjudicator.institution_id).first().pk,
            'create_institution_conflict': 'on',
            'tournament': adjudicator.tournament_id,
            'base_score': adjudicator.base_score,
            'institution_conflicts': [],
            'team_conflicts': [],
            'adjudicator_conflicts': [],
            'trainee': adjudicator.trainee,
            'breaking': adjudicator.breaking,
            'independent': adjudicator.independent,
            'adj_core': adjudicator.adj_core,
            'registration_status': adjudicator.registration_status,
        }, instance=adjudicator)
        for field_name in ('institution_conflicts', 'team_conflicts', 'adjudicator_conflicts'):
            form.fields[field_name].required = False

        self.assertTrue(form.is_valid(), form.errors)
        form.save(commit=False).save()
        AdjudicatorAdmin(Adjudicator, admin.site).save_related(None, form, [], False)
        self.assertTrue(AdjudicatorInstitutionConflict.objects.filter(
            adjudicator=adjudicator, institution=adjudicator.institution,
        ).exists())
