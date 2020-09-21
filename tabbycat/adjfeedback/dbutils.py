"""Contains utilities that add or remove things from the database, relating
to adjudicator feedback.

These are mainly used in management commands, but in principle could be used
by a front-end interface as well."""

import itertools
import logging
import random

from django.contrib.auth import get_user_model

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam
from participants.models import Adjudicator, Team

from . import models as fm

logger = logging.getLogger(__name__)
User = get_user_model()

WORDS = {
    5: ["perfect", "outstanding", "super", "collected", "insightful"],
    4: ["great", "methodical", "logical", "insightful", "happy"],
    3: ["middler", "average", "solid", "fair", "clear"],
    2: ["biased", "unclear", "convoluted", "learning", "smart"],
    1: ["useless", "incompetent", "novice", "stupid", "biased"],
}

COMMENTS = {
    5: [
        "Amazeballs.",
        "Saw it exactly how we did.",
        "Couldn't have been better.",
        "Really insightful feedback.",
    ],
    4: [
        "Great adjudication but parts were unclear.",
        "Clear but a bit long. Should break.",
        "Understood debate but missed a couple of nuances.",
        "Agreed with adjudication but feedback wasn't super helpful.",
    ],
    3: [
        "Identified all main issues, didn't see interactions between them.",
        "Solid, would trust to get right, but couldn't articulate some points.",
        "Pretty good for a novice adjudicator.",
        "Know what (s)he's doing but reasoning a bit convoluted.",
    ],
    2: [
        "Missed some crucial points in the debate.",
        "Stepped into debate, but not too significantly.",
        "Didn't give the other team enough credit for decent points.",
        "Had some awareness of the debate but couldn't identify main points.",
    ],
    1: [
        "It's as if (s)he was listening to a different debate.",
        "Worst adjudication I've ever seen.",
        "Gave his/her own analysis to rebut our arguments.",
        "Should not be adjudicating at this tournament.",
    ],
}


def add_feedback_to_round(round, **kwargs):
    """Calls add_feedback() for every debate in the given round."""
    for debate in round.debate_set_with_prefetches():
        add_feedback(debate, **kwargs)


def delete_all_feedback_for_round(round):
    """Deletes all feedback for the given round."""
    fm.AdjudicatorFeedback.objects.filter(source_adjudicator__debate__round=round).delete()
    fm.AdjudicatorFeedback.objects.filter(source_team__debate__round=round).delete()


def delete_feedback(debate):
    """Deletes all feedback for the given debate."""
    fm.AdjudicatorFeedback.objects.filter(source_adjudicator__debate=debate).delete()
    fm.AdjudicatorFeedback.objects.filter(source_team__debate=debate).delete()


def add_feedback(debate, submitter_type, user, probability=1.0, discarded=False, confirmed=False):
    """Adds feedback to a debate.
    Specifically, adds feedback from both teams on the chair, and from every
    adjudicator on every other adjudicator.

    ``debate`` is the Debate to which feedback should be added.
    ``submitter_type`` is a valid value of AdjudicatorFeedback.submitter_type.
    ``user`` is a User object.
    ``probability``, a float between 0.0 and 1.0, is the probability with which
        feedback is generated.
    ``discarded`` and ``confirmed`` are whether the feedback should be
        discarded or confirmed, respectively."""

    if discarded and confirmed:
        raise ValueError("Feedback can't be both discarded and confirmed!")

    if debate.adjudicators.chair is None:
        raise ValueError("This debate ({}) doesn't have a chair.".format(debate.matchup))

    if debate.round.tournament.pref('feedback_from_teams') == 'all-adjs':
        sources_and_subjects = [(team, adj) for team in debate.teams for adj in debate.adjudicators.all()]
    else:
        sources_and_subjects = [(team, debate.adjudicators.chair) for team in debate.teams]

    sources_and_subjects.extend(itertools.permutations(
        (adj for adj, position in debate.adjudicators.with_debateadj_types()), 2))

    fbs = list()

    for source, adj in sources_and_subjects:

        if random.random() > probability:
            logger.info(" - Skipping %s on %s", source, adj)
            continue

        fb = fm.AdjudicatorFeedback(submitter_type=submitter_type)
        if submitter_type == fm.AdjudicatorFeedback.SUBMITTER_TABROOM:
            fb.submitter = user

        fb.adjudicator = adj
        if isinstance(source, Adjudicator):
            fb.source_adjudicator = DebateAdjudicator.objects.get(
                debate=debate, adjudicator=source)
        elif isinstance(source, Team):
            fb.source_team = DebateTeam.objects.get(
                debate=debate, team=source)
        else:
            raise TypeError("source must be an Adjudicator or a Team")

        score = float(random.randrange(1, 6))
        fb.score = score

        fb.discarded = discarded
        fb.confirmed = confirmed
        fb.save()

        for question in debate.round.tournament.adj_feedback_questions:
            if fb.source_team and not question.from_team:
                continue
            if fb.source_adjudicator and not question.from_adj:
                continue

            if question.answer_type_class == fm.AdjudicatorFeedbackBooleanAnswer:
                answer = random.choice([None, True, False])
                if answer is None:
                    continue
            elif question.answer_type_class == fm.AdjudicatorFeedbackIntegerAnswer:
                min_value = int(question.min_value) or 0
                max_value = int(question.max_value) or 10
                answer = random.randrange(min_value, max_value+1)
            elif question.answer_type_class == fm.AdjudicatorFeedbackFloatAnswer:
                min_value = question.min_value or 0
                max_value = question.max_value or 10
                answer = random.uniform(min_value, max_value)
            elif question.answer_type_class == fm.AdjudicatorFeedbackStringAnswer:
                if question.answer_type == fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_LONGTEXT:
                    answer = random.choice(COMMENTS[score])
                elif question.answer_type == fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_SINGLE_SELECT:
                    answer = random.choice(question.choices_for_field)[0]
                elif question.answer_type == fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_MULTIPLE_SELECT:
                    answers = random.sample(question.choices_for_field, random.randint(0, len(question.choices_for_field)))
                    answer = [a[0] for a in answers]
                else:
                    answer = random.choice(WORDS[score])
            question.answer_type_class(question=question, feedback=fb, answer=answer).save()

        name = source.name if isinstance(source, Adjudicator) else source.short_name
        logger.info("[%s] %s on %s: %s", debate.round.tournament.slug, name, adj, score)

        fbs.append(fb)

    return fbs
