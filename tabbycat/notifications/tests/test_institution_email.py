from django.test import TestCase

from notifications.utils import InstitutionCustomEmailGenerator
from participants.models import Adjudicator, Coach, Institution, RegistrationStatus, Team, TournamentInstitution
from tournaments.models import Tournament


class InstitutionCustomEmailTests(TestCase):

    def test_registered_counts_include_unconfirmed_and_stay_within_tournament_and_institution(self):
        tournament = Tournament.objects.create(name='Email test', slug='email-test')
        other_tournament = Tournament.objects.create(name='Other test', slug='other-test')
        coaches = []
        for name in ('Registered', 'Empty'):
            institution = Institution.objects.create(name=name, code=name)
            t_inst = TournamentInstitution.objects.create(tournament=tournament, institution=institution)
            coaches.append(Coach.objects.create(
                name=name, tournament_institution=t_inst, url_key=name.lower(),
            ))

        institution = coaches[0].tournament_institution.institution
        for model in (Team, Adjudicator):
            for status in RegistrationStatus.values:
                identity = {'reference': status} if model is Team else {'name': status}
                model.objects.create(tournament=tournament, institution=institution, registration_status=status, **identity)
            model.objects.create(tournament=other_tournament, institution=institution, **identity)

        emails = InstitutionCustomEmailGenerator.generate(
            coaches, tournament, private_url='https://example.com/registration/',
        )
        registered, empty = [context for context, person in emails]
        self.assertEqual((registered.TEAMS_REGISTERED, registered.ADJUDICATORS_REGISTERED), (2, 2))
        self.assertEqual((empty.TEAMS_REGISTERED, empty.ADJUDICATORS_REGISTERED), (0, 0))
        self.assertIn('https://example.com/registration/registered/', registered.PRIVATE_URL)
