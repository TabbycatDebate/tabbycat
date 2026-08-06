from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Adjudicator, Institution, Speaker, Team
from results.models import BallotSubmission, SpeakerScore
from tournaments.models import Round, Tournament
from utils.tests import ConditionalTableViewTestsMixin
from venues.models import Venue


class PublicResultsForRoundViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle_preference = 'public_features__public_results'
    view_name = 'results-public-round'
    round_seq = 3

    def expected_row_counts(self):
        return [self.round.debate_set.count() * 2]


class MergeLatestBallotsMedianOverviewTest(TestCase):
    """Tests the view-only median-aggregation preview shown on the "Merge
    Ballots" pages, a KPDP compliance quality-of-life feature. It should only
    appear when median scoring is on and there's an actual panel (2+ voting
    adjudicators) to aggregate across, and should never affect saved data."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="mergetest", name="MergeTest")
        self.tournament.preferences['scoring__score_aggregation_function'] = 'median'
        self.tournament.preferences['scoring__margin_includes_dissenters'] = True
        self.tournament.preferences['data_entry__individual_ballots'] = True
        self.tournament.preferences['debate_rules__substantive_speakers'] = 1
        self.tournament.preferences['debate_rules__reply_scores_enabled'] = False

        self.teams = []
        for i in range(2):
            inst = Institution.objects.create(code="MInst{:d}".format(i), name="Merge Institution {:d}".format(i))
            team = Team.objects.create(tournament=self.tournament, institution=inst,
                    reference="Team {:d}".format(i), use_institution_prefix=False)
            self.teams.append(team)
            Speaker.objects.create(team=team, name="Speaker {:d}".format(i))

        venue = Venue.objects.create(name="Venue", priority=10, tournament=self.tournament)
        rd = Round.objects.create(tournament=self.tournament, seq=1, abbreviation="R1")
        self.debate = Debate.objects.create(round=rd, venue=venue)

        for team, side in zip(self.teams, [DebateSide.AFF, DebateSide.NEG]):
            DebateTeam.objects.create(debate=self.debate, team=team, side=side)

        inst = Institution.objects.create(code="MAdjs", name="Merge Adjudicators")
        self.adjs = [Adjudicator.objects.create(tournament=self.tournament, institution=inst,
                name="Adjudicator {:d}".format(i), base_score=5) for i in range(3)]

        self.debate.adjudicators.chair = self.adjs[0]
        self.debate.adjudicators.panellists = self.adjs[1:]
        self.debate.adjudicators.save()

        # Adjudicators 0 and 1 give AFF the win; adjudicator 2 dissents (votes NEG).
        # Median AFF (60, 76, 80) = 76; median NEG (70, 75, 90) = 75. Vote split 2-1.
        self.adj_scores = {
            self.adjs[0]: {DebateSide.AFF: 80, DebateSide.NEG: 70},
            self.adjs[1]: {DebateSide.AFF: 76, DebateSide.NEG: 75},
            self.adjs[2]: {DebateSide.AFF: 60, DebateSide.NEG: 90},
        }
        for adj, side_scores in self.adj_scores.items():
            bs = BallotSubmission.objects.create(debate=self.debate, single_adj=True,
                    submitter_type=BallotSubmission.Submitter.PUBLIC, participant_submitter=adj,
                    confirmed=False)
            for side in [DebateSide.AFF, DebateSide.NEG]:
                dt = self.debate.debateteam_set.get(side=side)
                speaker = dt.team.speaker_set.first()
                SpeakerScore.objects.create(ballot_submission=bs, debate_team=dt,
                        speaker=speaker, position=1, score=side_scores[side])

        user_model = get_user_model()
        self.user = user_model.objects.create(username='mergetest_admin', is_superuser=True)
        self.client.force_login(self.user)

    def get_merge_response(self):
        url = reverse('results-merge-latest', kwargs={
            'tournament_slug': self.tournament.slug, 'debate_id': self.debate.id})
        return self.client.get(url)

    def test_overview_shown_with_correct_medians_and_split(self):
        response = self.get_merge_response()
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Final Ballot Overview', content)
        self.assertIn('76', content)
        self.assertIn('75', content)
        self.assertIn('2-1', content)

    def test_overview_hidden_when_mean_preference(self):
        self.tournament.preferences['scoring__score_aggregation_function'] = 'mean'
        response = self.get_merge_response()
        self.assertNotIn('Final Ballot Overview', response.content.decode())

    def test_overview_hidden_for_solo_adjudicator(self):
        self.debate.adjudicators.panellists = []
        self.debate.adjudicators.save()
        BallotSubmission.objects.exclude(participant_submitter=self.adjs[0]).delete()
        response = self.get_merge_response()
        self.assertNotIn('Final Ballot Overview', response.content.decode())

    def test_overview_absent_on_regular_ballot_entry_page(self):
        # Uses the same enter_results.html template as the merge page, but
        # via the non-merge entry view, which never sets 'median_overview'.
        url = reverse('old-results-ballotset-new', kwargs={
            'tournament_slug': self.tournament.slug, 'debate_id': self.debate.id})
        response = self.client.get(url)
        self.assertNotIn('Final Ballot Overview', response.content.decode())
