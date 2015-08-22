"""Adds randomly generated feedbacks to the given debates, with probability
specified"""

import header
import adjfeedback.models as fm

from draw.models import Debate, DebateTeam
from participants.models import Team, Adjudicator

from django.contrib.auth.models import User
from results.result import BallotSet
from adjallocation.models import DebateAdjudicator

import random
import itertools

SUBMITTER_TYPE_MAP = {
    'tabroom': fm.AdjudicatorFeedback.SUBMITTER_TABROOM,
    'public':  fm.AdjudicatorFeedback.SUBMITTER_PUBLIC
}

WORDS = {
    5: ["perfect", "outstanding", "super", "collected", "insightful"],
    4: ["great", "methodical", "logical", "insightful", "happy"],
    3: ["middler", "average", "solid", "fair", "clear"],
    2: ["biased", "unclear", "convoluted", "learning", "smart"],
    1: ["useless", "incompetent", "novice", "stupid", "biased"],
}

COMMENTS = {
    5: ["Amazeballs.", "Saw it exactly how we did.", "Couldn't have been better.", "Really insightful feedback."],
    4: ["Great adjudication but parts were unclear.", "Clear but a bit long. Should break.", "Understood debate but missed a couple of nuances.", "Agreed with adjudication but feedback wasn't super helpful."],
    3: ["Identified all main issues, didn't see interactions between them.", "Solid, would trust to get right, but couldn't articulate some points.", "Pretty good for a novice adjudicator.", "Know what (s)he's doing but reasoning a bit convoluted."],
    2: ["Missed some crucial points in the debate.", "Stepped into debate, but not too significantly.", "Didn't give the other team enough credit for decent points.", "Had some awareness of the debate but couldn't identify main points."],
    1: ["It's as if (s)he was listening to a different debate.", "Worst adjudication I've ever seen.", "Give his/her own analysis to rebut our arguments.", "Should not be adjudicating at this tournament."]
}

def add_feedback(debate, submitter_type, user, probability=1.0, discarded=False, confirmed=False):

    if discarded and confirmed:
        raise ValueError("Feedback can't be both discarded and confirmed!")

    sources_and_subjects = [
        (debate.aff_team, debate.adjudicators.chair),
        (debate.neg_team, debate.adjudicators.chair),
    ]
    sources_and_subjects.extend(itertools.permutations(
            (adj for type, adj in debate.adjudicators), 2))

    fbs = list()

    for source, adj in sources_and_subjects:

        if random.random() > probability:
            print(" - Skipping", source, "on", adj)
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
                    answer = fm.AdjudicatorFeedbackQuestion.CHOICE_SEPARATOR.join(a[0] for a in answers)
                else:
                    answer = random.choice(WORDS[score])
            question.answer_type_class(question=question, feedback=fb, answer=answer).save()

        print(source, "on", adj, ":", score)

        fbs.append(fb)

    return fbs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("debate", type=int, nargs='+', help="Debate ID(s) to add to")
    parser.add_argument("-p", "--probability", type=float, help="Probability with which to add feedback", default=1.0)
    parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=list(SUBMITTER_TYPE_MAP.keys()), default="tabroom")
    parser.add_argument("-u", "--user", type=str, help="User ID", default="random")
    status = parser.add_mutually_exclusive_group(required=True)
    status.add_argument("-d", "--discarded", action="store_true", help="Ballot set is discarded")
    status.add_argument("-c", "--confirmed", action="store_true", help="Ballot set is confirmed")
    args = parser.parse_args()

    submitter_type = SUBMITTER_TYPE_MAP[args.type]
    if submitter_type == fm.AdjudicatorFeedback.SUBMITTER_TABROOM:
        user = User.objects.get(username=args.user)
    else:
        user = None

    for debate_id in args.debate:
        debate = Debate.objects.get(id=debate_id)

        print(debate)

        try:
            fbs = add_feedback(debate, submitter_type, user, args.probability, args.discarded, args.confirmed)
        except ValueError as e:
            print("Error:", e)
