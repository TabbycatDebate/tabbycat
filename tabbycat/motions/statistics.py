import itertools

from django.db.models import Avg, CharField, Count, F, Q, Value
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from draw.types import DebateSide
from tournaments.models import Round

from .models import Motion, RoundMotion


def _annotate_annotations(dict_motions, queryset, fields):
    for item in queryset:
        for field in fields:
            setattr(dict_motions[item.pk], field, getattr(item, field))


class MotionTwoTeamStatsCalculator:

    def __init__(self, tournament):
        self.tournament = tournament
        self.by_motion = tournament.pref('enable_motions')
        self.include_vetoes = tournament.pref('motion_vetoes_enabled')

        self._prefetch_motions()

        for pk, motion in self.dict_motions.items():
            self._annotate_percentages(motion)
            motion.χ2_label, motion.χ2_info = self._annotate_χsquared(motion.s0_wins, motion.s1_wins)

            if self.include_vetoes:
                # vetoes are the "other way round", since an aff veto indicates it's neg-weighted
                motion.veto_χ2_label, motion.veto_χ2_info = self._annotate_χsquared(motion.s1_vetoes, motion.s0_vetoes)

        self.motions = self.dict_motions.values()

    def _prefetch_motions(self):
        motions = Motion.objects.filter(
            rounds__tournament=self.tournament,
        ).prefetch_related('rounds').annotate(
            tdebates=Count('rounds__debate'),
        ).order_by('text')

        self.dict_motions = {m.id: m for m in motions}

        # This if-else block could be simplified using **kwargs notation, but it'd be miserable to read
        motions = Motion.objects.filter(
            pk__in=self.dict_motions.keys(),
        ).annotate(nrounds=Count('rounds'), ndebates=Count('ballotsubmission', filter=Q(ballotsubmission__confirmed=True)))
        _annotate_annotations(self.dict_motions, motions, ('nrounds', 'ndebates'))

        motions = Motion.objects.filter(
            pk__in=self.dict_motions.keys(),
        ).annotate(**{'s%d_wins' % side: Count(
            'ballotsubmission__teamscore',
            filter=Q(
                ballotsubmission__confirmed=True,
                ballotsubmission__teamscore__debate_team__side=side,
                ballotsubmission__teamscore__win=True,
            )) for side in self.tournament.sides},
        )
        _annotate_annotations(self.dict_motions, motions, ['s%d_wins' % side for side in self.tournament.sides])

        if self.include_vetoes:
            motions = Motion.objects.filter(pk__in=self.dict_motions.keys()).annotate(**{'s%d_vetoes' % side: Count(
                'debateteammotionpreference',
                filter=Q(
                    debateteammotionpreference__debate_team__side=side,
                    debateteammotionpreference__preference=3,
                    debateteammotionpreference__ballot_submission__confirmed=True,
                )) for side in self.tournament.sides})
            _annotate_annotations(self.dict_motions, motions, ['s%d_vetoes' % side for side in self.tournament.sides])

    def _annotate_percentages(self, motion):
        if motion.tdebates == 0:  # Avoid division by 0
            return

        motion.s0_win_percentage = motion.s0_wins / motion.tdebates * 100
        motion.s1_win_percentage = motion.s1_wins / motion.tdebates * 100

        if self.include_vetoes:
            motion.s0_veto_percentage = motion.s0_vetoes / motion.tdebates * 100 / 2
            motion.s1_veto_percentage = motion.s1_vetoes / motion.tdebates * 100 / 2

    CRITICAL_VALUES = [
        # (maximum value, level of significance as percentage string, evidence strength)
        (10.826, '0.1%', gettext_lazy("extremely strong evidence")),
        (6.635,    '1%', gettext_lazy("strong evidence")),
        (5.412,    '2%', gettext_lazy("moderate evidence")),
        (3.841,    '5%', gettext_lazy("weak evidence")),
        (2.706,   '10%', gettext_lazy("very weak evidence")),
        (0.455,   '50%', gettext_lazy("extremely weak evidence")),
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


class RoundMotionTwoTeamStatsCalculator(MotionTwoTeamStatsCalculator):

    def _prefetch_motions(self):
        motions = RoundMotion.objects.filter(
            round__tournament=self.tournament,
            motion__ballotsubmission__confirmed=True,
        ).annotate(
            nrounds=Count('round'),
            ndebates=Count('motion__ballotsubmission', filter=Q(
                motion__ballotsubmission__debate__round=F('round'),
                motion__ballotsubmission__confirmed=True),
            ),
        ).prefetch_related('round', 'motion').order_by('round__seq', 'seq')
        self.dict_motions = {m.id: m for m in motions}

        motions = RoundMotion.objects.filter(pk__in=self.dict_motions.keys()).annotate(tdebates=Count('round__debate'))
        _annotate_annotations(self.dict_motions, motions, ('tdebates',))

        motions = RoundMotion.objects.filter(
            pk__in=self.dict_motions.keys(),
        ).annotate(**{'s%d_wins' % side: Count(
            'motion__ballotsubmission__teamscore',
            filter=Q(
                motion__ballotsubmission__confirmed=True,
                motion__ballotsubmission__teamscore__debate_team__side=side,
                motion__ballotsubmission__teamscore__win=True,
                motion__ballotsubmission__debate__round=F('round'),
            )) for side in self.tournament.sides})
        _annotate_annotations(self.dict_motions, motions, ['s%d_wins' % side for side in self.tournament.sides])

        if self.include_vetoes:
            motions = RoundMotion.objects.filter(
                pk__in=self.dict_motions.keys(),
            ).annotate(**{'s%d_vetoes' % side: Count(
                'motion__debateteammotionpreference',
                filter=Q(
                    motion__debateteammotionpreference__debate_team__side=side,
                    motion__debateteammotionpreference__preference=3,
                    motion__debateteammotionpreference__ballot_submission__confirmed=True,
                )) for side in self.tournament.sides})
            _annotate_annotations(self.dict_motions, motions, ['s%d_vetoes' % side for side in self.tournament.sides])


class MotionBPStatsCalculator:

    def __init__(self, tournament):
        self.tournament = tournament

        self._prefetch_prelim_motions()
        self._collate_prelim_motion_annotations()
        self._prefetch_elim_motions()
        self._collate_elim_motion_annotations()
        self.motions = itertools.chain(self.prelim_motions_dict.values(), self.elim_motions_dict.values())

    def _prefetch_prelim_motions(self):
        """Constructs the database query for preliminary round motions.

        The annotations are (1) the average team points by teams in each
        position, and (2) the number of teams receiving n points from each
        position for each n = 0, 1, 2, 3.

        Assumes that motion selection is disabled, so there's only one motion
        per round. We'll implement motion selection if and when we discover that
        it's used by someone with BP."""

        self.prelim_motions = Motion.objects.filter(
            rounds__tournament=self.tournament,
            rounds__stage=Round.Stage.PRELIMINARY,
            ballotsubmission__confirmed=True,
        ).annotate(ndebates=Count('ballotsubmission', filter=Q(ballotsubmission__confirmed=True)),
            stage=Value('prelim', output_field=CharField()))
        self.prelim_motions_dict = {m.id: m for m in self.prelim_motions.all()}

        annotations = {}  # dict of keyword arguments to pass to .annotate()
        annotations.update({'s%d_average' % side: Avg(
            'ballotsubmission__teamscore__points',
            filter=Q(ballotsubmission__teamscore__debate_team__side=side, ballotsubmission__confirmed=True),
        ) for side in self.tournament.sides})

        annotations.update({'s%d_%d_count' % (side, points): Count(
            'ballotsubmission__teamscore',
            filter=Q(
                ballotsubmission__confirmed=True,
                ballotsubmission__teamscore__debate_team__side=side,
                ballotsubmission__teamscore__points=points,
            )) for side in self.tournament.sides for points in range(4)})

        motions = Motion.objects.filter(pk__in=self.prelim_motions_dict.keys()).annotate(**annotations)
        _annotate_annotations(self.prelim_motions_dict, motions, annotations.keys())

    def _collate_prelim_motion_annotations(self):
        """Collect annotations (which will be attributes) and convert them to
        dictionaries to allow for easy iteration in the template."""

        for motion in self.prelim_motions_dict.values():
            motion.averages = []
            motion.counts_by_side = []
            motion.counts_by_half = {'top': 0, 'bottom': 0}
            motion.counts_by_bench = {'gov': 0, 'opp': 0}

            for side in self.tournament.sides:
                average = getattr(motion, 's%d_average' % side)
                if average is None:
                    continue
                motion.averages.append((side, average, average / 6 * 100))
                counts = []
                for points in [3, 2, 1, 0]:
                    count = getattr(motion, 's%d_%d_count' % (side, points))
                    percentage = count / motion.ndebates * 100 if motion.ndebates > 0 else 0
                    counts.append((points, count, percentage))
                motion.counts_by_side.append((side, counts))

                if side == DebateSide.OG or side == DebateSide.OO:
                    motion.counts_by_half['top'] += (average / 2)
                else:
                    motion.counts_by_half['bottom'] += (average / 2)

                if side == DebateSide.OG or side == DebateSide.CG:
                    motion.counts_by_bench['gov'] += (average / 2)
                else:
                    motion.counts_by_bench['opp'] += (average / 2)

    def _prefetch_elim_motions(self):
        """Constructs the database query for elimination round motions.

        Elimination rounds in BP are advancing/eliminated, so this just collates
        information on who advanced and who did not.

        Assumes that motion selection is disabled, so there's only one motion
        per round. We'll implement motion selection if and when we discover that
        it's used by someone with BP."""

        self.elim_motions = Motion.objects.filter(
            rounds__tournament=self.tournament,
            rounds__stage=Round.Stage.ELIMINATION,
            ballotsubmission__confirmed=True,
        ).annotate(ndebates=Count('ballotsubmission', filter=Q(ballotsubmission__confirmed=True)),
            stage=Value('elim', output_field=CharField()))
        self.elim_motions_dict = {m.id: m for m in self.elim_motions.all()}

        annotations = {}  # dict of keyword arguments to pass to .annotate()
        annotations.update({'s%d_%s' % (side, status): Count(
            'ballotsubmission__teamscore',
            filter=Q(
                ballotsubmission__confirmed=True,
                ballotsubmission__teamscore__debate_team__side=side,
                ballotsubmission__teamscore__win=value,
            )) for side in self.tournament.sides for (status, value) in [("advancing", True), ("eliminated", False)]
        })
        motions = Motion.objects.filter(pk__in=self.elim_motions_dict.keys()).annotate(**annotations)
        _annotate_annotations(self.elim_motions_dict, motions, annotations.keys())

    def _collate_elim_motion_annotations(self):
        """Collect annotations (which will be attributes) and convert them to
        dictionaries to allow for easy iteration in the template."""

        for motion in self.elim_motions_dict.values():
            motion.counts_by_side = []

            for side in self.tournament.sides:
                advancing = getattr(motion, 's%d_advancing' % side)
                advancing_pc = advancing / motion.ndebates * 100 if motion.ndebates > 0 else 0
                eliminated = getattr(motion, 's%d_eliminated' % side)
                eliminated_pc = eliminated / motion.ndebates * 100 if motion.ndebates > 0 else 0
                motion.counts_by_side.append((side, advancing, advancing_pc, eliminated, eliminated_pc))


class RoundMotionBPStatsCalculator(MotionBPStatsCalculator):

    def _prefetch_prelim_motions(self):
        """Constructs the database query for preliminary round motions.

        The annotations are (1) the average team points by teams in each
        position, and (2) the number of teams receiving n points from each
        position for each n = 0, 1, 2, 3."""

        self.prelim_motions = RoundMotion.objects.filter(
            round__tournament=self.tournament,
            round__stage=Round.Stage.PRELIMINARY,
            motion__ballotsubmission__confirmed=True,
        ).order_by('round__seq', 'seq').select_related('motion', 'round').annotate(
            ndebates=Count('motion__ballotsubmission', filter=Q(
                motion__ballotsubmission__confirmed=True,
                motion__ballotsubmission__debate__round=F('round'))),
            stage=Value('prelim', output_field=CharField()))
        self.prelim_motions_dict = {m.id: m for m in self.prelim_motions}

        annotations = {}  # dict of keyword arguments to pass to .annotate()
        annotations.update({'s%d_average' % side: Avg(
            'motion__ballotsubmission__teamscore__points',
            filter=Q(
                motion__ballotsubmission__confirmed=True,
                motion__ballotsubmission__debate__round=F('round'),
                motion__ballotsubmission__teamscore__debate_team__side=side,
            )) for side in self.tournament.sides})

        annotations.update({'s%d_%d_count' % (side, points): Count(
            'motion__ballotsubmission__teamscore',
            filter=Q(
                motion__ballotsubmission__confirmed=True,
                motion__ballotsubmission__debate__round=F('round'),
                motion__ballotsubmission__teamscore__debate_team__side=side,
                motion__ballotsubmission__teamscore__points=points,
            )) for side in self.tournament.sides for points in range(4)})

        motions = RoundMotion.objects.filter(pk__in=self.prelim_motions_dict.keys()).annotate(**annotations)
        _annotate_annotations(self.prelim_motions_dict, motions, annotations.keys())

    def _prefetch_elim_motions(self):
        """Constructs the database query for elimination round motions.

        Elimination rounds in BP are advancing/eliminated, so this just collates
        information on who advanced and who did not."""

        self.elim_motions = RoundMotion.objects.filter(
            round__tournament=self.tournament,
            round__stage=Round.Stage.ELIMINATION,
            motion__ballotsubmission__confirmed=True,
        ).order_by('round__seq', 'seq').select_related('motion', 'round').annotate(
            ndebates=Count('motion__ballotsubmission', filter=Q(
                motion__ballotsubmission__confirmed=True,
                motion__ballotsubmission__debate__round=F('round'))),
            stage=Value('elim', output_field=CharField()))
        self.elim_motions_dict = {m.id: m for m in self.elim_motions}

        annotations = {}  # dict of keyword arguments to pass to .annotate()
        annotations.update({'s%d_%s' % (side, status): Count(
            'motion__ballotsubmission__teamscore',
            filter=Q(
                motion__ballotsubmission__confirmed=True,
                motion__ballotsubmission__debate__round=F('round'),
                motion__ballotsubmission__teamscore__debate_team__side=side,
                motion__ballotsubmission__teamscore__win=value,
            )) for side in self.tournament.sides for (status, value) in [("advancing", True), ("eliminated", False)]
        })
        motions = RoundMotion.objects.filter(pk__in=self.elim_motions_dict.keys()).annotate(**annotations)
        _annotate_annotations(self.elim_motions_dict, motions, annotations.keys())
