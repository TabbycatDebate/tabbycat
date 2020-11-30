"""Standings generator for teams."""

import logging

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Avg, Count, F, FloatField, Func, PositiveIntegerField, Q, StdDev, Sum
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _

from results.models import TeamScore
from tournaments.models import Round

from .base import BaseStandingsGenerator
from .metrics import BaseMetricAnnotator, metricgetter, QuerySetMetricAnnotator, RepeatedMetricAnnotator
from .ranking import BasicRankAnnotator, RankFromInstitutionAnnotator, SubrankAnnotator

logger = logging.getLogger(__name__)


class NullIf(Func):
    """NULLIF() function in SQL. This implementation doesn't vet arguments, so
    it's a little fragile when used incorrectly - use with care."""
    function = 'NULLIF'


# ==============================================================================
# Metric annotators
# ==============================================================================

class TeamScoreQuerySetMetricAnnotator(QuerySetMetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations
    of TeamScore instances."""

    function = None  # must be set by subclasses
    field = None  # must be set by subclasses
    output_field = None

    where_value = None

    exclude_unconfirmed = True

    def get_field(self):
        """Subclasses with complicated fields override this method."""
        return 'debateteam__teamscore__' + self.field

    def get_where_field(self):
        return self.get_field()

    def get_annotation_filter(self, round=None):
        annotation_filter = Q(
            debateteam__debate__round__stage=Round.STAGE_PRELIMINARY,
        )
        if round is not None:
            annotation_filter &= Q(debateteam__debate__round__seq__lte=round.seq)
        if self.exclude_unconfirmed:
            annotation_filter &= Q(debateteam__teamscore__ballot_submission__confirmed=True)
        if self.where_value is not None:
            annotation_filter &= Q(**{self.get_where_field(): self.where_value})
        return annotation_filter

    def get_annotation(self, round=None):
        return self.function(self.get_field(), filter=self.get_annotation_filter(round), output_field=self.output_field)


class PointsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total number of points."""
    key = "points"
    name = _("points")
    abbr = _("Pts")

    function = Sum
    field = "points"
    output_field = PositiveIntegerField()

    def get_field(self):
        return F(super().get_field()) * F('debateteam__debate__round__weight')


class WinsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total number of wins."""
    key = "wins"
    name = _("wins")
    abbr = _("Wins")

    function = Count
    field = "win"
    where_value = True


class TotalSpeakerScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "speaks_sum"
    name = _("total speaker score")
    abbr = _("Spk")

    function = Sum
    field = "score"


class AverageSpeakerScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "speaks_avg"
    name = _("average total speaker score")
    abbr = _("ATSS")

    function = Avg
    field = "score"


class SpeakerScoreStandardDeviationMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "speaks_stddev"
    name = _("speaker score standard deviation")
    abbr = _("SSD")
    ascending = True

    function = StdDev
    field = "score"


class SumMarginMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for sum of margins."""
    key = "margin_sum"
    name = _("sum of margins")
    abbr = _("Marg")

    function = Sum
    field = "margin"


class AverageMarginMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for average margin."""
    key = "margin_avg"
    name = _("average margin")
    abbr = _("AWM")

    function = Avg
    field = "margin"


class AverageIndividualScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total substantive speaker score."""
    key = "speaks_ind_avg"
    name = _("average individual speaker score")
    abbr = _("AISS")

    function = Avg

    def get_field(self):
        return 'debateteam__speakerscore__score'

    def get_annotation_filter(self, round=None):
        annotation_filter = Q(
            debateteam__teamscore__ballot_submission__confirmed=True,
            debateteam__debate__round__stage=Round.STAGE_PRELIMINARY,
            debateteam__speakerscore__ghost=False,
        )
        if round is not None:
            annotation_filter &= Q(debateteam__debate__round__seq__lte=round.seq)

        # `self.tournament` is only None if `queryset.first()` was None (see
        # `get_annotated_queryset()` below), in which case the filter doesn't
        # matter because the queryset is empty anyway.
        if self.tournament is not None:
            annotation_filter &= Q(debateteam__speakerscore__position__lte=self.tournament.last_substantive_position)

        return annotation_filter

    def get_annotated_queryset(self, queryset, round=None):
        if round is not None:
            self.tournament = round.tournament
        else:
            first_team = queryset.first()
            self.tournament = first_team.tournament if first_team is not None else None

        return super().get_annotated_queryset(queryset, round)


class BaseDrawStrengthMetricAnnotator(BaseMetricAnnotator):

    opponent_annotator = None

    def annotate(self, queryset, standings, round=None):
        if not queryset.exists():
            return

        logger.info("Running opponents query for draw strength:")

        # Make a copy of teams queryset and annotate with opponents
        opponents_filter = ~Q(debateteam__debate__debateteam__team_id=F('id'))
        opponents_filter &= Q(debateteam__debate__round__stage=Round.STAGE_PRELIMINARY)
        if round is not None:
            opponents_filter &= Q(debateteam__debate__round__seq__lte=round.seq)
        opponents_annotation = ArrayAgg('debateteam__debate__debateteam__team_id',
                filter=opponents_filter)
        logger.info("Opponents annotation: %s", str(opponents_annotation))
        teams_with_opponents = queryset.all().annotate(opponent_ids=opponents_annotation)
        opponents_by_team = {team.id: team.opponent_ids for team in teams_with_opponents}

        opp_metric_queryset = self.opponent_annotator().get_annotated_queryset(
                queryset[0].tournament.team_set.all(), round)
        opp_metric_queryset_teams = {team.id: team for team in opp_metric_queryset}

        for team in queryset:
            draw_strength = 0
            for opponent_id in opponents_by_team[team.id]:
                opp_metric = getattr(opp_metric_queryset_teams[opponent_id], self.opponent_annotator.key)
                if opp_metric is not None: # opp_metric is None when no debates have happened
                    draw_strength += opp_metric
            standings.add_metric(team, self.key, draw_strength)


class DrawStrengthByWinsMetricAnnotator(BaseDrawStrengthMetricAnnotator):
    """Metric annotator for draw strength."""
    key = "draw_strength"  # keep this key for backwards compatibility
    name = _("draw strength by wins")
    abbr = _("DS")
    opponent_annotator = PointsMetricAnnotator


class DrawStrengthBySpeakerScoreMetricAnnotator(BaseDrawStrengthMetricAnnotator):
    """Metric annotator for draw strength by score."""
    key = "draw_strength_speaks"
    name = _("draw strength by total speaker score")
    abbr = _("DSS")
    opponent_annotator = TotalSpeakerScoreMetricAnnotator


class TeamPullupsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for number of times pulled up.

    How many teams the team has been pulled up (i.e., has a pullup flag in
    an associated DebateTeam object)."""

    key = "npullups"
    name = _("number of pullups before this round")
    abbr = _("PU")

    function = Count
    where_value = ['pullup']
    exclude_unconfirmed = False

    def get_field(self):
        return 'debateteam'

    def get_where_field(self):
        return 'debateteam__flags__contains'


class NumberOfAdjudicatorsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for number of votes given by a panel.

    The metric normalizes each debate to an assumed typical panel size. For
    example, if `self.adjs_per_debate == 3`, but a particular debate has a panel
    of five, then for that debate, a team winning on a 4-1 split will earn
    "2.4 votes" for that debate."""

    key = "num_adjs"
    name = _("number of adjudicators who voted for this team")
    abbr = _("Ballots")
    choice_name = _("votes/ballots carried")
    function = Sum

    def __init__(self, adjs_per_debate=3):
        self.adjs_per_debate = adjs_per_debate

    def get_field(self):
        return (Cast('debateteam__teamscore__votes_given', FloatField()) /
            NullIf('debateteam__teamscore__votes_possible', 0, output_field=FloatField()) *
            self.adjs_per_debate)

    def annotate_with_queryset(self, queryset, standings):
        # If the number of ballots carried by every team is an integer, then
        # it's probably (though not certainly) the case that there are no
        # "weird" cases causing any fractional numbers of votes due to
        # normalization. In that case, convert all metrics to integers.
        cast = int if all(t.num_adjs == int(t.num_adjs) for t in queryset) else float
        for item in queryset:
            metric = item.num_adjs
            if metric is None:
                metric = 0
            standings.add_metric(item, self.key, cast(metric))


class NumberOfFirstsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    key = "firsts"
    name = _("number of firsts")
    abbr = _("1sts")

    function = Count
    field = "points"
    where_value = 3


class NumberOfSecondsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    key = "seconds"
    name = _("number of seconds")
    abbr = _("2nds")

    function = Count
    field = "points"
    where_value = 2


class NumberOfThirdsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    key = "thirds"
    name = _("number of thirds")
    abbr = _("3rds")

    function = Count
    field = "points"
    where_value = 1


class WhoBeatWhomMetricAnnotator(RepeatedMetricAnnotator):
    """Metric annotator for who-beat-whom. Use once for every who-beat-whom in
    the precedence."""

    key_prefix = "wbw"
    name_prefix = _("Who-beat-whom")
    abbr_prefix = _("WBW")
    choice_name = _("who-beat-whom")

    def get_team_scores(self, key, equal_teams, tsi, round):
        equal_teams.remove(tsi)
        other = equal_teams[0]
        ts = TeamScore.objects.filter(
            ballot_submission__confirmed=True,
            debate_team__team=tsi.team,
            debate_team__debate__debateteam__team=other.team,
            debate_team__debate__round__stage=Round.STAGE_PRELIMINARY,
        )

        if round is not None:
            ts = ts.filter(debate_team__debate__round__seq__lte=round.seq)

        ts = ts.aggregate(Sum('points'))
        logger.info("who beat whom, %s %s vs %s %s: %s",
            tsi.team.short_name, key(tsi), other.team.short_name, key(other),
            ts["points__sum"])
        return ts

    def annotate(self, queryset, standings, round=None):
        key = metricgetter(self.keys)

        def who_beat_whom(tsi):
            equal_teams = [x for x in standings.infoview() if key(x) == key(tsi)]
            if len(equal_teams) != 2:
                return "n/a"  # fail fast if attempt to compare with an int

            ts = self.get_team_scores(key, equal_teams, tsi, round)
            return ts["points__sum"] or 0

        for tsi in standings.infoview():
            wbw = who_beat_whom(tsi)
            tsi.add_metric(self.key, wbw)


# ==============================================================================
# Standings generator
# ==============================================================================

class TeamStandingsGenerator(BaseStandingsGenerator):
    """Class for generating standings. An instance is configured with metrics
    and rankings in the constructor, and an iterable of Team objects is passed
    to its `generate()` method to generate standings. Example:

        generator = TeamStandingsGenerator(('points', 'speaker_score'), ('rank',))
        standings = generator.generate(teams)

    The generate() method returns a TeamStandings object.
    """

    TIEBREAK_FUNCTIONS = BaseStandingsGenerator.TIEBREAK_FUNCTIONS.copy()
    TIEBREAK_FUNCTIONS["shortname"] = lambda x: x.sort(key=lambda y: y.team.short_name)
    TIEBREAK_FUNCTIONS["institution"] = lambda x: x.sort(key=lambda y: y.team.institution.name)

    metric_annotator_classes = {
        "points"              : PointsMetricAnnotator,
        "wins"                : WinsMetricAnnotator,
        "speaks_sum"          : TotalSpeakerScoreMetricAnnotator,
        "speaks_avg"          : AverageSpeakerScoreMetricAnnotator,
        "speaks_ind_avg"      : AverageIndividualScoreMetricAnnotator,
        "speaks_stddev"       : SpeakerScoreStandardDeviationMetricAnnotator,
        "draw_strength"       : DrawStrengthByWinsMetricAnnotator,
        "draw_strength_speaks": DrawStrengthBySpeakerScoreMetricAnnotator,
        "margin_sum"          : SumMarginMetricAnnotator,
        "margin_avg"          : AverageMarginMetricAnnotator,
        "npullups"            : TeamPullupsMetricAnnotator,
        "num_adjs"            : NumberOfAdjudicatorsMetricAnnotator,
        "firsts"              : NumberOfFirstsMetricAnnotator,
        "seconds"             : NumberOfSecondsMetricAnnotator,
        "thirds"              : NumberOfThirdsMetricAnnotator,
        "wbw"                 : WhoBeatWhomMetricAnnotator,
    }

    ranking_annotator_classes = {
        "rank"            : BasicRankAnnotator,
        "subrank"         : SubrankAnnotator,
        "institution_rank": RankFromInstitutionAnnotator,
    }
