from types import SimpleNamespace
from unittest.mock import Mock

from django import forms
from django.test import SimpleTestCase, TestCase

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Adjudicator, Team
from results.forms import PerAdjudicatorBallotSetForm, SingleBallotSetForm
from results.models import BallotSubmission, ScoreCriterion
from tournaments.models import Round, Tournament


class PerAdjudicatorBallotSetFormTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="formtest", name="Form Test")
        round = Round.objects.create(
            tournament=self.tournament, seq=1, schedule_group=1, abbreviation="R1",
        )
        self.debate = Debate.objects.create(round=round)
        for side in (DebateSide.AFF, DebateSide.NEG):
            team = Team.objects.create(tournament=self.tournament, reference=f"Team {side}")
            DebateTeam.objects.create(debate=self.debate, team=team, side=side)

        self.adjudicator = Adjudicator.objects.create(
            tournament=self.tournament, name="Chair", base_score=5,
        )
        DebateAdjudicator.objects.create(
            debate=self.debate,
            adjudicator=self.adjudicator,
            type=DebateAdjudicator.TYPE_CHAIR,
        )
        self.ballotsub = BallotSubmission(debate=self.debate)

    def test_derived_criterion_total_does_not_validate_score_range(self):
        ScoreCriterion.objects.create(
            tournament=self.tournament,
            name="Content",
            seq=1,
            weight=1,
            min_score=0,
            max_score=100,
            step=1,
        )

        form = PerAdjudicatorBallotSetForm(
            self.ballotsub, tabroom=True, filled=True, vetos={},
        )
        field_name = form._fieldname_score(self.adjudicator, DebateSide.AFF, 1)
        field = form.fields[field_name]

        self.assertTrue(field.disabled)
        self.assertEqual(0, form.initial[field_name])
        self.assertEqual(0, field.clean(form.initial[field_name]))

    def test_entered_speaker_score_still_validates_score_range(self):
        form = PerAdjudicatorBallotSetForm(self.ballotsub, tabroom=True)
        field_name = form._fieldname_score(self.adjudicator, DebateSide.AFF, 1)

        with self.assertRaises(forms.ValidationError):
            form.fields[field_name].clean(0)


class Criteria(list):
    def exists(self):
        return bool(self)


class TestSingleBallotSetFormScoreCriteria(SimpleTestCase):
    def setUp(self):
        self.criterion = SimpleNamespace(
            id=1,
            min_score=24,
            max_score=32,
            step=0.5,
            weight=1,
            required=True,
            applies_to_position=lambda position, reply_position: True,
        )
        self.form = SingleBallotSetForm.__new__(SingleBallotSetForm)
        self.form.sides = [1]
        self.form.positions = [1]
        self.form.reply_position = None
        self.form.criteria = Criteria([self.criterion])
        self.form.fields = {}
        self.form.using_speaker_ranks = False
        self.form.using_declared_winner = False
        self.form.declared_winner = 'none'
        self.form.tournament = Mock()
        self.form.tournament.pref.side_effect = {
            'score_min': 60,
            'score_max': 80,
            'score_step': 0.5,
        }.__getitem__

    def test_total_score_range_is_not_validated_when_using_criteria(self):
        self.form.create_score_fields()
        score_name = self.form._fieldname_score(1, 1)
        score_field = self.form.fields[score_name]
        self.assertTrue(score_field.disabled)

        bound_form = forms.Form(data={score_name: '24'})
        bound_form.fields[score_name] = score_field
        self.assertTrue(bound_form.is_valid(), bound_form.errors)
