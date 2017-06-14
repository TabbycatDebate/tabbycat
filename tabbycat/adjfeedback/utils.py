import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

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
        logger.error("Unrecognised preference: %s", feedback_paths)

    return targets


def get_feedback_overview(t, adjudicators):

    rounds = list(t.prelim_rounds(until=t.current_round))
    debate_adjudicators = DebateAdjudicator.objects.filter(debate__round__tournament=t)
    all_feedbacks = AdjudicatorFeedback.objects.filter(
                        Q(source_adjudicator__debate__round__in=rounds) |
                        Q(source_team__debate__round__in=rounds), confirmed=True).select_related(
                        'adjudicator', 'source_adjudicator', 'source_team',
                        'source_adjudicator__debate__round',
                        'source_team__debate__round').exclude(
                        source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE)

    all_scores = SpeakerScoreByAdj.objects.filter(
                        ballot_submission__confirmed=True,
                        debate_adjudicator__debate__round__in=rounds).select_related(
                        'debate_adjudicator__adjudicator', 'ballot_submission').exclude(
                        position=t.REPLY_POSITION)

    for adj in adjudicators:
        # Gather feedback scores for graphs
        adj_feedbacks = [f for f in all_feedbacks if f.adjudicator == adj]
        adj_adjudications = [a for a in debate_adjudicators if a.adjudicator == adj]
        adj_scores = [s for s in all_scores if s.debate_adjudicator.adjudicator == adj]

        # Gather a dict of round-by-round feedback for the graph
        adj.feedback_data = feedback_stats(adj, rounds, adj_feedbacks, debate_adjudicators)
        # Sum up remaining stats
        adj = scoring_stats(adj, adj_scores, adj_adjudications)

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


def scoring_stats(adj, scores, adjudications):
    adj.debates = len(adjudications)
    adj.avg_score = None
    adj.avg_margin = None

    if len(scores) == 0 or len(adjudications) == 0:
        return adj

    adj.avg_score = sum(s.score for s in scores) / len(scores)
    # Figure out average margin by summing speaks (post splitting them in 2)
    ballot_ids = [s.ballot_submission for s in scores]
    ballot_ids = sorted(set([b.id for b in ballot_ids])) # Deduplicate
    ballot_margins = []

    for id in ballot_ids:
        # For each unique ballot id make an array of all its scores
        ballot_scores = [s.score for s in scores if s.ballot_submission.id == id]
        speakers = int(len(ballot_scores) / 2)

        # Get the team totals by summing each half of the scores array
        aff_pts = sum(ballot_scores[:speakers])
        neg_pts = sum(ballot_scores[speakers:])
        # The margin is the largest team pt difference - the smallest
        ballot_margins.append(max(aff_pts, neg_pts) - min(aff_pts, neg_pts))

    if ballot_margins:
        # print('%s has %s margins %s' % (adj, len(ballot_margins), ballot_margins))
        adj.avg_margin = sum(ballot_margins) / len(ballot_margins)

    return adj


def parse_feedback(feedback, questions):

    if feedback.source_team:
        source_annotation = " (" + feedback.source_team.get_result_display() + ")"
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
