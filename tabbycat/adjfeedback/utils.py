from django.core.exceptions import ObjectDoesNotExist

from adjallocation.models import DebateAdjudicator
from participants.models import Adjudicator, Team
from results.models import SpeakerScoreByAdj
from tournaments.models import Round
from utils.tables import TabbycatTableBuilder
from utils.misc import reverse_tournament

from .models import AdjudicatorFeedback
from .progress import FeedbackProgressForAdjudicator, FeedbackProgressForTeam


class FeedbackTableBuilder(TabbycatTableBuilder):

    def add_breaking_checkbox(self, adjudicators, key="Breaking"):
        breaking_header = {
            'key': 'B',
            'icon': 'glyphicon-star',
            'tooltip': 'Whether the adj is marked as breaking (click to mark)',
        }
        breaking_data = [{
            'text': '<input type="checkbox" class="toggle_breaking_status vue-table-checkbox" adj_id="%s" %s>' % (adj.id, 'checked' if adj.breaking else ''),
            'sort': adj.breaking,
            'class': 'checkbox-target'
        } for adj in adjudicators]

        self.add_column(breaking_header, breaking_data)

    def add_score_columns(self, adjudicators):

        feedback_weight = self.tournament.current_round.feedback_weight
        scores = {adj: adj.weighted_score(feedback_weight) for adj in adjudicators}

        overall_header = {
            'key': 'Overall Score',
            'icon': 'glyphicon-signal',
            'tooltip': 'Current weighted score',
        }
        overall_data = [{
            'text': '<strong>%0.1f</strong>' % scores[adj] if scores[adj] is not None else 'N/A',
            'tooltip': 'Current weighted average of all feedback',
        } for adj in adjudicators]
        self.add_column(overall_header, overall_data)

        test_header = {
            'key': 'Test Score',
            'icon': 'glyphicon-scale',
            'tooltip': 'Test score result',
        }
        test_data = [{
            'text': '%0.1f' % adj.test_score if adj.test_score is not None else 'N/A',
            'modal': adj.id,
            'class': 'edit-test-score',
            'tooltip': 'Click to edit test score',
        } for adj in adjudicators]
        self.add_column(test_header, test_data)

    def add_feedback_graphs(self, adjudicators):
        feedback_head = {
            'key': 'Feedback',
            'text': 'Feedback as <span class="position-display chair">&nbsp;Chair&nbsp;</span>' +
            ' <span class="position-display panellist">&nbsp;Panellist&nbsp;</span>' +
            ' <span class="position-display trainee">&nbsp;Trainee&nbsp;</span>'
        }
        feedback_data = [{
            'graphData': adj.feedback_data,
            'component': 'feedback-trend',
            'minScore': self.tournament.pref('adj_min_score'),
            'maxScore': self.tournament.pref('adj_max_score'),
            'roundSeq': self.tournament.current_round.seq,
        } for adj in adjudicators]
        self.add_column(feedback_head, feedback_data)

    def add_feedback_link_columns(self, adjudicators):
        link_head = {
            'key': 'VF',
            'icon': 'glyphicon-question-sign'
        }
        link_cell = [{
            'text': 'View<br>Feedback',
            'class': 'view-feedback',
            'link': reverse_tournament('adjfeedback-view-on-adjudicator', self.tournament, kwargs={'pk': adj.pk})
        } for adj in adjudicators]
        self.add_column(link_head, link_cell)

    def add_feedback_misc_columns(self, adjudicators):
        if self.tournament.pref('enable_adj_notes'):
            note_head = {
                'key': 'NO',
                'icon': 'glyphicon-list-alt'
            }
            note_cell = [{
                'text': 'Edit<br>Note',
                'class': 'edit-note',
                'modal': str(adj.id) + '===' + str(adj.notes)
            } for adj in adjudicators]
            self.add_column(note_head, note_cell)

        adjudications_head = {
            'key': 'DD',
            'icon': 'glyphicon-eye-open',
            'tooltip': 'Debates adjudicated'
        }
        adjudications_cell = [{'text': adj.debates} for adj in adjudicators]
        self.add_column(adjudications_head, adjudications_cell)

        avgs_head = {
            'key': 'AVGS',
            'icon': 'glyphicon-resize-full',
            'tooltip': 'Average Margin (top) and Average Score (bottom)'
        }
        avgs_cell = [{
            'text': "%0.1f<br>%0.1f" % (adj.avg_margin if adj.avg_margin else 0, adj.avg_score if adj.avg_margin else 0)
        } for adj in adjudicators]
        self.add_column(avgs_head, avgs_cell)

    def add_feedback_progress_columns(self, progress, key="P"):

        coverage_header = {
            'key': 'Coverage',
            'icon': 'glyphicon-eye-open',
            'tooltip': 'Percentage of feedback returned',
        }
        coverage_data = [{
            'text': str(team_or_adj.coverage) + "%"
        } for team_or_adj in progress]
        self.add_column(coverage_header, coverage_data)

        owed_header = {
            'key': 'Owed',
            'icon': 'glyphicon-remove',
            'tooltip': 'Unsubmitted feedback ballots',
        }
        owed_data = [{
            'text': str(team_or_adj.owed_ballots)
        } for team_or_adj in progress]
        self.add_column(owed_header, owed_data)

        submitted_header = {
            'key': 'Submitted',
            'icon': 'glyphicon-ok',
            'tooltip': 'Submitted feedback ballots',
        }
        submitted_data = [{
            'text': str(team_or_adj.submitted_ballots)
        } for team_or_adj in progress]
        self.add_column(submitted_header, submitted_data)

        if self._show_record_links:
            owed_link_header = {
                'key': 'Submitted',
                'icon': 'glyphicon-question-sign',
            }
            owed_link_data = [{
                'text': 'View Missing',
                'link': team_or_adj.missing_admin_link if self.admin else team_or_adj.missing_public_link
            } for team_or_adj in progress]
            self.add_column(owed_link_header, owed_link_data)


def get_feedback_overview(t, adjudicators):

    all_debate_adjudicators = list(DebateAdjudicator.objects.all().select_related(
        'adjudicator'))
    all_adj_feedbacks = list(AdjudicatorFeedback.objects.filter(confirmed=True).select_related(
        'adjudicator', 'source_adjudicator', 'source_team',
        'source_adjudicator__debate__round', 'source_team__debate__round').exclude(
            source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE))
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


def get_feedback_progress_new(t):
    """This turns out to be really, really inefficient. Continue using the
    original function until a better way can be found."""

    adjudicators = Adjudicator.objects.filter(tournament=t)
    teams = Team.objects.filter(tournament=t)

    for team in teams:
        progress = FeedbackProgressForTeam(team)
        team.submitted_ballots = progress.num_fulfilled()
        team.owed_ballots = progress.num_unsubmitted()
        team.coverage = progress.coverage()
        print(team)

    for adj in adjudicators:
        progress = FeedbackProgressForAdjudicator(adj)
        adj.submitted_ballots = progress.num_fulfilled()
        adj.owed_ballots = progress.num_unsubmitted()
        adj.coverage = progress.coverage()
        print(adj)

    return teams, adjudicators


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

    total_possible = 0
    total_submitted = 0

    for adj in adjudicators:
        adj.total_ballots = 0
        adj.submitted_feedbacks = feedback.filter(source_adjudicator__adjudicator=adj)
        adjs_adjudications = [a for a in adjudications if a.adjudicator == adj]

        for item in adjs_adjudications:
            # Finding out the composition of their panel, tallying owed ballots
            if item.type == item.TYPE_CHAIR:
                adj.total_ballots += len(item.debate.adjudicators.trainees)
                adj.total_ballots += len(item.debate.adjudicators.panellists)

            if item.type == item.TYPE_PANEL:
                # Panelists owe on chairs
                adj.total_ballots += 1

            if item.type == item.TYPE_TRAINEE:
                # Trainees owe on chairs
                adj.total_ballots += 1

        adj.submitted_ballots = max(adj.submitted_feedbacks.count(), 0)
        adj.owed_ballots = max((adj.total_ballots - adj.submitted_ballots), 0)
        adj.coverage = min(calculate_coverage(adj.submitted_ballots, adj.total_ballots), 100)
        adj.missing_admin_link = reverse_tournament(
            'participants-adjudicator-record', t, kwargs={'pk': adj.pk})
        adj.missing_public_link = reverse_tournament(
            'participants-public-adjudicator-record', t, kwargs={'pk': adj.pk})
        total_possible += len(adjs_adjudications)
        total_submitted += adj.submitted_ballots

    for team in teams:
        team.submitted_ballots = max(feedback.filter(source_team__team=team).count(), 0)
        team.owed_ballots = max((rounds_owed - team.submitted_ballots), 0)
        team.coverage = min(calculate_coverage(team.submitted_ballots, rounds_owed), 100)
        team.missing_admin_link = reverse_tournament(
            'participants-team-record', t, kwargs={'pk': team.pk})
        team.missing_public_link = reverse_tournament(
            'participants-public-team-record', t, kwargs={'pk': team.pk})
        total_possible += rounds_owed
        total_submitted += team.submitted_ballots

    print(total_submitted, total_possible)
    total_coverage = calculate_coverage(total_submitted, total_possible)

    return teams, adjudicators, total_coverage


def parse_feedback(feedback, questions):

    if feedback.source_team:
        source_annotation = " (" + feedback.source_team.result + ")"
    elif feedback.source_adjudicator:
        source_annotation = " (" + feedback.source_adjudicator.get_type_display() + ")"
    else:
        source_annotation = ""

    data = {
        'round': feedback.round.abbreviation,
        'version': str(feedback.version) + (feedback.confirmed and "*" or ""),
        'bracket': feedback.debate.bracket,
        'matchup': feedback.debate.matchup,
        'source': feedback.source,
        'source_note': source_annotation,
        'score': feedback.score,
        'questions': []
    }

    for question in questions:
        q = {
            'reference': question.reference,
            'text': question.text,
            'name': question.name
        }
        try:
            q['answer'] = question.answer_set.get(feedback=feedback).answer
        except ObjectDoesNotExist:
            q['answer'] = "-"

        data['questions'].append(q)

    return data
