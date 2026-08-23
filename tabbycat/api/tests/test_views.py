import json
from unittest.mock import patch

from django.conf import settings
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase

from availability.models import RoundAvailability
from participants.models import Team
from results.models import SpeakerScore
from tournaments.models import Round
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

    def test_access_with_user_auth(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-ballot-list', kwargs={'tournament_slug': self.tournament.slug, 'round_seq': 1, 'debate_pk': 12}))
        self.assertEqual(response.status_code, 200)

    def test_access_with_private_url(self):
        response = self.client.get(reverse('api-ballot-list', kwargs={'tournament_slug': self.tournament.slug, 'round_seq': 1, 'debate_pk': 12}), headers={"Authorization": "Key urlkey"})
        self.assertEqual(response.status_code, 200)


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
