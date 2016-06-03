"""Contains utilities that add or remove things from the database, relating
to results of debates.

These are mainly used in management commands, but in principle could be used
by a front-end interface as well."""

import random
import logging

from django.contrib.auth import get_user_model

from draw.models import Debate
from results.models import BallotSubmission
from results.result import BallotSet

logger = logging.getLogger(__name__)
User = get_user_model()


def add_ballotsets_to_round(round, **kwargs):
    """Calls add_ballotset() for every debate in the given round."""
    for debate in round.debate_set.all():
        add_ballotset(debate, **kwargs)


def add_ballotsets_to_round_partial(round, num, **kwargs):
    """Calls ``add_ballotset()`` on ``num`` randomly-chosen debates in the given round."""
    debates = random.sample(list(round.debate_set.all()), num)
    for debate in debates:
        add_ballotset(debate, **kwargs)


def delete_all_ballotsets_for_round(round):
    """Deletes all ballot sets from the given round."""
    BallotSubmission.objects.filter(debate__round=round).delete()


def delete_ballotset(debate):
    """Deletes all ballot sets from the given debate."""
    debate.ballotsubmission_set.all().delete()


def add_ballotset(debate, submitter_type, user, discarded=False, confirmed=False,
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

    last_substantive_position = debate.round.tournament.LAST_SUBSTANTIVE_POSITION
    reply_position = debate.round.tournament.REPLY_POSITION

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
    for adj in debate.adjudicators.list:
        rr[adj] = gen_results()

    # Create relevant scores
    bset = BallotSet(bsub)

    for side in ('aff', 'neg'):
        speakers = getattr(debate, '%s_team' % side).speakers
        for i in range(1, last_substantive_position+1):
            bset.set_speaker(team=side, position=i, speaker=speakers[i - 1])

        reply_speaker = random.randint(0, last_substantive_position-1) if reply_random else 0
        bset.set_speaker(team=side, position=reply_position, speaker=speakers[reply_speaker])

        for adj in debate.adjudicators.list:
            for pos in debate.round.tournament.POSITIONS:
                bset.set_score(adj, side, pos, rr[adj][side][pos-1])

    # Pick a motion
    motions = debate.round.motion_set.all()
    if motions:
        motion = random.choice(motions)
        bset.motion = motion

    bset.discarded = discarded
    bset.confirmed = confirmed

    bset.save()

    # Update result status (only takes into account marginal effect, does not "fix")
    if confirmed:
        debate.result_status = Debate.STATUS_CONFIRMED
    elif not discarded and debate.result_status != Debate.STATUS_CONFIRMED:
        debate.result_status = Debate.STATUS_DRAFT
    debate.save()

    logger.info("{debate} won by {team} on {motion}".format(
        debate=debate.matchup, team=bset.aff_win and "affirmative" or "negative",
        motion=bset.motion and bset.motion.reference or "<No motion>"))

    return bset
