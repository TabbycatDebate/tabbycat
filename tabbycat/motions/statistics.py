import itertools
import numpy

from decimal import Decimal, getcontext

from django.db.models import Avg, Count, Q
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

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

        for motion in self.prelim_motions:
            motion.χ2_label, motion.χ2_info = self._annotate_χsquared(motion.ndebates, motion.averages)

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

    def _annotate_χsquared(self, ndebates, averages):
        """ motion_chi() adapted from code provided by Sella Nevo """

        averages_list = [a[1] for a in averages] # Eg [ 2, 1, 1, 0]
        T, P = self.motion_chi(ndebates, averages_list)

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

    def motion_chi(self, N, averages):
        # Calculates the chi-squared score of a motion.
        # N is the number of rooms
        # averages is the average number of points OG, OO, CG and CO received

        assert len(averages) == 4
        EPSILON = 0.0000001
        assert abs(sum(averages) - 6) < EPSILON

        # Remove CO (Since can be inferred from previous teams)
        # And convert to array
        averages = averages[:3]

        X = numpy.matrix(averages)
        # As opposed to Shengwu's proposition, I create a generic covariance matrix
        # for placings. Though this might not actually be the covariance (For this
        # round or in general), I think that it is more accurate than estimating it
        # according to the round (Which might give a singular covariance matrix or
        # just have too large of a statistical error)
        V = self.create_general_places_covariance()
        # (Also, for some reason linalg.inv sometimes gives wrong results, but it
        # works for this matrix)
        V_inv = numpy.linalg.inv(V)

        mu = numpy.matrix([1.5, 1.5, 1.5])

        z = float(N * (X-mu) * V_inv * numpy.transpose(X - mu))
        DEG_OF_FREEDOM = 3
        pvalue = self.chisqr(DEG_OF_FREEDOM, z)
        # print('Bits:', math.log(pvalue, 0.5))
        return z, pvalue

    @staticmethod
    def create_general_places_covariance():
        possible_results = [numpy.matrix(x[:3]) for x in itertools.permutations(range(4))]
        mu = numpy.matrix([1.5,1.5,1.5])

        V = sum(numpy.transpose(list(possible_results)[i]) * possible_results[i] - numpy.transpose(mu) * mu for i in range(len(possible_results)))
        V = V / float(len(possible_results))
        return V

    @staticmethod
    def chisqr(dof, cv):

        def igf(s, z):
            if z < Decimal('0'):
                return Decimal('0')

            sc = Decimal('1') / s
            sc *= getcontext().power(z,s)
            sc *= Decimal(-z).exp()

            sum_v = Decimal('1')
            nom = Decimal('1')
            denom = Decimal('1')

            for i in range(0,200):
                nom *= z
                s+=Decimal('1')
                denom *= s

                sum_v += (nom / denom)

            return sum_v * sc

        def mygamma(z):
            """
               The constant SQRT2PI is defined as sqrt(2.0 * PI);
               For speed the constant is already defined in decimal
               form.  However, if you wish to ensure that you achieve
               maximum precision on your own machine, you can calculate
               it yourself using (sqrt(atan(1.0) * 8.0))
           """
            #const long double SQRT2PI = sqrtl(atanl(1.0) * 8.0);
            SQRT2PI = Decimal('2.5066282746310005024157652848110452530069867406099383')
            A = Decimal('15')

            f = Decimal('1')
            sum_v = SQRT2PI

            sc = getcontext().power(z+A,z+Decimal('0.5'))

            sc *= Decimal(Decimal('-1') * (z+A)).exp()

            sc /= z

            for k in range(1,15):
                z+=Decimal('1')
                ck = getcontext().power(A - Decimal(k) , Decimal(k) - Decimal('0.5'))
                ck *= Decimal(A - Decimal(k)).exp()
                ck /= f

                sum_v += (ck / z)

                f *= (Decimal('-1') * k)

            return sum_v * sc

        # Convert to decimal
        dof = Decimal(dof)
        cv = Decimal(cv)

        if cv < Decimal('0') or dof < Decimal('1'):
            return Decimal('0')

        k = dof * Decimal('0.5')
        x = cv * Decimal('0.5')

        if dof == Decimal('2'):
            print(Decimal(Decimal('-1') * x).exp())
            return

        pvalue = igf(k,x)

        if pvalue.is_nan() or pvalue.is_infinite() or pvalue <= 1e-8:
            return 1e-14

        pvalue /= mygamma(k)

        return float(Decimal('1') - pvalue)

    CRITICAL_VALUES = [
        # (maximum value, level of significance as percentage string, evidence strength)
        (10.826, '0.1%', ugettext_lazy("extremely strong evidence")),
        (6.635,    '1%', ugettext_lazy("strong evidence")),
        (5.412,    '2%', ugettext_lazy("moderate evidence")),
        (3.841,    '5%', ugettext_lazy("weak evidence")),
        (2.706,   '10%', ugettext_lazy("very weak evidence")),
        (0.455,   '50%', ugettext_lazy("extremely weak evidence")),
    ]
