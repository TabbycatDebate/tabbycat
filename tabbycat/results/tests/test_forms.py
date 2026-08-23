from django import forms
from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Adjudicator, Team
from results.forms import PerAdjudicatorBallotSetForm
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
