from participants.models import Institution, Speaker, Team
from registration.views import BaseCreateTeamFormView
from utils.tests import BaseMinimalTournamentTestCase


class TestInitialsReference(BaseMinimalTournamentTestCase):

    def setUp(self):
        super().setUp()
        self.institution = Institution.objects.first()
        self.team = Team.objects.create(
            tournament=self.tournament,
            institution=self.institution,
            reference='',
        )

    def test_null_last_name_does_not_raise(self):
        speakers = [
            Speaker(name='Alice', last_name='Smith'),
            Speaker(name='Bob', last_name=None),
        ]
        reference = BaseCreateTeamFormView._initials_reference(self.team, speakers, exclude_team=self.team)
        self.assertEqual(reference, 'S')

    def test_empty_last_name_does_not_raise(self):
        speakers = [Speaker(name='Alice', last_name='')]
        reference = BaseCreateTeamFormView._initials_reference(self.team, speakers, exclude_team=self.team)
        self.assertEqual(reference, '')

    def test_partial_team_uses_only_registered_speakers(self):
        speakers = [Speaker(name='Alice', last_name='Smith')]
        reference = BaseCreateTeamFormView._initials_reference(self.team, speakers, exclude_team=self.team)
        self.assertEqual(reference, 'S')
