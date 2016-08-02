import logging

from django.core.exceptions import ObjectDoesNotExist

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from results.models import SpeakerScoreByAdj

logger = logging.getLogger(__name__)


def expected_feedback_targets(debateadj, feedback_paths=None, debate=None):
    """Returns a list of adjudicators and positions (adj, pos), each being
    someone that the given DebateAdjudicator object is expected to give feedback
    on. If the debate adjudicator's position and the tournament preferences
    dictate that the source adjudicator should not submit feedback on anyone for
    this debate, then it returns an empty list.

    Each element of the returned list is a 2-tuple `(adj, pos)`, where `adj` is
    an Adjudicator instance and `pos` is an AdjudicatorAllocation.POSITION_*
    constant. DebateAdjudicator instances are not returned by this function; in
    fact, the use of DebateAdjudicator instances for feedback targets is in
    general discouraged, since feedback targets are Adjudicator instances, not
    DebateAdjudicator instances.

    `feedback_paths` can be used to avoid unnecessary tournament lookups,
    and should be one of the available options in
    options.dynamic_preferences_registry.FeedbackPaths.choices.

    `debate` can be used to avoid unnecessary database hits populating
    AdjudicatorAllocation, and should be equal to debateadj.debate.
    """

    if feedback_paths is None:
        feedback_paths = debateadj.debate.round.tournament.pref('feedback_paths')
    if debate is None:
        debate = debateadj.debate
    adjudicators = debate.adjudicators

    if feedback_paths == 'all-adjs' or debateadj.type == DebateAdjudicator.TYPE_CHAIR:
        targets = [(adj, pos) for adj, pos in adjudicators.with_positions() if adj.id != debateadj.adjudicator_id]
    elif feedback_paths == 'with-p-on-c' and debateadj.type == DebateAdjudicator.TYPE_PANEL:
        targets = [(adjudicators.chair, AdjudicatorAllocation.POSITION_CHAIR)]
    else:
        targets = []

    if feedback_paths not in ['all-adjs', 'with-p-on-c', 'minimal']:
        logger.error("Unrecognised preference: {!r}".format(feedback_paths))

    return targets


def get_feedback_overview(t, adjudicators):

    all_debate_adjudicators = list(DebateAdjudicator.objects.all().select_related(
        'adjudicator'))
    all_adj_feedbacks = list(AdjudicatorFeedback.objects.filter(confirmed=True).select_related(
        'adjudicator', 'source_adjudicator', 'source_team',
        'source_adjudicator__debate__round', 'source_team__debate__round').exclude(
            source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE))
    all_adj_scores = list(SpeakerScoreByAdj.objects.filter(
        ballot_submission__confirmed=True).exclude(position=t.REPLY_POSITION).select_related(
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
                largest_difference = max(t_a_total, t_b_total)
                smallest_difference = min(t_a_total, t_b_total)
                ballot_margins.append(
                    largest_difference - smallest_difference)
            except TypeError:
                print(team_split)

        if ballot_margins:
            print('has %s margins %s' % (len(ballot_margins), ballot_margins))
            adj.avg_margin = sum(ballot_margins) / len(ballot_margins)

    return adj


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
