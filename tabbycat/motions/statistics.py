from draw.models import DebateTeam
from results.models import TeamScore

from .models import DebateTeamMotionPreference, Motion
# From scipy.stats import chisquare


def statistics(tournament, rounds):

    motions = Motion.objects.select_related('round').filter(
        round__in=rounds)

    winners = TeamScore.objects.filter(
        win=True,
        ballot_submission__confirmed=True,
        ballot_submission__debate__round__in=rounds).select_related(
        'debate_team', 'ballot_submission__motion')

    wins = dict()
    for pos, _ in DebateTeam.SIDE_CHOICES:
        wins[pos] = dict.fromkeys(motions, 0)
    for winner in winners:
        if winner.ballot_submission.motion:
            wins[winner.debate_team.side][winner.ballot_submission.motion] += 1

    for motion in motions:
        motion.aff_wins = wins[DebateTeam.SIDE_AFF][motion]
        motion.neg_wins = wins[DebateTeam.SIDE_NEG][motion]
        motion.chosen_in = motion.aff_wins + motion.neg_wins

        """
        motion.c1, motion.p_value = chisquare([motion.aff_wins, motion.neg_wins], f_exp=[motion.chosen_in / 2, motion.chosen_in / 2])
        # Culling out the NaN errors
        try:
            test = int(motion.c1)
        except ValueError:
            motion.c1, motion.p_value = None, None
        TODO: temporarily disabled
        """

        motion.c1, motion.p_value = None, None

    if tournament.pref('motion_vetoes_enabled'):
        veto_objs = DebateTeamMotionPreference.objects.filter(
            preference=3,
            ballot_submission__confirmed=True,
            ballot_submission__debate__round__in=rounds).select_related(
            'debate_team', 'ballot_submission__motion')
        vetoes = dict()
        for pos, _ in DebateTeam.SIDE_CHOICES:
            vetoes[pos] = dict.fromkeys(motions, 0)
        for veto in veto_objs:
            vetoes[veto.debate_team.side][veto.motion] += 1

        for motion in motions:
            motion.aff_vetoes = vetoes[DebateTeam.SIDE_AFF][motion]
            motion.neg_vetoes = vetoes[DebateTeam.SIDE_NEG][motion]

    return motions
