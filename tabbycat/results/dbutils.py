"""Contains utilities that add or remove things from the database, relating
to results of debates.

These are mainly used in management commands, but in principle could be used
by a front-end interface as well."""

import random
import logging

from django.contrib.auth import get_user_model

from draw.models import Debate
from results.models import BallotSubmission
from results.result import VotingDebateResult

logger = logging.getLogger(__name__)
User = get_user_model()


def add_results_to_round(round, **kwargs):
    """Calls add_result() for every debate in the given round."""
    for debate in round.debate_set.all():
        add_result(debate, **kwargs)


def add_results_to_round_partial(round, num, **kwargs):
    """Calls ``add_result()`` on ``num`` randomly-chosen debates in the given round."""
    debates = random.sample(list(round.debate_set.all()), num)
    for debate in debates:
        add_result(debate, **kwargs)


def delete_all_ballotsubs_for_round(round):
    """Deletes all ballot sets from the given round."""
    BallotSubmission.objects.filter(debate__round=round).delete()


def delete_ballotsub(debate):
    """Deletes all ballot sets from the given debate."""
    debate.ballotsubmission_set.all().delete()


def add_result(debate, submitter_type, user, discarded=False, confirmed=False,
                  min_score=72, max_score=78, reply_random=False):
    """Adds a ballot set to a debate.

    ``debate`` is the Debate to which the ballot set should be added.
    ``submitter_type`` is a valid value of BallotSubmission.submitter_type.
    ``user`` is a User object.
    ``discarded`` and ``confirmed`` are whether the feedback should be discarded or
        confirmed, respectively.
    ``min_score`` and ``max_score`` are the range in which scores should be generated."""

    if discarded and confirmed:
        raise ValueError("Ballot can't be both discarded and confirmed!")

    last_substantive_position = debate.round.tournament.last_substantive_position
    reply_position = debate.round.tournament.reply_position

    # Create a new BallotSubmission
    bsub = BallotSubmission(submitter_type=submitter_type, debate=debate)
    if submitter_type == BallotSubmission.SUBMITTER_TABROOM:
        bsub.submitter = user
    bsub.save()

    def gen_results():
        r = {'aff': (0,), 'neg': (0,)}

        def do():
            s = [random.randint(min_score, max_score) for i in range(last_substantive_position)]
            s.append(random.randint(min_score, max_score)/2)
            return s
        while sum(r['aff']) == sum(r['neg']):
            r['aff'] = do()
            r['neg'] = do()
        return r

    rr = dict()
    for adj in debate.adjudicators.voting():
        rr[adj] = gen_results()

    # Create relevant scores
    result = VotingDebateResult(bsub)

    for side in ('aff', 'neg'):
        speakers = getattr(debate, '%s_team' % side).speakers
        for i in range(1, last_substantive_position+1):
            result.set_speaker(side, i, speakers[i-1])
            result.set_ghost(side, i, False)

        reply_speaker = random.randint(0, last_substantive_position-1) if reply_random else 0
        result.set_speaker(side, reply_position, speakers[reply_speaker])
        result.set_ghost(side, reply_position, False)

        for adj in debate.adjudicators.voting():
            for pos in debate.round.tournament.positions:
                result.set_score(adj, side, pos, rr[adj][side][pos-1])

    result.save()

    # Pick a motion
    motions = debate.round.motion_set.all()
    if motions:
        motion = random.choice(motions)
        bsub.motion = motion

    bsub.discarded = discarded
    bsub.confirmed = confirmed

    bsub.save()

    # Update result status (only takes into account marginal effect, does not "fix")
    if confirmed:
        debate.result_status = Debate.STATUS_CONFIRMED
    elif not discarded and debate.result_status != Debate.STATUS_CONFIRMED:
        debate.result_status = Debate.STATUS_DRAFT
    debate.save()

    logger.info("{debate} won by {team} on {motion}".format(
        debate=debate.matchup, team=result.winning_side(),
        motion=bsub.motion and bsub.motion.reference or "<No motion>"))

    return result
