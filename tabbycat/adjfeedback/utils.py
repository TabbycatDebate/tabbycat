import logging
from statistics import mean, stdev

from django.db.models import Count, Prefetch, Q

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from options.preferences import FeedbackPaths

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
    options.preferences.FeedbackPaths.choices.

    `debate` can be used to avoid unnecessary database hits populating
    AdjudicatorAllocation, and should be equal to debateadj.debate.
    """

    if feedback_paths is None:
        feedback_paths = debateadj.debate.round.tournament.pref('feedback_paths')
    if feedback_paths not in [o[0] for o in FeedbackPaths.choices]:
        logger.error("Unrecognised preference: %s", feedback_paths)

    # Need to associate the feedback submission status with the Adjudicator object
    # directly to be passed onto AdjudicatorAllocation. Must use debateadj to assure
    # the prefetch is available.
    if hasattr(debateadj.debate.debateadjudicator_set.first(), 'submitted'):
        for dadj in debateadj.debate.debateadjudicator_set.all():
            dadj.adjudicator.submitted = dadj.submitted

    if debate is None:
        debate = debateadj.debate
    adjudicators = debate.adjudicators

    if feedback_paths == 'all-adjs' or debateadj.type == DebateAdjudicator.TYPE_CHAIR:
        targets = [(adj, pos) for adj, pos in adjudicators.with_positions() if adj.id != debateadj.adjudicator_id]
    elif feedback_paths == 'with-p-on-c' and debateadj.type == DebateAdjudicator.TYPE_PANEL:
        if adjudicators.has_chair:
            targets = [(adjudicators.chair, AdjudicatorAllocation.POSITION_CHAIR)]
        else:
            logger.warning("Panellist has no chair to give feedback on")
            targets = []
    else:
        targets = []

    return targets


def get_feedback_overview(t, adjudicators):
    """Collates feedback statistics for the feedback overview."""

    rounds = list(t.prelim_rounds(until=t.current_round))  # force to list for performance in next querysets

    annotated_adjs = adjudicators.filter(id__in=[adj.id for adj in adjudicators]).prefetch_related(
        Prefetch('adjudicatorfeedback_set', to_attr='adjfeedback_for_rounds',
            queryset=AdjudicatorFeedback.objects.filter(
                Q(source_adjudicator__debate__round__in=rounds) | Q(source_team__debate__round__in=rounds),
                confirmed=True,
                ignored=False,
            ).exclude(
                source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE,
            ).select_related('source_adjudicator__debate__round', 'source_team__debate__round'),
        ),
        Prefetch('debateadjudicator_set', to_attr='debateadjs_for_rounds',
            queryset=DebateAdjudicator.objects.filter(
                debate__round__in=rounds).select_related('debate__round')),
    ).annotate(debates=Count('debateadjudicator'))
    annotated_adjs_by_id = {adj.id: adj for adj in annotated_adjs}

    for adj in adjudicators:
        annotated_adj = annotated_adjs_by_id[adj.id]
        adj.debates = annotated_adj.debates
        adj.feedback_data = feedback_stats(annotated_adj, rounds)
        adj.feedback_variance = feedback_variance(annotated_adj, rounds)

    return adjudicators


def feedback_variance(adj, rounds):
    feedback_scores = [fb.score for fb in adj.adjfeedback_for_rounds]
    feedback_scores.append(adj.base_score)
    if len(feedback_scores) > 1:
        return stdev(feedback_scores)
    else:
        return None


def feedback_stats(adj, rounds):
    """Collates the feedback statistics for an adjudicator. Assumes
    adj.adjfeedback_for_rounds and adj.debateadj_for_rounds are populated as in
    get_feedback_overview()."""

    adj_classes = {  # Do not translate
        DebateAdjudicator.TYPE_CHAIR: "chair",
        DebateAdjudicator.TYPE_PANEL: "panellist",
        DebateAdjudicator.TYPE_TRAINEE: "trainee",
    }

    # Start with base score
    feedback_data = [{'x': 0, 'y': adj.base_score, 'position': "Base Score"}]

    # Sort into rounds
    feedback_by_round = {r: [] for r in rounds}
    for fb in adj.adjfeedback_for_rounds:
        feedback_by_round[fb.round].append(fb)

    debateadjs_by_round = dict.fromkeys(rounds, None)
    for da in adj.debateadjs_for_rounds:
        debateadjs_by_round[da.debate.round] = da

    for r in rounds:
        scores = [fb.score for fb in feedback_by_round[r]]
        if scores and debateadjs_by_round[r]:
            feedback_data.append({
                'x': r.seq,
                'y': round(mean(scores), 2),  # average score
                'position_class': adj_classes[debateadjs_by_round[r].type],
                'position': debateadjs_by_round[r].get_type_display(),
            })

    return feedback_data
