from django.db.models import Q
from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Institution, RegistrationStatus, Team
from tournaments.models import Round, Tournament
from venues.models import VenueCategory, VenueConstraint


class VenueConstraintManagerTest(TestCase):

    def setUp(self):
        tournament = Tournament.objects.create(slug='venue-constraints')
        first_round = Round.objects.create(tournament=tournament, seq=1)
        second_round = Round.objects.create(tournament=tournament, seq=2)
        self.first_debate = Debate.objects.create(round=first_round)
        self.second_debate = Debate.objects.create(round=first_round)
        self.other_debate = Debate.objects.create(round=second_round)

        institution = Institution.objects.create(pk=100, name='Selected', code='SEL')
        other_institution = Institution.objects.create(pk=200, name='Other', code='OTH')
        team = Team.objects.create(pk=200, tournament=tournament, institution=institution, reference='One')
        teammate = Team.objects.create(pk=201, tournament=tournament, institution=institution, reference='Two')
        other_team = Team.objects.create(pk=300, tournament=tournament, institution=other_institution)
        unconfirmed_team = Team.objects.create(
            pk=400, tournament=tournament, registration_status=RegistrationStatus.UNCONFIRMED,
        )
        adjudicator = Adjudicator.objects.create(pk=300, tournament=tournament, name='Selected')
        other_adjudicator = Adjudicator.objects.create(pk=100, tournament=tournament, name='Other')
        for debate, teams in (
            (self.first_debate, [team, teammate]),
            (self.second_debate, [team, unconfirmed_team]),
            (self.other_debate, [team, other_team]),
        ):
            for side, debate_team in enumerate(teams):
                DebateTeam.objects.create(debate=debate, team=debate_team, side=side)
            DebateAdjudicator.objects.create(
                debate=debate,
                adjudicator=other_adjudicator if debate == self.other_debate else adjudicator,
                type=DebateAdjudicator.TYPE_CHAIR,
            )

        category = VenueCategory.objects.create(tournament=tournament, name='Accessible')
        other_category = VenueCategory.objects.create(tournament=tournament, name='Nearby')
        self.team_constraint = VenueConstraint.objects.create(subject=team, category=category, priority=1)
        self.other_category_constraint = VenueConstraint.objects.create(subject=team, category=other_category, priority=2)
        self.institution_constraint = VenueConstraint.objects.create(subject=institution, category=category, priority=1)
        self.adjudicator_constraint = VenueConstraint.objects.create(subject=adjudicator, category=category, priority=1)
        self.unconfirmed_constraint = VenueConstraint.objects.create(subject=unconfirmed_team, category=category, priority=1)
        self.other_constraints = [
            VenueConstraint.objects.create(subject=subject, category=category, priority=1)
            for subject in (other_institution, other_team, other_adjudicator)
        ]
        self.first_debate_constraints = [
            self.team_constraint, self.other_category_constraint,
            self.institution_constraint, self.adjudicator_constraint,
        ]

    def assert_constraints_match(self, debates, expected):
        original = VenueConstraint.objects.filter(
            Q(team__debateteam__debate__in=debates) |
            Q(institution__team__debateteam__debate__in=debates) |
            Q(adjudicator__debateadjudicator__debate__in=debates),
        ).distinct()
        actual = list(VenueConstraint.objects.filter_for_debates(debates).select_related('category'))
        self.assertCountEqual(actual, expected)
        self.assertCountEqual(actual, original)

    def test_queryset_matches_all_subject_types_without_id_collisions(self):
        debates = Debate.objects.filter(pk=self.first_debate.pk)
        self.assert_constraints_match(debates, self.first_debate_constraints)

    def test_round_deduplicates_shared_subjects_and_includes_unconfirmed_teams(self):
        debates = Debate.objects.filter(round=self.first_debate.round)
        self.assert_constraints_match(debates, self.first_debate_constraints + [self.unconfirmed_constraint])

    def test_debate_list_spanning_rounds(self):
        self.assert_constraints_match(
            [self.first_debate, self.second_debate, self.other_debate],
            self.first_debate_constraints + [self.unconfirmed_constraint] + self.other_constraints,
        )

    def test_empty_inputs(self):
        for debates in ([], Debate.objects.none()):
            with self.subTest(debates=type(debates).__name__):
                self.assert_constraints_match(debates, [])
