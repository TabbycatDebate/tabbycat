import json
from unittest.mock import AsyncMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.fields import DateTimeField
from rest_framework.test import APITestCase

from actionlog.models import ActionLogEntry
from adjallocation.models import PreformedPanel
from adjfeedback.models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from availability.models import RoundAvailability
from breakqual.models import BreakingTeam
from checkins.models import Event
from options.models import TournamentPreferenceModel
from participants.models import Institution, Speaker, Team, TournamentInstitution
from results.models import BallotSubmission, SpeakerScore
from tournaments.models import Round, Tournament
from users.models import UserPermission
from users.permissions import Permission
from utils.tests import CompletedTournamentTestMixin, V1_ROOT_URL


class RootTests(APITestCase):

    def test_get_root(self):
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "_links": {"v1": V1_ROOT_URL},
            "timezone": settings.TIME_ZONE,
            "version": settings.TABBYCAT_VERSION,
            "version_name": settings.TABBYCAT_CODENAME,
        })

    def test_get_schema(self):
        response = self.client.get(reverse('api-schema'))
        self.assertEqual(response.status_code, 200)

    def test_get_v1_root(self):
        response = self.client.get(reverse('api-v1-root'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "_links": {
                "tournaments": V1_ROOT_URL + "/tournaments",
                "institutions": V1_ROOT_URL + "/institutions",
                "users": V1_ROOT_URL + "/users",
            },
        })


class APIExceptionHandlerTests(CompletedTournamentTestMixin, APITestCase):

    @patch('api.views.TournamentViewSet.list', side_effect=RuntimeError('deliberate failure'))
    def test_unhandled_exception_returns_json(self, _mock):
        response = self.client.get(reverse('api-tournament-list'))
        self.assertEqual(response.status_code, 500)
        self.assertIn('application/json', response['Content-Type'])
        payload = json.loads(response.content)
        self.assertIn('detail', payload)


class TournamentViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def test_get_tournament_list(self):
        response = self.client.get(reverse('api-tournament-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_tournament_detail(self):
        response = self.client.get(self.reverse_url('api-tournament-detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.tournament.id)


class ParticipantNameValidationTests(CompletedTournamentTestMixin, APITestCase):

    def test_create_participant_with_overlong_name(self):
        self.client.login(username="admin", password="admin")
        team = self.tournament.team_set.first()
        payloads = {
            'adjudicator': {
                'institution': None,
                'institution_conflicts': [],
                'team_conflicts': [],
                'adjudicator_conflicts': [],
            },
            'speaker': {
                'team': 'http://testserver' + self.reverse_url('api-team-detail', pk=team.pk),
                'categories': [],
            },
        }
        for participant, payload in payloads.items():
            with self.subTest(participant=participant):
                response = self.client.post(self.reverse_url(f'api-{participant}-list'), {
                    **payload,
                    'name': 'a' * 71,
                }, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(set(response.data), {'name'})
                self.assertEqual(response.data['name'][0].code, 'max_length')


class MotionViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def test_no_public_access_preferences(self):
        self.tournament.preferences['public_features__public_motions'] = False
        self.tournament.preferences['tab_release__motion_tab_released'] = False
        response = self.client.get(reverse('api-motion-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(response.status_code, 401)

    def test_exclude_unreleased_public(self):
        self.tournament.round_set.filter(seq=1).update(motions_status=Round.MotionsStatus.MOTIONS_RELEASED)

        self.tournament.preferences['public_features__public_motions'] = True
        self.tournament.preferences['tab_release__motion_tab_released'] = False
        response = self.client.get(reverse('api-motion-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        for motion in response.data:
            self.assertEqual(len(motion['rounds']), 1)
        self.tournament.round_set.filter(seq=1).update(motions_status=Round.MotionsStatus.NOT_RELEASED) # Reset

    def test_include_unreleased_tab_public(self):
        self.tournament.preferences['public_features__public_motions'] = False
        self.tournament.preferences['tab_release__motion_tab_released'] = True
        response = self.client.get(reverse('api-motion-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 18)  # 6 rounds * 3 motions/round

    def test_unauthorized_motion_detail(self):
        self.tournament.preferences['public_features__public_motions'] = True
        self.tournament.preferences['tab_release__motion_tab_released'] = False
        # Motion with id exists
        response = self.client.get(reverse('api-motion-detail', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(response.status_code, 404)


class RoundViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        self.round_seq = 1
        super().setUp()

    def test_get_round_list(self):
        self.round_seq = None  # Unset since it isn't used for list
        response = self.client.get(self.reverse_url('api-round-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

    def test_get_paginated_round_list(self):
        self.round_seq = None  # Unset since it isn't used for list
        response = self.client.get(self.reverse_url('api-round-list'), {'limit': 100, 'offset': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

    def test_get_round_detail(self):
        response = self.client.get(self.reverse_url('api-round-detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.round.id)

    def test_patch_round_detail(self):
        # Ensure the test will be valid first
        self.assertEqual(self.round.motions_status, Round.MotionsStatus.NOT_RELEASED)

        self.client.login(username="admin", password="admin")

        response = self.client.patch(
            self.reverse_url('api-round-detail'),
            json.dumps({"motions_released": True}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['motions_released'], True)
        self.round.refresh_from_db()
        self.assertEqual(self.round.motions_status, Round.MotionsStatus.MOTIONS_RELEASED)

    def test_post_round_detail(self):
        # Ensure the test will be valid first
        self.assertEqual(self.round.silent, False)

        self.client.login(username="admin", password="admin")

        response = self.client.post(
            self.reverse_url('api-round-detail'),
            json.dumps({
                "break_category": None,
                "starts_at": None,
                "seq": 1,
                "completed": True,
                "name": "Round 1",
                "abbreviation": "R1",
                "stage": "P",
                "draw_type": "R",
                "draw_status": "R",
                "silent": True,
                "motions_released": False,
                "weight": 1,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['silent'], True)
        self.round.refresh_from_db()
        self.assertEqual(self.round.silent, True)


class PairingViewsetTests(CompletedTournamentTestMixin, APITestCase):
    round_seq = 1

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_draw'] = 'all-released'
        debate = self.round.debate_set.first()
        debate.flags = ['max_swapped']
        debate.save()
        debate.debateteam_set.update(flags=['pullup'])

    def test_exclude_flags_public(self):
        response = self.client.get(self.reverse_url('api-pairing-list'))
        self.assertEqual(response.status_code, 200)
        for debate in response.data:
            self.assertNotIn('flags', debate)
            for team in debate['teams']:
                self.assertNotIn('flags', team)

    def test_include_flags_authenticated(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.reverse_url('api-pairing-list'))
        self.assertEqual(response.status_code, 200)
        flagged = [debate for debate in response.data if debate['flags']]
        self.assertEqual(len(flagged), 1)
        self.assertEqual([team['flags'] for team in flagged[0]['teams']], [['pullup'], ['pullup']])


class InstitutionViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_institutions_list'] = True
        institution = self.tournament.team_set.exclude(institution=None).first().institution
        tournament_institution = self.tournament.tournamentinstitution_set.create(institution=institution)
        tournament_institution.coach_set.create(name="Coach", email="coach@example.com",
            phone="0123456789", url_key="coachkey", gender='F', pronoun="she")

    def get_coaches(self):
        response = self.client.get(self.reverse_url('api-institution-list'))
        self.assertEqual(response.status_code, 200)
        return [coach for institution in response.data for coach in institution.get('coaches') or []]

    def test_exclude_coach_private_fields_public(self):
        coaches = self.get_coaches()
        self.assertEqual(len(coaches), 1)
        for field in ('email', 'phone', 'url_key', 'gender', 'pronoun', 'answers'):
            self.assertNotIn(field, coaches[0])
        self.assertEqual(coaches[0]['name'], "Coach")

    def test_include_coach_private_fields_authenticated(self):
        self.client.login(username="admin", password="admin")
        coaches = self.get_coaches()
        self.assertEqual(len(coaches), 1)
        self.assertEqual(coaches[0]['email'], "coach@example.com")
        self.assertEqual(coaches[0]['url_key'], "coachkey")


class TeamViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_participants'] = True
        Speaker.objects.filter(team__tournament=self.tournament).update(email="speaker@example.com")

    def test_exclude_speaker_private_fields_public(self):
        response = self.client.get(self.reverse_url('api-team-list'))
        self.assertEqual(response.status_code, 200)
        for team in response.data:
            self.assertGreater(len(team['speakers']), 0)
            for speaker in team['speakers']:
                for field in ('email', 'phone', 'url_key', 'gender', 'pronoun', 'barcode', 'answers'):
                    self.assertNotIn(field, speaker)
                self.assertIn('name', speaker)

    def test_include_speaker_private_fields_authenticated(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.reverse_url('api-team-list'))
        self.assertEqual(response.status_code, 200)
        for team in response.data:
            self.assertGreater(len(team['speakers']), 0)
            for speaker in team['speakers']:
                self.assertEqual(speaker['email'], "speaker@example.com")
                self.assertIn('url_key', speaker)

    def test_create_with_speakers(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post(self.reverse_url('api-team-list'), {
            'reference': "New team",
            'speakers': [{'name': "New speaker", 'email': "new@example.com"}],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual([speaker['name'] for speaker in response.data['speakers']], ["New speaker"])
        self.assertEqual(Speaker.objects.get(email="new@example.com").team_id, response.data['id'])

    def test_update_with_speakers(self):
        self.client.login(username="admin", password="admin")
        team = self.tournament.team_set.first()
        speakers = team.speaker_set.count()
        response = self.client.patch(self.reverse_url('api-team-detail', pk=team.pk), {
            'speakers': [{'name': "New speaker", 'email': "new@example.com"}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(team.speaker_set.count(), speakers + 1)


class SpeakerCategoryViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.tournament.speakercategory_set.create(name='sc1', slug='sc1', seq=1, public=False)
        self.tournament.speakercategory_set.create(name='sc2', slug='sc2', seq=2, public=True)

    def test_private_excluded_public(self):
        response = self.client.get(reverse('api-speakercategory-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(len(response.data), 1)

    def test_all_categories_authenticated(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-speakercategory-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(len(response.data), 2)


class SpeakerRoundStandingsViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username="admin", password="admin")

    def get_speeches(self, params=None):
        response = self.client.get(self.reverse_url('api-speaker-round-standings'), params or {})
        self.assertEqual(response.status_code, 200)
        return [
            speech
            for speaker in response.data
            for round_data in speaker['rounds']
            for speech in round_data['speeches']
        ]

    def test_paginates_before_loading_round_scores(self):
        url = self.reverse_url('api-speaker-round-standings')
        full_response = self.client.get(url)
        self.assertEqual(full_response.status_code, 200)
        self.assertGreater(len(full_response.data), 1)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url, {'limit': 1, 'offset': 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, full_response.data[1:2])
        self.assertIn('rel="next"', response['Link'])
        self.assertIn('rel="prev"', response['Link'])
        speaker_id = int(response.data[0]['speaker'].rsplit('/', 1)[1])
        score_queries = [q['sql'] for q in queries if 'FROM "results_speakerscore"' in q['sql']]
        self.assertEqual(len(score_queries), 1)
        self.assertIn('"results_speakerscore"."speaker_id" IN (%d)' % speaker_id, score_queries[0])

        response = self.client.get(url, {'limit': 1, 'offset': len(full_response.data)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_defaults_to_substantive_speeches(self):
        self.assertTrue(SpeakerScore.objects.filter(position=self.tournament.reply_position).exists())

        speeches = self.get_speeches()

        self.assertTrue(speeches)
        self.assertTrue(all(speech['position'] <= self.tournament.last_substantive_position for speech in speeches))

    def test_can_filter_for_reply_speeches(self):
        speeches = self.get_speeches({'replies': 'true'})

        self.assertTrue(speeches)
        self.assertTrue(all(speech['position'] == self.tournament.reply_position for speech in speeches))

    def test_can_filter_for_ghost_speeches(self):
        SpeakerScore.objects.filter(ballot_submission__confirmed=True).update(ghost=True)

        speeches = self.get_speeches({'ghost': 'true', 'substantive': 'false'})

        self.assertTrue(speeches)
        self.assertTrue(all(speech['ghost'] for speech in speeches))

    def test_includes_scores_from_speakers_previous_team(self):
        score = SpeakerScore.objects.filter(
            ballot_submission__confirmed=True, position__lte=self.tournament.last_substantive_position,
        ).select_related(
            'speaker__team', 'debate_team__debate__round',
        ).first()
        speaker = score.speaker
        new_team = Team.objects.filter(tournament=self.tournament).exclude(pk=speaker.team_id).first()
        speaker.team = new_team
        speaker.save(update_fields=['team'])

        response = self.client.get(self.reverse_url('api-speaker-round-standings'))

        self.assertEqual(response.status_code, 200)
        speaker_data = next(item for item in response.data if item['speaker'].endswith('/%d' % speaker.pk))
        previous_round = next(
            item for item in speaker_data['rounds']
            if item['round'].endswith('/%d' % score.debate_team.debate.round.seq)
        )
        self.assertIn(score.score, [speech['score'] for speech in previous_round['speeches']])


class BreakEligibilityViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def test_get_eligible_teams(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-breakcategory-eligibility', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(len(response.data), 2)


class SpeakerEligibilityViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.sc = self.tournament.speakercategory_set.create(name='sc1', slug='sc1', seq=1, public=False)
        self.sc.speaker_set.set(self.tournament.team_set.first().speaker_set.all())

    def test_get_eligible_speakers(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-speakercategory-eligibility', kwargs={'tournament_slug': self.tournament.slug, 'pk': self.sc.pk}))
        self.assertEqual(len(response.data), 2)

    def test_unauthorized_if_private(self):
        response = self.client.get(reverse('api-speakercategory-eligibility', kwargs={'tournament_slug': self.tournament.slug, 'pk': self.sc.pk}))
        self.assertEqual(response.status_code, 401)


class BreakingTeamsViewsetTests(CompletedTournamentTestMixin, APITestCase):
    client_class = Client

    def test_get_breaking_teams(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(len(response.data), 8)

    def test_generate_break(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(len(response.data), 13)

    def test_delete_break(self):
        self.client.login(username="admin", password="admin")
        response = self.client.delete(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(response.status_code, 204)

    def test_remove_breaking_team(self):
        self.client.login(username="admin", password="admin")
        response = self.client.patch(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}), {
            'team': 'http://testserver/api/v1/tournaments/demo/teams/7',
            'remark': 'w',
        }, content_type='application/json')
        self.assertEqual(len(response.data), 16)


class BallotViewSetTests(CompletedTournamentTestMixin, APITestCase):

    def get_ballot_url(self, ballot):
        return self.reverse_url('api-ballot-detail', round_seq=ballot.debate.round.seq, debate_pk=ballot.debate_id, pk=ballot.pk)

    def test_patch_discarded_preserves_confirmation(self):
        self.client.login(username="admin", password="admin")
        ballot = BallotSubmission.objects.filter(debate__round__tournament=self.tournament, confirmed=True).first()
        confirmation = (ballot.confirmer_id, ballot.confirm_timestamp)

        response = self.client.patch(self.get_ballot_url(ballot), {'discarded': True})

        self.assertEqual(response.status_code, 200)
        ballot.refresh_from_db()
        self.assertTrue(ballot.discarded)
        self.assertTrue(ballot.confirmed)
        self.assertEqual((ballot.confirmer_id, ballot.confirm_timestamp), confirmation)

    def test_delete_discards_and_logs_ballot(self):
        self.client.login(username="admin", password="admin")
        ballot = BallotSubmission.objects.filter(debate__round__tournament=self.tournament).first()

        response = self.client.delete(self.get_ballot_url(ballot))

        self.assertEqual(response.status_code, 200)
        ballot.refresh_from_db()
        self.assertTrue(ballot.discarded)
        log = ActionLogEntry.objects.get(type=ActionLogEntry.ActionType.BALLOT_DISCARD, agent=ActionLogEntry.Agent.API)
        self.assertEqual(log.content_object, ballot)

    def test_access_with_user_auth(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-ballot-list', kwargs={'tournament_slug': self.tournament.slug, 'round_seq': 1, 'debate_pk': 12}))
        self.assertEqual(response.status_code, 200)

    def test_access_with_private_url(self):
        response = self.client.get(reverse('api-ballot-list', kwargs={'tournament_slug': self.tournament.slug, 'round_seq': 1, 'debate_pk': 12}), headers={"Authorization": "Key urlkey"})
        self.assertEqual(response.status_code, 200)


class RoundActionTests(CompletedTournamentTestMixin, APITestCase):
    round_seq = 1

    def setUp(self):
        super().setUp()
        self.client.login(username="admin", password="admin")

    def assert_round_action_logged(self, action_type):
        log = ActionLogEntry.objects.get(type=action_type, agent=ActionLogEntry.Agent.API)
        self.assertEqual(log.content_object, self.round)
        self.assertEqual(log.round, self.round)
        self.assertEqual(log.tournament, self.tournament)

    def test_delete_all_pairings(self):
        self.assertTrue(self.round.debate_set.exists())
        response = self.client.delete(self.reverse_url('api-pairing-list'))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.round.debate_set.exists())
        self.assert_round_action_logged(ActionLogEntry.ActionType.DRAW_REGENERATE)

    def test_delete_all_preformed_panels(self):
        PreformedPanel.objects.create(round=self.round, room_rank=1)
        response = self.client.delete(self.reverse_url('api-preformedpanel-list'))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(PreformedPanel.objects.filter(round=self.round).exists())
        self.assert_round_action_logged(ActionLogEntry.ActionType.PREFORMED_PANELS_DELETE)

    def test_add_blank_preformed_panels(self):
        response = self.client.put(self.reverse_url('api-preformedpanel-list'))

        self.assertEqual(response.status_code, 200)
        expected_panels = self.tournament.team_set.count() // self.tournament.pref('teams_in_debate')
        self.assertGreater(expected_panels, 0)
        self.assertEqual(PreformedPanel.objects.filter(round=self.round).count(), expected_panels)
        self.assertEqual(len(response.data), expected_panels)
        self.assert_round_action_logged(ActionLogEntry.ActionType.PREFORMED_PANELS_CREATE)

    @patch('api.views.get_channel_layer')
    def test_debate_checkin_broadcasts_matchup(self, get_channel_layer):
        group_send = AsyncMock()
        get_channel_layer.return_value.group_send = group_send
        debate = self.round.debate_set.first()
        url = self.reverse_url('api-debate-checkin', debate_pk=debate.pk)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)

        response = self.client.put(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['checked'])
        self.assertIsNotNone(response.data['timestamp'])
        self.assertEqual(Event.objects.filter(identifier=debate.checkin_identifier).count(), 1)
        group_send.assert_awaited_once()
        message = group_send.call_args.args[1]
        self.assertTrue(message['created'])
        self.assertEqual(message['checkins'][0]['owner_name'], debate.matchup)


class AvailabilitiesViewSetTests(CompletedTournamentTestMixin, APITestCase):
    round_seq = 1

    def setUp(self):
        super().setUp()
        self.client.login(username="admin", password="admin")
        RoundAvailability.objects.filter(round=self.round).delete()
        self.objects = {
            'adjudicators': self.tournament.adjudicator_set.first(),
            'teams': self.tournament.team_set.first(),
            'venues': self.tournament.venue_set.first(),
        }
        for obj in self.objects.values():
            RoundAvailability.objects.create(round=self.round, content_object=obj)

    def get_availabilities(self, params=None):
        response = self.client.get(self.reverse_url('api-availability-list'), params or {})
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_no_types_returns_no_availabilities(self):
        self.assertEqual(self.get_availabilities(), [])

    def test_filters_availabilities_by_requested_type(self):
        for param, obj in self.objects.items():
            with self.subTest(param=param):
                availabilities = self.get_availabilities({param: 'true'})
                self.assertEqual(len(availabilities), 1)
                self.assertTrue(availabilities[0].endswith('/%d' % obj.pk))

    def test_can_request_multiple_availability_types(self):
        availabilities = self.get_availabilities({'teams': 'true', 'venues': 'true'})

        self.assertEqual(len(availabilities), 2)
        self.assertEqual(
            {int(url.rsplit('/', 1)[-1]) for url in availabilities},
            {self.objects['teams'].pk, self.objects['venues'].pk},
        )


class ActionLogEntryViewSetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.get(username="admin")
        self.client.login(username="admin", password="admin")

    def log(self, content_object=None, type=ActionLogEntry.ActionType.TOURNAMENT_EDIT, **kwargs):
        kwargs.setdefault('tournament', self.tournament)
        return ActionLogEntry.objects.log(type=type, user=self.user, content_object=content_object, **kwargs)

    def get_entries(self, params=None):
        response = self.client.get(self.reverse_url('api-actionlogentry-list'), params or {})
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_list_entries(self):
        round = self.tournament.round_set.get(seq=2)
        first = self.log(round, ActionLogEntry.ActionType.DRAW_CREATE, round=round, agent=ActionLogEntry.Agent.API)
        second = self.log(ip_address='127.0.0.1')

        entries = self.get_entries()

        self.assertEqual([entry['id'] for entry in entries], [first.id, second.id])
        tournament_url = V1_ROOT_URL + "/tournaments/" + self.tournament.slug
        self.assertEqual(entries[0], {
            'id': first.id,
            'url': tournament_url + "/action-log/%d" % first.id,
            'type': 'dr.crea',
            'timestamp': DateTimeField().to_representation(first.timestamp),
            'user': self.user.id,
            'ip_address': None,
            'agent': 'a',
            'round': tournament_url + "/rounds/2",
            'object': tournament_url + "/rounds/2",
        })
        self.assertIsNone(entries[1]['round'])
        self.assertIsNone(entries[1]['object'])
        self.assertEqual(entries[1]['ip_address'], '127.0.0.1')

    def test_get_entry_detail(self):
        entry = self.log(self.tournament)
        response = self.client.get(self.reverse_url('api-actionlogentry-detail', pk=entry.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], entry.id)
        self.assertEqual(response.data['object'], V1_ROOT_URL + "/tournaments/" + self.tournament.slug)

    def test_object_urls_link_to_endpoints(self):
        round = self.tournament.round_set.get(seq=1)
        debate = round.debate_set.first()
        ballot = debate.ballotsubmission_set.first()
        panel = PreformedPanel.objects.create(round=round, room_rank=1)
        self.tournament.preferences.all()  # Populate preferences
        preference = TournamentPreferenceModel.objects.get(instance=self.tournament, section='ui_options', name='team_code_names')
        adjudicator = self.tournament.adjudicator_set.first()
        feedback = AdjudicatorFeedback.objects.create(adjudicator=adjudicator, source_team=debate.debateteam_set.first(), score=3)
        question = AdjudicatorFeedbackQuestion.objects.filter(tournament=self.tournament).first()
        team = self.tournament.team_set.first()
        speaker = team.speaker_set.first()
        motion = self.tournament.motion_set.first()
        venue = self.tournament.venue_set.first()
        break_category = self.tournament.breakcategory_set.first()
        institution = Institution.objects.first()

        tournament_path = "/tournaments/" + self.tournament.slug
        debate_path = tournament_path + "/rounds/1/pairings/%d" % debate.pk
        objects = [
            (self.tournament, tournament_path),
            (round, tournament_path + "/rounds/1"),
            (debate, debate_path),
            (ballot, debate_path + "/ballots/%d" % ballot.pk),
            (panel, tournament_path + "/rounds/1/preformed-panels/%d" % panel.pk),
            (preference, tournament_path + "/preferences/ui_options__team_code_names"),
            (adjudicator, tournament_path + "/adjudicators/%d" % adjudicator.pk),
            (adjudicator.adjudicatorbasescorehistory_set.first(), tournament_path + "/adjudicators/%d" % adjudicator.pk),
            (feedback, tournament_path + "/feedback/%d" % feedback.pk),
            (question, tournament_path + "/feedback-questions/%d" % question.pk),
            (team, tournament_path + "/teams/%d" % team.pk),
            (speaker, tournament_path + "/speakers/%d" % speaker.pk),
            (motion, tournament_path + "/motions/%d" % motion.pk),
            (venue, tournament_path + "/venues/%d" % venue.pk),
            (break_category, tournament_path + "/break-categories/%d" % break_category.pk),
            (institution, "/institutions/%d" % institution.pk),
            (TournamentInstitution.objects.create(tournament=self.tournament, institution=institution),
                "/institutions/%d" % institution.pk),
        ]

        for obj, path in objects:
            with self.subTest(model=type(obj).__name__):
                entry = self.log(obj)
                response = self.client.get(self.reverse_url('api-actionlogentry-detail', pk=entry.pk))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['object'], V1_ROOT_URL + path)
                self.assertEqual(self.client.get(response.data['object']).status_code, 200)

    def test_object_null_if_deleted_or_without_endpoint(self):
        speaker = Speaker.objects.filter(team__tournament=self.tournament).first()
        deleted_entry = self.log(speaker, ActionLogEntry.ActionType.SPEAKER_DELETE)
        speaker.delete()
        breaking_team = BreakingTeam.objects.filter(break_category__tournament=self.tournament).first()
        self.log(breaking_team, ActionLogEntry.ActionType.BREAK_EDIT_REMARKS)

        entries = self.get_entries()

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['id'], deleted_entry.id)
        self.assertEqual([entry['object'] for entry in entries], [None, None])

    def test_excludes_entries_of_other_tournaments(self):
        other = Tournament.objects.create(slug='other', name='Other')
        own_entry = self.log(self.tournament)
        other_entry = self.log(other, tournament=other)
        self.log(tournament=None)

        self.assertEqual([entry['id'] for entry in self.get_entries()], [own_entry.id])
        response = self.client.get(self.reverse_url('api-actionlogentry-detail', pk=other_entry.pk))
        self.assertEqual(response.status_code, 404)

    def test_constant_queries_for_objects(self):
        def count_list_queries():
            with CaptureQueriesContext(connection) as queries:
                self.get_entries()
            return len(queries)

        round = self.tournament.round_set.get(seq=1)
        for debate in round.debate_set.all()[:2]:
            self.log(debate, ActionLogEntry.ActionType.DEBATE_EDIT, round=round)
            self.log(debate.ballotsubmission_set.first(), ActionLogEntry.ActionType.BALLOT_CONFIRM, round=round)
        self.get_entries()  # Populate the content type cache
        expected_queries = count_list_queries()

        for debate in round.debate_set.all()[2:]:
            self.log(debate, ActionLogEntry.ActionType.DEBATE_EDIT, round=round)
            self.log(debate.ballotsubmission_set.first(), ActionLogEntry.ActionType.BALLOT_CONFIRM, round=round)
        self.assertEqual(count_list_queries(), expected_queries)

    def test_read_only(self):
        entry = self.log()
        list_url = self.reverse_url('api-actionlogentry-list')
        detail_url = self.reverse_url('api-actionlogentry-detail', pk=entry.pk)

        self.assertEqual(self.client.post(list_url, {'type': 'to.edit'}).status_code, 405)
        self.assertEqual(self.client.patch(detail_url, {'type': 'to.edit'}).status_code, 405)
        self.assertEqual(self.client.delete(detail_url).status_code, 405)
        self.assertTrue(ActionLogEntry.objects.filter(pk=entry.pk).exists())

    def test_unauthenticated(self):
        entry = self.log()
        self.client.logout()
        self.assertEqual(self.client.get(self.reverse_url('api-actionlogentry-list')).status_code, 401)
        self.assertEqual(self.client.get(self.reverse_url('api-actionlogentry-detail', pk=entry.pk)).status_code, 401)

    def test_requires_view_permission(self):
        entry = self.log()
        user = get_user_model().objects.create_user('log-viewer', password='log-viewer')
        self.client.login(username='log-viewer', password='log-viewer')
        self.assertEqual(self.client.get(self.reverse_url('api-actionlogentry-list')).status_code, 403)

        UserPermission.objects.create(user=user, tournament=self.tournament, permission=Permission.VIEW_ACTIONLOGENTRIES)
        self.assertEqual([listed['id'] for listed in self.get_entries()], [entry.id])
        response = self.client.get(self.reverse_url('api-actionlogentry-detail', pk=entry.pk))
        self.assertEqual(response.status_code, 200)
