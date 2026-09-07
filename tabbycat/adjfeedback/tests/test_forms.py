from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from adjfeedback.forms import make_feedback_form_class_for_adj, make_feedback_form_class_for_team
from breakqual.models import BreakCategory
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Institution, Speaker, Team
from tournaments.models import Round, Tournament
from venues.models import Venue


class TestFeedbackFormRoundScope(TestCase):
    """Tests that the round-scope preferences control which rounds are offered
    in the feedback forms."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="scope", name="Scope")
        inst = Institution.objects.create(code="I", name="Institution")
        for i in range(4):
            team = Team.objects.create(tournament=self.tournament, institution=inst, reference=i)
            for j in range(3):
                Speaker.objects.create(team=team, name="%d-%d" % (i, j))
        for i in range(4):
            Adjudicator.objects.create(tournament=self.tournament, institution=inst, name=i)
        self.venue = Venue.objects.create(name="Venue", priority=1)

        self.break_category = BreakCategory.objects.create(tournament=self.tournament,
                name="Open", slug="open", seq=1, break_size=2, is_general=True, priority=1)

        # The preliminary round must be completed for the elimination round to
        # become current, which is what current_round_seq_limit is based on.
        self.prelim = Round.objects.create(tournament=self.tournament, seq=1, schedule_group=1,
                abbreviation="R1", name="Round 1", completed=True,
                draw_status=Round.Status.RELEASED)
        self.elim = Round.objects.create(tournament=self.tournament, seq=2, schedule_group=2,
                abbreviation="EF", name="Elimination", stage=Round.Stage.ELIMINATION,
                break_category=self.break_category, draw_status=Round.Status.RELEASED)

        self.prelim_debate = self._create_debate(self.prelim, (0, 1), (0, 1))
        self.elim_debate = self._create_debate(self.elim, (0, 2), (0, 2))

    def tearDown(self):
        DebateTeam.objects.all().delete()
        Institution.objects.all().delete()
        Venue.objects.all().delete()
        self.tournament.delete()

    def _adj(self, a):
        return Adjudicator.objects.get(tournament=self.tournament, name=a)

    def _team(self, t):
        return Team.objects.get(tournament=self.tournament, reference=t)

    def _create_debate(self, rd, teams, adjs):
        debate = Debate.objects.create(round=rd, venue=self.venue)
        for side, t in enumerate(teams):
            DebateTeam.objects.create(debate=debate, team=self._team(t), side=side)
        DebateAdjudicator.objects.create(debate=debate, adjudicator=self._adj(adjs[0]),
                type=DebateAdjudicator.TYPE_CHAIR)
        for a in adjs[1:]:
            DebateAdjudicator.objects.create(debate=debate, adjudicator=self._adj(a),
                    type=DebateAdjudicator.TYPE_PANEL)
        return debate

    def _round_names_in_choices(self, form_class):
        """The target field groups choices by round name; returns the group
        labels, which are the rounds the source may submit feedback for."""
        return [group for group, choices in form_class.base_fields['target'].choices if group is not None]

    def _fresh_tournament(self):
        """Tournament.pref() memoises on the instance, so a fresh instance is
        needed to pick up a preference changed since the last lookup."""
        return Tournament.objects.get(pk=self.tournament.pk)

    def _adj_form_rounds(self):
        form_class = make_feedback_form_class_for_adj(self._adj(0), self._fresh_tournament(), {})
        return self._round_names_in_choices(form_class)

    def _team_form_rounds(self):
        form_class = make_feedback_form_class_for_team(self._team(0), self._fresh_tournament(), {})
        return self._round_names_in_choices(form_class)

    # ==========================================================================
    # Adjudicator source
    # ==========================================================================

    def test_adj_form_prelims_only_excludes_elim_round(self):
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'prelims'
        self.assertEqual(self._adj_form_rounds(), ["Round 1"])

    def test_adj_form_all_rounds_includes_elim_round(self):
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.assertCountEqual(self._adj_form_rounds(), ["Round 1", "Elimination"])

    def test_adj_form_default_is_prelims_only(self):
        self.assertEqual(self._adj_form_rounds(), ["Round 1"])

    # ==========================================================================
    # Team source
    # ==========================================================================

    def test_team_form_prelims_only_excludes_elim_round(self):
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.assertEqual(self._team_form_rounds(), ["Round 1"])

    def test_team_form_all_rounds_includes_elim_round(self):
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.assertCountEqual(self._team_form_rounds(), ["Round 1", "Elimination"])

    def test_team_form_default_is_prelims_only(self):
        self.assertEqual(self._team_form_rounds(), ["Round 1"])

    def test_team_form_excludes_silent_elim_round(self):
        self.elim.silent = True
        self.elim.save()
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.assertEqual(self._team_form_rounds(), ["Round 1"])

    def test_adj_form_includes_silent_elim_round(self):
        self.elim.silent = True
        self.elim.save()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        # Silent rounds only suppress feedback from teams, not from adjudicators.
        self.assertCountEqual(self._adj_form_rounds(), ["Round 1", "Elimination"])

    # ==========================================================================
    # The two scopes are independent
    # ==========================================================================

    def test_scopes_are_independent_in_forms(self):
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.assertCountEqual(self._adj_form_rounds(), ["Round 1", "Elimination"])
        self.assertEqual(self._team_form_rounds(), ["Round 1"])

        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'prelims'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.assertEqual(self._adj_form_rounds(), ["Round 1"])
        self.assertCountEqual(self._team_form_rounds(), ["Round 1", "Elimination"])
