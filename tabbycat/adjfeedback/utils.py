import logging
from statistics import mean, StatisticsError

from django.db.models import Avg, Count, Prefetch, Q

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from draw.models import DebateTeam
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
        if adjudicators.has_chair:
            targets = [(adjudicators.chair, AdjudicatorAllocation.POSITION_CHAIR)]
        else:
            logger.warning("Panellist has no chair to give feedback on")
            targets = []
    else:
        targets = []

    if feedback_paths not in ['all-adjs', 'with-p-on-c', 'minimal']:
        logger.error("Unrecognised preference: %s", feedback_paths)

    return targets


def get_feedback_overview(t, adjudicators):
    """Collates feedback statistics for the feedback overview."""

    rounds = list(t.prelim_rounds(until=t.current_round))  # force to list for performance in next querysets

    annotated_adjs = adjudicators.filter(id__in=[adj.id for adj in adjudicators]).prefetch_related(
        Prefetch('adjudicatorfeedback_set', to_attr='adjfeedback_for_rounds',
            queryset=AdjudicatorFeedback.objects.filter(
                Q(source_adjudicator__debate__round__in=rounds) | Q(source_team__debate__round__in=rounds),
                confirmed=True,
            ).exclude(
                source_adjudicator__type=DebateAdjudicator.TYPE_TRAINEE
            ).select_related('source_adjudicator__debate__round', 'source_team__debate__round')
        ),
        Prefetch('debateadjudicator_set', to_attr='debateadjs_for_rounds',
            queryset=DebateAdjudicator.objects.filter(
                debate__round__in=rounds).select_related('debate__round')),
        Prefetch('debateadjs_for_rounds__speakerscorebyadj_set',
            queryset=SpeakerScoreByAdj.objects.filter(
                debate_adjudicator__debate__round__in=rounds
            ).select_related('debate_team')
        ),
    ).annotate(debates=Count('debateadjudicator'))
    annotated_adjs_by_id = {adj.id: adj for adj in annotated_adjs}

    adjs_with_scores = adjudicators.filter(
        debateadjudicator__speakerscorebyadj__position__lte=t.last_substantive_position,
    ).annotate(
        avg_score=Avg('debateadjudicator__speakerscorebyadj__score'),
    )
    avg_scores = {adj.id: adj.avg_score for adj in adjs_with_scores}

    for adj in adjudicators:
        annotated_adj = annotated_adjs_by_id[adj.id]
        adj.debates = annotated_adj.debates
        adj.feedback_data = feedback_stats(annotated_adj, rounds)
        adj.avg_score = avg_scores.get(adj.id, None)  # might not exist, because of the filter
        adj.avg_margin = compute_avg_margin(annotated_adj)

    return adjudicators


def compute_avg_margin(adj):
    """Computes the average margin given by an adjudicator. Assumes
    adj.debateadj_for_rounds is populated as in get_feedback_overview()."""

    margins = []
    for da in adj.debateadjs_for_rounds:
        aff_total = 0
        neg_total = 0
        for ssba in da.speakerscorebyadj_set.all():
            if ssba.debate_team.side == DebateTeam.SIDE_AFF:
                aff_total += ssba.score
            elif ssba.debate_team.side == DebateTeam.SIDE_NEG:
                neg_total += ssba.score
        margin = abs(aff_total - neg_total)
        margins.append(margin)

    try:
        return mean(margins)
    except StatisticsError:
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

    # Start with test score
    feedback_data = [{'x': 0, 'y': adj.test_score, 'position': "Test Score"}]

    # Sort into rounds
    feedback_by_round = {r: [] for r in rounds}
    for fb in adj.adjfeedback_for_rounds:
        feedback_by_round[fb.round].append(fb)

    debateadjs_by_round = dict.fromkeys(rounds, None)
    for da in adj.debateadjs_for_rounds:
        debateadjs_by_round[da.debate.round] = da

    for r in rounds:
        scores = [fb.score for fb in feedback_by_round[r]]
        if scores:
            feedback_data.append({
                'x': r.seq,
                'y': round(mean(scores), 2),  # average score
                'position_class': adj_classes[debateadjs_by_round[r].type],
                'position': debateadjs_by_round[r].get_type_display(),
            })

    return feedback_data
