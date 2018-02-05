import itertools

from django.db.models import Avg, Count, Q
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.utils.functional import cached_property

from motions.models import Motion
from tournaments.models import Round


def MotionStatistics(tournament, *args, **kwargs):  # noqa: N802
    if tournament.pref('teams_in_debate') == 'two':
        return MotionTwoTeamStatsCalculator(tournament, *args, **kwargs)
    else:
        return MotionBPStatsCalculator(tournament, *args, **kwargs)


class MotionTwoTeamStatsCalculator:

    def __init__(self, tournament):
        self.tournament = tournament
        self.by_motion = tournament.pref('enable_motions')
        self.include_vetoes = self.by_motion and tournament.pref('motion_vetoes_enabled')

        self._prefetch_motions()
        self.ndebates_by_round = {r: r.ndebates for r in
                tournament.round_set.annotate(ndebates=Count('debate'))}

        for motion in self.motions:
            self._annotate_percentages(motion)
            motion.χ2_label, motion.χ2_info = self._annotate_χsquared(motion.aff_wins, motion.neg_wins)

            if self.include_vetoes:
                # vetoes are the "other way round", since an aff veto indicates it's neg-weighted
                motion.veto_χ2_label, motion.veto_χ2_info = self._annotate_χsquared(motion.neg_vetoes, motion.aff_vetoes)

    def _prefetch_motions(self):

        self.motions = Motion.objects.filter(round__tournament=self.tournament).order_by(
            'round__seq').select_related('round')
        annotations = {}  # dict of keyword arguments to pass to .annotate()

        # This if-else block could be simplified using **kwargs notation, but it'd be miserable to read
        if self.by_motion:
            self.motions = self.motions.filter(ballotsubmission__confirmed=True)
            annotations['ndebates'] = Count('ballotsubmission', distinct=True)
            annotations.update({'%s_wins' % side: Count(
                'ballotsubmission__teamscore',
                filter=Q(
                    ballotsubmission__teamscore__debate_team__side=side,
                    ballotsubmission__teamscore__win=True,
                ), distinct=True) for side in self.tournament.sides})

        else:
            self.motions = self.motions.filter(round__debate__ballotsubmission__confirmed=True)
            annotations['ndebates'] = Count('round__debate__ballotsubmission', distinct=True)
            annotations.update({'%s_wins' % side: Count(
                'round__debate__ballotsubmission__teamscore',
                filter=Q(
                    round__debate__ballotsubmission__teamscore__debate_team__side=side,
                    round__debate__ballotsubmission__teamscore__win=True,
                ), distinct=True) for side in self.tournament.sides})

        if self.include_vetoes:
            annotations.update({'%s_vetoes' % side: Count(
                'debateteammotionpreference',
                filter=Q(
                    debateteammotionpreference__debate_team__side=side,
                    debateteammotionpreference__preference=3,
                    debateteammotionpreference__ballot_submission__confirmed=True,
                ), distinct=True) for side in self.tournament.sides})

        self.motions = self.motions.annotate(**annotations)

    def _annotate_percentages(self, motion):
        ndebates_in_round = self.ndebates_by_round[motion.round]

        if ndebates_in_round == 0:
            return

        motion.aff_win_percentage = motion.aff_wins / ndebates_in_round * 100
        motion.neg_win_percentage = motion.neg_wins / ndebates_in_round * 100

        if self.include_vetoes:
            motion.aff_veto_percentage = motion.aff_vetoes / ndebates_in_round * 100 / 2
            motion.neg_veto_percentage = motion.neg_vetoes / ndebates_in_round * 100 / 2

    CRITICAL_VALUES = [
        # (maximum value, level of significance as percentage string, evidence strength)
        (10.826, '0.1%', ugettext_lazy("extremely strong evidence")),
        (6.635,    '1%', ugettext_lazy("strong evidence")),
        (5.412,    '2%', ugettext_lazy("moderate evidence")),
        (3.841,    '5%', ugettext_lazy("weak evidence")),
        (2.706,   '10%', ugettext_lazy("very weak evidence")),
        (0.455,   '50%', ugettext_lazy("extremely weak evidence")),
    ]

    def _annotate_χsquared(self, affs, negs):  # noqa: N802
        """Annotates motions with information from the χ² test.
        Test and confidence levels contributed by Viran Weerasekera.
        The χ² statistic is computed as follows:

                (A - μ)²   (N - μ)²   (A² + N²)
            T = -------- + -------- = --------- - n
                   μ          μ           μ

        where A is the number of debates won by affirmative teams,
        N is the number of debates won by negative teams,
        n = (A + N) is the total number of debates, and
        μ = (A + N)/2 is the expected number of debates under the null hypothesis.

        T is then distributed according to a χ² distribution with one degree of freedom.
        """

        n = affs + negs

        if n < 10:
            label = _("balance inconclusive")
            info = _("too few debates to get a meaningful statistic")
            return label, info

        μ = n / 2  # noqa: N806
        T = (affs ** 2 + negs ** 2) / μ - n  # noqa: N806

        for critical, level_str, evidence_str in self.CRITICAL_VALUES:
            if T > critical:
                label = _("imbalanced at %(level)s level") % {'level': level_str}
                info = _("χ² statistic is %(chisq).3f, providing %(evidence)s to "
                    "suggest that this motion was imbalanced — at a %(level)s level of "
                    "significance.") % {'chisq': T, 'level': level_str, 'evidence': evidence_str}
                break
        else:
            label = _("probably balanced")
            info = _("χ² statistic is %(chisq).3f, providing insufficient evidence "
                "to suggest that this motion was imbalanced at any level of significance.") % {'chisq': T}

        return label, info


class MotionBPStatsCalculator:

    def __init__(self, tournament):
        self.tournament = tournament

        self._prefetch_prelim_motions()
        self._collate_prelim_motion_annotations()
        self._prefetch_elim_motions()
        self._collate_elim_motion_annotations()
        self.motions = itertools.chain(self.prelim_motions, self.elim_motions)

    def _prefetch_prelim_motions(self):
        """Constructs the database query for preliminary round motions.

        The annotations are (1) the average team points by teams in each
        position, and (2) the number of teams receiving n points from each
        position for each n = 0, 1, 2, 3.

        Assumes that motion selection is disabled, so there's only one motion
        per round. We'll implement motion selection if and when we discover that
        it's used by someone with BP."""

        self.prelim_motions = Motion.objects.filter(
            round__tournament=self.tournament,
            round__stage=Round.STAGE_PRELIMINARY,
            round__debate__ballotsubmission__confirmed=True,
        ).order_by('round__seq').select_related('round')

        annotations = {}  # dict of keyword arguments to pass to .annotate()
        annotations['ndebates'] = Count('round__debate__ballotsubmission', distinct=True)

        annotations.update({'%s_average' % side: Avg(
            'round__debate__ballotsubmission__teamscore__points',
            filter=Q(round__debate__ballotsubmission__teamscore__debate_team__side=side),
            distinct=True,
        ) for side in self.tournament.sides})

        annotations.update({'%s_%d_count' % (side, points): Count(
            'round__debate__ballotsubmission__teamscore',
            filter=Q(
                round__debate__ballotsubmission__teamscore__debate_team__side=side,
                round__debate__ballotsubmission__teamscore__points=points
            ), distinct=True
        ) for side in self.tournament.sides for points in range(4)})

        self.prelim_motions = self.prelim_motions.annotate(**annotations)

    def _collate_prelim_motion_annotations(self):
        """Collect annotations (which will be attributes) and convert them to
        dictionaries to allow for easy iteration in the template."""

        for motion in self.prelim_motions:
            motion.averages = []
            motion.counts_by_side = []

            for side in self.tournament.sides:
                average = getattr(motion, '%s_average' % side)
                motion.averages.append((side, average, average / 6 * 100))
                counts = []
                for points in [3, 2, 1, 0]:
                    count = getattr(motion, '%s_%d_count' % (side, points))
                    percentage = count / motion.ndebates * 100 if motion.ndebates > 0 else 0
                    counts.append((points, count, percentage))
                motion.counts_by_side.append((side, counts))

    def _prefetch_elim_motions(self):
        """Constructs the database query for elimination round motions.

        Elimination rounds in BP are advancing/eliminated, so this just collates
        information on who advanced and who did not.

        Assumes that motion selection is disabled, so there's only one motion
        per round. We'll implement motion selection if and when we discover that
        it's used by someone with BP."""

        self.elim_motions = Motion.objects.filter(
            round__tournament=self.tournament,
            round__stage=Round.STAGE_ELIMINATION,
        ).order_by('round__seq').select_related('round')

        annotations = {}  # dict of keyword arguments to pass to .annotate()
        annotations['ndebates'] = Count('round__debate__ballotsubmission', distinct=True)

        annotations.update({'%s_%s' % (side, status): Count(
            'round__debate__ballotsubmission__teamscore',
            filter=Q(
                round__debate__ballotsubmission__teamscore__debate_team__side=side,
                round__debate__ballotsubmission__teamscore__win=value,
            ), distinct=True)
            for side in self.tournament.sides
            for (status, value) in [("advancing", True), ("eliminated", False)]
        })

        self.elim_motions = self.elim_motions.annotate(**annotations)

    def _collate_elim_motion_annotations(self):
        """Collect annotations (which will be attributes) and convert them to
        dictionaries to allow for easy iteration in the template."""

        for motion in self.elim_motions:
            motion.counts_by_side = []

            for side in self.tournament.sides:
                advancing = getattr(motion, '%s_advancing' % side)
                advancing_pc = advancing / motion.ndebates * 100 if motion.ndebates > 0 else 0
                eliminated = getattr(motion, '%s_eliminated' % side)
                eliminated_pc = eliminated / motion.ndebates * 100 if motion.ndebates > 0 else 0
                motion.counts_by_side.append((side, advancing, advancing_pc, eliminated, eliminated_pc))


class MotionStats:

    def __init__(self, motion, t, results, all_vetoes=None):
        self.motion = motion
        self.round = motion.round # Needed for regroup
        self.sides = t.sides

        results_data_for_round = [r for r in results if r.ballot_submission.debate.round == self.round]
        if t.pref('enable_motions'):
            results_data_for_motion = [r for r in results_data_for_round if r.ballot_submission.motion == motion]
        else:
            results_data_for_motion = results_data_for_round

        if all_vetoes and len(all_vetoes) > 0:
            vetoes_data = [v for v in all_vetoes if v.motion == motion]

        if t.pref('teams_in_debate') == 'two':
            self.isBP = False
            self.round_rooms = len(results_data_for_round) // 2
            self.debate_rooms = len(results_data_for_motion) // 2
        else:
            self.isBP = True
            self.round_rooms = len(results_data_for_round) // 4
            self.debate_rooms = len(results_data_for_motion) // 4

        self.placings = self.gather_placings(self.points_dict(), results_data_for_motion)
        self.result_balance = self.determine_balance()

        if all_vetoes and len(all_vetoes) > 0:
            self.vetoes = self.gather_vetoes(self.points_dict(), vetoes_data)
            self.veto_balance = self.determine_balance(True)
        else:
            self.vetoes = False
            self.veto_balance = False

    def points_dict(self):
        if self.isBP:
            return dict((s, {3: 0, 2: 0, 1: 0, 0: 0}) for s in self.sides)
        else:
            return dict((s, {1: 0, 0: 0}) for s in self.sides)

    # Calculate points per position and debate
    def gather_placings(self, placings, results_data):
        for result in results_data:
            if result.points is not None: # Some finals rounds etc wont have points
                placings[result.debate_team.side][result.points] += 1
            elif result.win is True: # Out rounds
                placings[result.debate_team.side][3] += 1
            elif result.win is False: # Out rounds
                placings[result.debate_team.side][0] += 1

        return placings

    # Calculate points per position and debate
    def gather_vetoes(self, vetoes, vetoes_data):
        for veto in vetoes_data:
            vetoes[veto.debate_team.side][1] += 1
        return vetoes

    def determine_balance(self, for_vetoes=False):
        if self.debate_rooms < 10: # Too few wins/vetoes to calculate
            return 'balance inconclusive', 'Too few debate to determine meaningful balance'
        elif self.isBP:
            return None
            # return self.four_team_balance(for_vetoes) # Not implemented
        else:
            return self.two_team_balance(for_vetoes)

    def two_team_balance(self, for_vetoes):
        # Test and confidence levels contributed by Viran Weerasekera
        if for_vetoes:
            # Swap keys as we assume vetos favour the opposite side
            affs = self.vetoes['neg'][1]
            negs = self.vetoes['aff'][1]
        else:
            affs = self.placings['aff'][1]
            negs = self.placings['neg'][1]

        n_2 = self.debate_rooms / 2
        aff_c_stat = pow(affs - n_2, 2) / n_2
        neg_c_stat = pow(negs - n_2, 2) / n_2
        c_stat = round(aff_c_stat + neg_c_stat, 2)

        threshold = next((ir for ir in self.BALANCES_2V2 if c_stat <= ir['critical']), None)
        info = "%s critical value; %s level of signficance" % (c_stat, threshold['freedom'])

        if affs > negs:
            return threshold['label'].replace('TEAM', 'aff'), info
        elif affs < negs:
            return threshold['label'].replace('TEAM', 'neg'), info
        else:
            return threshold['label'], info

    def four_team_balance(self):
        # For reference here we have self.placings dictionary of positions { 'og': X, 'oo': Y }
        # Within each position key there is a list of points and the total number of times that side
        # received those points; ie { 'og': {3: 9, 2: 10, 1: 5, 0: 8}
        # threshold = next((ir for ir in self.BALANCES if c_stat <= ir['critical']), None)
        # info = "%s critical value; %s level of signficance" % (c_stat, threshold['freedom'])
        # return threshold['label'], info
        raise NotImplementedError

    @cached_property
    def results_rates(self):
        return self.points_rates(self.placings)

    # Called by template
    @cached_property
    def veto_rates(self):
        return self.points_rates(self.vetoes, True)

    # For a given point figure out what % of total results it was
    def points_rates(self, data_set, vetoes=False):
        if self.round_rooms == 0 or self.debate_rooms == 0 or not data_set:
            return None

        rates_for_side = dict(self.points_dict())
        for side in self.sides:
            for points, count in data_set[side].items():
                # Measuring vetoes (per-team) not wins (per room)
                if vetoes and self.isBP:
                    denominator = self.round_rooms * 4
                elif vetoes and not self.isBP:
                    denominator = self.round_rooms * 2
                else:
                    denominator = self.round_rooms

                percentage = (data_set[side][points] / denominator) * 100
                rates_for_side[side][points] = round(percentage, 1)

        return rates_for_side

    @cached_property
    def points_average(self):
        if self.debate_rooms == 0:
            return None

        avgs_for_side = dict(self.points_dict())
        for side in self.sides:
            all_points = []
            counts = 0
            for points, count in self.placings[side].items():
                all_points.append(points * count)
                counts += count

            if counts > 0: # Avoid divide by zero
                avgs_for_side[side] = sum(all_points) / float(counts)
            else:
                avgs_for_side[side] = 1.5

        return avgs_for_side

    # Critical Values / Determination
    BALANCES_2V2 = [
        {'critical': 0.455,  'label': '50% (balanced)',             'freedom': .5},
        {'critical': 2.706,  'label': '90% likely TEAM favoured ',  'freedom': .1},
        {'critical': 3.841,  'label': '95% likely TEAM favoured',   'freedom': .05},
        {'critical': 5.412,  'label': '98% likely TEAM favoured',   'freedom': .02},
        {'critical': 6.635,  'label': '99% likely TEAM favoured',   'freedom': .01},
        # The last value is large enough to be a catch-all; ie over 99.9% confidence
        {'critical': 1000.0, 'label': '99.9% likely TEAM favoured', 'freedom': .001},
    ]

    BALANCES_BP = [

    ]
