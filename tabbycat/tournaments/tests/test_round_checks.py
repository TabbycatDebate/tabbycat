from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from availability.utils import set_availability
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Team
from tournaments.models import Round, Tournament
from venues.models import Venue


class TestRoundChecks(TestCase):
    """Tests the checks in the Round model for potential allocation errors."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="roundcheckstest", name="Round checks test")
        self.round = Round.objects.create(tournament=self.tournament, seq=1)
        self.debates = []
        self.venues = []
        self.teams = []
        self.adjs = []
        for i in [1, 2]:
            venue = Venue.objects.create(name=f"Venue {i}", priority=0)
            debate = Debate.objects.create(round=self.round, room_rank=i, venue=venue)
            team1 = Team.objects.create(tournament=self.tournament, reference=f"Team {i}A", use_institution_prefix=False)
            team2 = Team.objects.create(tournament=self.tournament, reference=f"Team {i}B", use_institution_prefix=False)
            adj = Adjudicator.objects.create(tournament=self.tournament, name=f"Adjudicator {i}")
            DebateTeam.objects.create(debate=debate, team=team1, side=DebateTeam.SIDE_AFF)
            DebateTeam.objects.create(debate=debate, team=team2, side=DebateTeam.SIDE_NEG)
            DebateAdjudicator.objects.create(debate=debate, adjudicator=adj, type=DebateAdjudicator.TYPE_CHAIR)
            self.debates.append(debate)
            self.venues.append(venue)
            self.teams.append([team1, team2])
            self.adjs.append(adj)

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def test_duplicate_panellists(self):
        self.assertEqual(self.round.duplicate_panellists.count(), 0)
        DebateAdjudicator.objects.create(debate=self.debates[1], adjudicator=self.adjs[0],
            type=DebateAdjudicator.TYPE_PANEL)
        self.assertEqual(self.round.duplicate_panellists.count(), 1)
        self.assertEqual(self.round.duplicate_panellists.first(), self.adjs[0])

    def test_duplicate_venues(self):
        self.assertEqual(self.round.duplicate_venues.count(), 0)
        self.debates[0].venue = self.venues[1]
        self.debates[0].save()
        self.assertEqual(self.round.duplicate_venues.count(), 1)
        self.assertEqual(self.round.duplicate_venues.first(), self.venues[1])

    def test_duplicate_team_names(self):
        self.assertEqual(self.round.duplicate_team_names.count(), 0)
        self.debates[0].aff_dt.team = self.teams[1][0]
        self.debates[0].aff_dt.save()
        self.assertEqual(self.round.duplicate_team_names.count(), 1)
        self.assertEqual(self.round.duplicate_team_names.first(), self.teams[1][0].short_name)

    # Properties need to be deleted in between checks, because they're all
    # decorated by @cached_property.

    def test_num_debates_without_chair(self):
        self.assertEqual(self.round.num_debates_without_chair, 0)
        del self.round.num_debates_without_chair
        DebateAdjudicator.objects.filter(debate=self.debates[0]).update(type=DebateAdjudicator.TYPE_PANEL)
        self.assertEqual(self.round.num_debates_without_chair, 1)
        del self.round.num_debates_without_chair
        DebateAdjudicator.objects.filter(debate=self.debates[0]).delete()
        self.assertEqual(self.round.num_debates_without_chair, 1)

    def test_num_debates_with_even_panel(self):
        self.assertEqual(self.round.num_debates_with_even_panel, 0)
        del self.round.num_debates_with_even_panel
        DebateAdjudicator.objects.create(debate=self.debates[0], adjudicator=self.adjs[1],
            type=DebateAdjudicator.TYPE_PANEL)
        self.assertEqual(self.round.num_debates_with_even_panel, 1)
        trainee = Adjudicator.objects.create(tournament=self.tournament, name="Trainee")
        del self.round.num_debates_with_even_panel
        DebateAdjudicator.objects.create(debate=self.debates[0], adjudicator=trainee,
            type=DebateAdjudicator.TYPE_TRAINEE)
        self.assertEqual(self.round.num_debates_with_even_panel, 1)

    def test_num_debates_without_venue(self):
        self.assertEqual(self.round.num_debates_without_venue, 0)
        del self.round.num_debates_without_venue
        self.debates[0].venue = None
        self.debates[0].save()
        self.assertEqual(self.round.num_debates_without_venue, 1)

    def test_num_debates_with_sides_unconfirmed(self):
        self.assertEqual(self.round.num_debates_with_sides_unconfirmed, 0)
        del self.round.num_debates_with_sides_unconfirmed
        self.debates[0].sides_confirmed = False
        self.debates[0].save()
        self.assertEqual(self.round.num_debates_with_sides_unconfirmed, 1)

    def test_unavailable_adjudicators_allocated(self):
        self.assertEqual(self.round.unavailable_adjudicators_allocated.count(), 2)
        set_availability(Adjudicator.objects.all(), self.round)
        self.assertEqual(self.round.unavailable_adjudicators_allocated.count(), 0)

    def test_num_available_adjudicators_not_allocated(self):
        set_availability(Adjudicator.objects.all(), self.round)
        self.assertEqual(self.round.num_available_adjudicators_not_allocated, 0)
        del self.round.num_available_adjudicators_not_allocated
        DebateAdjudicator.objects.filter(debate=self.debates[0]).delete()
        self.assertEqual(self.round.num_available_adjudicators_not_allocated, 1)
