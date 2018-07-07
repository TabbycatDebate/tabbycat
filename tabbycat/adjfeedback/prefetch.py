from adjallocation.models import DebateAdjudicator


def populate_debate_adjudicators(feedbacks):
    adjudicators = [feedback.adjudicator for feedback in feedbacks]
    debates = [feedback.debate for feedback in feedbacks]
    debateadjs = DebateAdjudicator.objects.filter(adjudicator__in=adjudicators, debate__in=debates)
    debateadjs_by_ids = {(da.adjudicator_id, da.debate_id): da for da in debateadjs}
    for feedback in feedbacks:
        try:
            feedback._debateadj = debateadjs_by_ids[(feedback.adjudicator_id, feedback.debate.id)]
        except KeyError:
            # This occurs when the matching debate adjudicator for this feedback no longer exists
            # This absence will be highlighted on the front-end through the feedback card
            pass
