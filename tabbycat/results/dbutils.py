"""Contains utilities that add or remove things from the database, relating
to results of debates.

These are mainly used in management commands, but in principle could be used
by a front-end interface as well."""

import logging
import random
from itertools import product

from django.contrib.auth import get_user_model

from draw.models import Debate
from results.models import BallotSubmission
from results.result import DebateResult

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


def fill_scoresheet_randomly(scoresheet, tournament, nattempts=1000):
    """Fills a scoresheet randomly. Operates in-place. Bails if it can't
    generate a valid scoresheet within 1000 attempts."""
    for attempt in range(nattempts):

        if scoresheet.uses_scores:
            for side, pos in product(scoresheet.sides, scoresheet.positions):
                if pos == tournament.reply_position:
                    step = tournament.pref('reply_score_step')
                    start = tournament.pref('reply_score_min') / step
                    stop = tournament.pref('reply_score_max') / step
                else:
                    step = tournament.pref('score_step')
                    start = tournament.pref('score_min') / step
                    stop = tournament.pref('score_max') / step
                score = random.randint(start, stop) * step
                scoresheet.set_score(side, pos, score)

        if scoresheet.uses_declared_winners:
            scoresheet.set_declared_winners(random.sample(scoresheet.sides, scoresheet.number_winners))

        if scoresheet.is_valid():
            break

    else:
        raise RuntimeError("Failed to generate valid scoresheet after %d attempts" % (nattempts,))


def add_result(debate, submitter_type, user, discarded=False, confirmed=False, reply_random=False):
    """Adds a ballot set to a debate.

    ``debate`` is the Debate to which the ballot set should be added.
    ``submitter_type`` is a valid value of BallotSubmission.submitter_type.
    ``user`` is a User object.
    ``discarded`` and ``confirmed`` are whether the feedback should be discarded or
        confirmed, respectively.
    ``min_score`` and ``max_score`` are the range in which scores should be generated."""

    if discarded and confirmed:
        raise ValueError("Ballot can't be both discarded and confirmed!")

    t = debate.round.tournament

    if not debate.sides_confirmed:
        debate.sides_confirmed = True
        debate.save()

    # Create a new BallotSubmission
    bsub = BallotSubmission(submitter_type=submitter_type, debate=debate)
    if submitter_type == BallotSubmission.SUBMITTER_TABROOM:
        bsub.submitter = user
    bsub.save()

    # Create relevant scores
    result = DebateResult(bsub)

    if result.uses_speakers:
        for side in t.sides:
            speakers = list(debate.get_team(side).speakers)  # fix order
            for i in range(1, t.last_substantive_position+1):
                result.set_speaker(side, i, speakers[i-1])
                result.set_ghost(side, i, False)

            if t.reply_position is not None:
                reply_speaker = random.randint(0, t.last_substantive_position-2) if reply_random else 0
                result.set_speaker(side, t.reply_position, speakers[reply_speaker])
                result.set_ghost(side, t.reply_position, False)

    if result.is_voting:
        for scoresheet in result.scoresheets.values():
            fill_scoresheet_randomly(scoresheet, t)
    else:
        fill_scoresheet_randomly(result.scoresheet, t)

    assert result.is_valid()
    result.save()

    # Pick a motion
    motions = debate.round.motion_set.all()
    if motions:
        num_motions = 3 if motions.count() > 3 else motions.count()
        sample = random.sample(list(motions), k=num_motions)
        motion = sample[0]
        bsub.motion = motion

        if t.pref('motion_vetoes_enabled') and len(sample) == len(t.sides) + 1:
            for i, side in enumerate(t.sides, 1):
                dt = debate.get_dt(side)
                dt.debateteammotionpreference_set.create(
                    motion=sample[i],
                    preference=3,
                    ballot_submission=bsub,
                )

    bsub.discarded = discarded
    bsub.confirmed = confirmed

    bsub.save()

    # Update result status (only takes into account marginal effect, does not "fix")
    if confirmed:
        debate.result_status = Debate.STATUS_CONFIRMED
    elif not discarded and debate.result_status != Debate.STATUS_CONFIRMED:
        debate.result_status = Debate.STATUS_DRAFT
    debate.save()

    if t.pref('teams_in_debate') == 'two':
        logger.info("%(debate)s won by %(team)s on %(motion)s", {
            'debate': debate.matchup,
            'team': result.winning_side(),
            'motion': bsub.motion and bsub.motion.reference or "<No motion>",
        })
    elif t.pref('teams_in_debate') == 'bp':
        if result.uses_declared_winners:
            logger.info("%(debate)s: %(advancing)s on %(motion)s", {
                'debate': debate.matchup,
                'advancing': ", ".join(result.get_winner()),
                'motion': bsub.motion and bsub.motion.reference or "<No motion>",
            })
        else:
            logger.info("%(debate)s: %(ranked)s on %(motion)s", {
                'debate': debate.matchup,
                'ranked': ", ".join(result.scoresheet.ranked_sides()),
                'motion': bsub.motion and bsub.motion.reference or "<No motion>",
            })

    return result
