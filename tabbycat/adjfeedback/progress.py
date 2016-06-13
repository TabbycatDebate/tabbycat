from adjallocation.models import DebateAdjudicator
from participants.models import Adjudicator, Team
from tournaments.models import Round

from .models import AdjudicatorFeedback


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
