import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from actionlog.models import ActionLogEntry
from participants.models import Adjudicator, Team
from tournaments.models import Round, Tournament
from users.models import UserPermission
from users.permissions import Permission
from utils.misc import reverse_round, reverse_tournament
from utils.tests import BaseMinimalTournamentTestCase
from venues.models import Venue

from ..models import RoundAvailability
from ..utils import set_availability


class AvailabilityMatrixTests(BaseMinimalTournamentTestCase):
    types = (
        (Team, 'teams', Permission.VIEW_ROUNDAVAILABILITIES_TEAM),
        (Adjudicator, 'adjudicators', Permission.VIEW_ROUNDAVAILABILITIES_ADJ),
        (Venue, 'venues', Permission.VIEW_ROUNDAVAILABILITIES_VENUE),
    )

    def setUp(self):
        super().setUp()
        cache.clear()
        self.round = Round.objects.create(tournament=self.tournament, seq=1, abbreviation='R1')
        self.next_round = Round.objects.create(tournament=self.tournament, seq=2, abbreviation='R2')
        self.tournament.current_round = self.round
        self.tournament.save()
        self.user = get_user_model().objects.create(username='admin', is_superuser=True)
        self.client.force_login(self.user)

    def post_changes(self, participant_type, changes):
        return self.client.post(
            reverse_round('availability-update-' + participant_type, self.round),
            json.dumps({'changes': changes}), content_type='application/json',
        )

    def test_setup_and_matrices_show_rounds_and_current_availability(self):
        response = self.client.get(reverse_tournament('availability-setup-index', self.tournament))
        self.assertEqual(response.status_code, 200)
        for model, participant_type, _ in self.types:
            with self.subTest(participant_type=participant_type):
                participants = model.objects.filter(tournament=self.tournament)
                participant = participants.first()
                set_availability(participants.filter(pk=participant.pk), self.round)
                response = self.client.get(reverse_tournament(
                    'availability-matrix-' + participant_type, self.tournament,
                ))
                self.assertEqual(response.status_code, 200)
                table = json.loads(response.context['tables_data'])[0]
                self.assertEqual(len(table['data']), participants.count())
                self.assertEqual([header['title'] for header in table['head'][-2:]], ['R1', 'R2'])
                cells = [cell for row in table['data'] for cell in row if cell.get('component') == 'check-cell']
                self.assertEqual(len(cells), participants.count() * 2)
                self.assertEqual([(cell['id'], cell['round']) for cell in cells if cell['checked']],
                                 [(participant.pk, self.round.pk)])
                self.assertTrue(all(not cell['disabled'] for cell in cells))

    def test_changes_preserve_other_participants_rounds_and_types(self):
        for model, participant_type, _ in self.types:
            with self.subTest(participant_type=participant_type):
                participants = model.objects.filter(tournament=self.tournament)
                first, second, third = list(participants[:3])
                set_availability(participants.filter(pk__in=[first.pk, third.pk]), self.round)
                set_availability(participants, self.next_round)
                before = set(RoundAvailability.objects.values_list('content_type_id', 'object_id', 'round_id'))
                changes = {str(first.pk): False, str(second.pk): True}
                self.assertEqual(self.post_changes(participant_type, changes).status_code, 200)
                self.assertEqual(self.post_changes(participant_type, changes).status_code, 200)
                content_type = ContentType.objects.get_for_model(model)
                expected = before - {(content_type.pk, first.pk, self.round.pk)}
                expected.add((content_type.pk, second.pk, self.round.pk))
                self.assertEqual(set(RoundAvailability.objects.values_list('content_type_id', 'object_id', 'round_id')), expected)
                self.assertTrue(ActionLogEntry.objects.filter(round=self.round, user=self.user).exists())

    def test_invalid_changes_do_not_write_any_availability(self):
        other = Tournament.objects.create(slug='other')
        foreign = Venue.objects.create(tournament=other, name='Foreign room', priority=0)
        venue = self.tournament.venue_set.first()
        for changes in ([venue.pk], {str(venue.pk): 'false'}, {str(venue.pk): True, str(foreign.pk): True}, {'invalid': True}):
            with self.subTest(changes=changes):
                self.assertEqual(self.post_changes('venues', changes).status_code, 400)
                self.assertFalse(RoundAvailability.objects.exists())

    def test_existing_round_snapshot_updates_still_work(self):
        venues = list(self.tournament.venue_set.all()[:2])
        set_availability(self.tournament.venue_set.all(), self.round)
        response = self.client.post(
            reverse_round('availability-update-venues', self.round),
            json.dumps({str(v.pk): {'checked': i == 0} for i, v in enumerate(venues)}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(self.round.active_venues), [venues[0]])

    def test_read_only_users_cannot_change_availability(self):
        reader = get_user_model().objects.create(username='reader')
        for model, participant_type, permission in self.types:
            with self.subTest(participant_type=participant_type):
                UserPermission.objects.create(user=reader, tournament=self.tournament, permission=permission)
                self.client.force_login(reader)
                response = self.client.get(reverse_tournament(
                    'availability-matrix-' + participant_type, self.tournament,
                ))
                self.assertEqual(response.status_code, 200)
                table = json.loads(response.context['tables_data'])[0]
                self.assertTrue(all(cell['disabled'] for row in table['data'] for cell in row if cell.get('component') == 'check-cell'))
                participant = model.objects.filter(tournament=self.tournament).first()
                self.assertEqual(self.post_changes(participant_type, {str(participant.pk): True}).status_code, 403)
        self.assertFalse(RoundAvailability.objects.exists())
