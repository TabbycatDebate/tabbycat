from django.db import models
from draw.models import DebateTeam
from results.models import TeamScore


class MotionManager(models.Manager):
    def statistics(self, round):
        #from scipy.stats import chisquare

        motions = self.select_related('round').filter(
            round__seq__lte=round.seq,
            round__tournament=round.tournament)

        winners = TeamScore.objects.filter(
            win=True,
            ballot_submission__confirmed=True,
            ballot_submission__debate__round__tournament=round.tournament,
            ballot_submission__debate__round__seq__lte=
            round.seq).select_related('debate_team__position',
                                      'ballot_submission__motion')

        wins = dict()
        for pos, _ in DebateTeam.POSITION_CHOICES:
            wins[pos] = dict.fromkeys(motions, 0)
        for winner in winners:
            if winner.ballot_submission.motion:
                wins[winner.debate_team.position][winner.ballot_submission.motion] += 1

        for motion in motions:
            motion.aff_wins = wins[DebateTeam.POSITION_AFFIRMATIVE][motion]
            motion.neg_wins = wins[DebateTeam.POSITION_NEGATIVE][motion]
            motion.chosen_in = sum(wins[pos][motion]
                                   for pos, _ in DebateTeam.POSITION_CHOICES)

            # motion.c1, motion.p_value = chisquare([motion.aff_wins, motion.neg_wins], f_exp=[motion.chosen_in / 2, motion.chosen_in / 2])
            # # Culling out the NaN errors
            # try:
            #     test = int(motion.c1)
            # except ValueError:
            #     motion.c1, motion.p_value = None, None
            # TODO: temporarily disabled
            motion.c1, motion.p_value = None, None

        if round.tournament.pref('motion_vetoes_enabled'):
            veto_objs = DebateTeamMotionPreference.objects.filter(
                preference=3,
                ballot_submission__confirmed=True,
                ballot_submission__debate__round__tournament=round.tournament,
                ballot_submission__debate__round__seq__lte=
                round.seq).select_related('debate_team__position',
                                          'ballot_submission__motion')
            vetoes = dict()
            for pos, _ in DebateTeam.POSITION_CHOICES:
                vetoes[pos] = dict.fromkeys(motions, 0)
            for veto in veto_objs:
                vetoes[veto.debate_team.position][veto.motion] += 1

            for motion in motions:
                motion.aff_vetoes = vetoes[DebateTeam.POSITION_AFFIRMATIVE][
                    motion]
                motion.neg_vetoes = vetoes[DebateTeam.POSITION_NEGATIVE][
                    motion]

        return motions


class Motion(models.Model):
    """Represents a single motion (not a set of motions)."""

    seq = models.IntegerField(
        help_text="The order in which motions are displayed")
    text = models.CharField(
        max_length=500,
        help_text=
        "The motion itself, e.g., \"This House would straighten all bananas\"")
    reference = models.CharField(
        max_length=100,
        help_text="Shortcode for the motion, e.g., \"Bananas\"")
    flagged = models.BooleanField(
        default=False,
        help_text=
        "For WADL: Allows for particular motions to be flagged as contentious")
    round = models.ForeignKey('tournaments.Round')
    objects = MotionManager()
    divisions = models.ManyToManyField('tournaments.Division', blank=True)

    class Meta:
        ordering = ['seq', ]

    def __str__(self):
        return self.text


class DebateTeamMotionPreference(models.Model):
    """Represents a motion preference submitted by a debate team."""
    debate_team = models.ForeignKey('draw.DebateTeam')
    motion = models.ForeignKey(Motion, db_index=True)
    preference = models.IntegerField(db_index=True)
    ballot_submission = models.ForeignKey('results.BallotSubmission')

    class Meta:
        unique_together = [('debate_team', 'preference', 'ballot_submission')]
