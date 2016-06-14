from adjallocation.models import DebateAdjudicator
from participants.models import Adjudicator, Team
from results.models import SpeakerScoreByAdj
from tournaments.models import Round

from .models import AdjudicatorFeedback


def get_feedback_overview(t, adjudicators):

    all_debate_adjudicators = list(DebateAdjudicator.objects.all().select_related(
        'adjudicator'))
    all_adj_feedbacks = list(AdjudicatorFeedback.objects.filter(confirmed=True).select_related(
        'adjudicator', 'source_adjudicator', 'source_team', 'source_adjudicator__debate__round', 'source_team__debate__round'))
    all_adj_scores = list(SpeakerScoreByAdj.objects.filter(ballot_submission__confirmed=True).select_related(
        'debate_adjudicator__adjudicator__id', 'ballot_submission'))
    rounds = t.prelim_rounds(until=t.current_round)

    for adj in adjudicators:
        # Gather feedback scores for graphs
        feedbacks = [f for f in all_adj_feedbacks if f.adjudicator == adj]
        debate_adjudications = [a for a in all_debate_adjudicators if a.adjudicator.id is adj.id]
        scores = [s for s in all_adj_scores if s.debate_adjudicator.adjudicator.id is adj.id]

        # Gather a dict of round-by-round feedback for the graph
        adj.feedback_data = feedback_stats(adj, rounds, feedbacks, all_debate_adjudicators)
        # Sum up remaining stats
        adj = scoring_stats(adj, scores, debate_adjudications)

    return adjudicators


def feedback_stats(adj, rounds, feedbacks, all_debate_adjudicators):

    # Start off with their test scores
    feedback_data = [{'x': 0, 'y': adj.test_score, 'position': "Test Score"}]

    for r in rounds:
        # Filter all the feedback to focus on this particular rouond
        adj_round_feedbacks = [f for f in feedbacks if (f.source_adjudicator and f.source_adjudicator.debate.round == r)]
        adj_round_feedbacks.extend([f for f in feedbacks if (f.source_team and f.source_team.debate.round == r)])

        if len(adj_round_feedbacks) > 0:
            debates = [fb.source_team.debate for fb in adj_round_feedbacks if fb.source_team]
            debates.extend([fb.source_adjudicator.debate for fb in adj_round_feedbacks if fb.source_adjudicator])
            adj_da = next((da for da in all_debate_adjudicators if (da.adjudicator == adj and da.debate == debates[0])), None)
            if adj_da:
                if adj_da.type == adj_da.TYPE_CHAIR:
                    adj_type = "Chair"
                elif adj_da.type == adj_da.TYPE_PANEL:
                    adj_type = "Panellist"
                elif adj_da.type == adj_da.TYPE_TRAINEE:
                    adj_type = "Trainee"

                total_score = [f.score for f in adj_round_feedbacks]
                average_score = round(sum(total_score) / len(total_score), 2)

                # Creating the object list for the graph
                feedback_data.append({
                    'x': r.seq,
                    'y': average_score,
                    'position': adj_type,
                })

    return feedback_data


def scoring_stats(adj, scores, debate_adjudications):
    # Processing scores to get average margins
    adj.debates = len(debate_adjudications)
    adj.avg_score = None
    adj.avg_margin = None

    if len(scores) > 0:
        adj.avg_score = sum(s.score for s in scores) / len(scores)

        ballot_ids = [score.ballot_submission for score in scores]
        ballot_ids = sorted(set([b.id for b in ballot_ids])) # Deduplication of ballot IDS
        ballot_margins = []

        for ballot_id in ballot_ids:
            # For each unique ballot id total its scores
            single_round = [s for s in scores if s.ballot_submission.id is ballot_id]
            adj_scores = [s.score for s in single_round] # TODO this is slow - should be prefetched
            team_split = int(len(adj_scores) / 2)
            try:
                # adj_scores is a list of all scores from the debate
                t_a_scores = adj_scores[:team_split]
                t_b_scores = adj_scores[team_split:]
                t_a_total, t_b_total = sum(t_a_scores), sum(t_b_scores)
                ballot_margins.append(
                    max(t_a_total, t_b_total) - min(t_a_total, t_b_total))
            except TypeError:
                print(team_split)

        # adj.average_score = adj.feedback_data['y']
        if ballot_margins:
            adj.avg_margin = sum(ballot_margins) / len(ballot_margins)

    return adj


def progress_cells(team_or_adj):
    ddict = []
    ddict.append({
        'head': {
            'key': 'Coverage',
            'icon': 'glyphicon-eye-open',
            'tooltip': 'Percentage Returned',
        },
        'cell': {'text': str(team_or_adj.coverage) + "%"}
    })
    ddict.append({
        'head': {
            'key': 'Owed',
            'icon': 'glyphicon-remove',
            'tooltip': 'Unsubmitted Feedbacks',
        },
        'cell': {'text': str(team_or_adj.owed_ballots) + "%"}
    })
    ddict.append({
        'head': {
            'key': 'Submitted',
            'icon': 'glyphicon-ok',
            'tooltip': 'Submitted Feedbacks',
        },
        'cell': {'text': str(team_or_adj.submitted_ballots) + "%"}
    })

    return ddict


def get_feedback_progress(t):
    def calculate_coverage(submitted, total):
        if total == 0 or submitted == 0:
            return 0  # Avoid divide-by-zero error
        else:
            return int(submitted / total * 100)

    feedback = AdjudicatorFeedback.objects.select_related(
        'source_adjudicator__adjudicator', 'source_team__team').all()
    adjudicators = Adjudicator.objects.filter(tournament=t)
    adjudications = list(
        DebateAdjudicator.objects.select_related('adjudicator', 'debate').filter(
            debate__round__stage=Round.STAGE_PRELIMINARY))
    teams = Team.objects.filter(tournament=t)

    # Teams only owe feedback on non silent rounds
    rounds_owed = t.round_set.filter(
        silent=False, stage=Round.STAGE_PRELIMINARY, draw_status=t.current_round.STATUS_RELEASED).count()

    for adj in adjudicators:
        adj.total_ballots = 0
        adj.submitted_feedbacks = feedback.filter(source_adjudicator__adjudicator=adj)
        adjs_adjudications = [a for a in adjudications if a.adjudicator == adj]

        for item in adjs_adjudications:
            # Finding out the composition of their panel, tallying owed ballots
            if item.type == item.TYPE_CHAIR:
                adj.total_ballots += len(item.debate.adjudicators.trainees)
                adj.total_ballots += len(item.debate.adjudicators.panel)

            if item.type == item.TYPE_PANEL:
                # Panelists owe on chairs
                adj.total_ballots += 1

            if item.type == item.TYPE_TRAINEE:
                # Trainees owe on chairs
                adj.total_ballots += 1

        adj.submitted_ballots = max(adj.submitted_feedbacks.count(), 0)
        adj.owed_ballots = max((adj.total_ballots - adj.submitted_ballots), 0)
        adj.coverage = min(calculate_coverage(adj.submitted_ballots, adj.total_ballots), 100)

    for team in teams:
        team.submitted_ballots = max(feedback.filter(source_team__team=team).count(), 0)
        team.owed_ballots = max((rounds_owed - team.submitted_ballots), 0)
        team.coverage = min(calculate_coverage(team.submitted_ballots, rounds_owed), 100)

    return teams, adjudicators
