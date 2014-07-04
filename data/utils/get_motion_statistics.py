"""Prints all motion statistics for a tournament.
Written for Australs 2014. Probably doesn't have much of another purpose.
Very inefficient because it doesn't use extra()."""

import header
import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for round in m.Round.objects.order_by('seq'):
    total_aff_vetos = m.DebateTeamMotionPreference.objects.filter(
            motion__round=round,
            debate_team__position=m.DebateTeam.POSITION_AFFIRMATIVE,
            preference=3, ballot_submission__confirmed=True).count()
    total_neg_vetos = m.DebateTeamMotionPreference.objects.filter(
            motion__round=round,
            debate_team__position=m.DebateTeam.POSITION_NEGATIVE,
            preference=3, ballot_submission__confirmed=True).count()
    total_debates = m.Debate.objects.filter(round=round).count()
    print "Round {seq}, {all} debates, {aff} aff vetos, {neg} neg vetos".format(seq=round.seq, all=total_debates, aff=total_aff_vetos, neg=total_neg_vetos)

    for motion in m.Motion.objects.filter(round=round).order_by('seq'):
        aff_vetos = m.DebateTeamMotionPreference.objects.filter(
                motion__round=round,
                debate_team__position=m.DebateTeam.POSITION_AFFIRMATIVE,
                preference=3, motion=motion,
                ballot_submission__confirmed=True).count()
        neg_vetos = m.DebateTeamMotionPreference.objects.filter(
                motion__round=round,
                debate_team__position=m.DebateTeam.POSITION_NEGATIVE,
                preference=3, motion=motion,
                ballot_submission__confirmed=True).count()
        aff_vetos_percent = float(aff_vetos) / float(total_aff_vetos)
        neg_vetos_percent = float(neg_vetos) / float(total_neg_vetos)

        ballots = m.BallotSubmission.objects.filter(confirmed=True, motion=motion)
        chosen_in = ballots.count()
        chosen_in_percent = float(chosen_in) / float(total_debates)
        aff_wins = sum(ballot.ballot_set.aff_win for ballot in ballots)
        aff_wins_percent = float(aff_wins) / float(chosen_in)
        neg_wins = sum(ballot.ballot_set.neg_win for ballot in ballots)
        neg_wins_percent = float(neg_wins) / float(chosen_in)

        print ("  {motion:<38}   av {affveto:>2d} {affvetopc:>6.1%}   nv {negveto:>2d} {negvetopc:>6.1%}    " + \
            "c {chosen:>2d} {chosenpc:>6.1%}    aw {affwin:>2d} {affwinpc:>6.1%}   nw {negwin:>2d} {negwinpc:>6.1%}").format(
            motion=motion.reference, affveto=aff_vetos, negveto=neg_vetos,
            affvetopc=aff_vetos_percent, negvetopc=neg_vetos_percent,
            chosen=chosen_in, chosenpc = chosen_in_percent,
            affwin=aff_wins, negwin=neg_wins,
            affwinpc=aff_wins_percent, negwinpc = neg_wins_percent)
