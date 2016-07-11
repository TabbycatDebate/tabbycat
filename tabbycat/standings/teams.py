"""Standings generator for teams."""

import logging
from itertools import groupby

from django.db.models import Sum
from django.db.models.expressions import RawSQL

from draw.prefetch import populate_opponents
from participants.models import Round
from results.models import TeamScore

from .base import BaseStandingsGenerator
from .metrics import BaseMetricAnnotator, RepeatedMetricAnnotator, QuerySetMetricAnnotator, metricgetter
from .ranking import BaseRankAnnotator, BasicRankAnnotator, SubrankAnnotator

logger = logging.getLogger(__name__)


# ==============================================================================
# Metric annotators
# ==============================================================================

class TeamScoreQuerySetMetricAnnotator(QuerySetMetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations
    of TeamScore instances."""

    function = None  # must be set by subclasses
    field = None  # must be set by subclasses

    exclude_forfeits = False
    where_value = None

    @staticmethod
    def get_annotation_metric_query_str(field, function, round=None, exclude_forfeits=False, where_value=None):
        """Returns a string, being an SQL query that can be passed into RawSQL()."""
        # This is what might be more concisely expressed, if it were permissible
        # in Django, as:
        # teams = teams.annotate_if(
        #     models.Sum('debateteam__teamscore__{field:s}'),
        #     condition={"debateteam__teamscore__ballot_submission__confirmed": True,
        #         "debateteam__debate__round__stage": Round.STAGE_PRELIMINARY}
        # )
        #
        # That is, it adds up the relevant field on *confirmed* ballots for each
        # team and adds them as columns to the table it returns. The standings
        # include only preliminary rounds.

        query = """
            SELECT DISTINCT {function}({field:s})
            FROM results_teamscore
            JOIN results_ballotsubmission ON results_teamscore.ballot_submission_id = results_ballotsubmission.id
            JOIN draw_debateteam ON results_teamscore.debate_team_id = draw_debateteam.id
            JOIN draw_debate ON draw_debateteam.debate_id = draw_debate.id
            JOIN tournaments_round ON draw_debate.round_id = tournaments_round.id
            WHERE results_ballotsubmission.confirmed = TRUE
            AND draw_debateteam.team_id = participants_team.id
            AND tournaments_round.stage = '""" + str(Round.STAGE_PRELIMINARY) + "\'"

        if round is not None:
            query += """
            AND tournaments_round.seq <= {round:d}""".format(round=round.seq)

        if exclude_forfeits:
            query += """
            AND results_teamscore.forfeit = FALSE"""

        if where_value is not None:
            query += """
            AND {field:s} = """ + str(where_value)

        return query.format(field=field, function=function)

    def get_annotation_metric_query_args(self, round):
        return (self.field, self.function, round, self.exclude_forfeits, self.where_value)


class Points210MetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for team points using win = 2, loss = 1, loss by forfeit = 0."""
    key = "points210"
    name = "points"
    abbr = "Pts"

    choice_name = "Points (2/1/0)"

    def annotate(self, queryset, standings, round=None):
        # Includes forfeits
        wins_query = self.get_annotation_metric_query_str("win", "COUNT", round, False, "TRUE")
        # Excludes forfeits
        losses_query = self.get_annotation_metric_query_str("win", "COUNT", round, True, "FALSE")
        query = "({wins}) * 2 + ({losses})".format(wins=wins_query, losses=losses_query)
        sql = RawSQL(query, ())
        logger.info("Running query: " + query)
        queryset = queryset.annotate(metric=sql).distinct()
        self.annotate_with_queryset(queryset, standings, round)


class PointsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total number of points."""
    key = "points"
    name = "points"
    abbr = "Pts"

    function = "SUM"
    field = "points"


class WinsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total number of wins."""
    key = "wins"
    name = "wins"
    abbr = "Wins"

    function = "COUNT"
    field = "win"
    where_value = "TRUE"


class TotalSpeakerScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "speaks_sum"
    name = "total speaker score"
    abbr = "Spk"

    function = "SUM"
    field = "score"


class AverageSpeakerScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "speaks_avg"
    name = "average speaker score"
    abbr = "ASS"
    exclude_forfeits = True

    function = "AVG"
    field = "score"


class SumMarginMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for sum of margins."""
    key = "margin_sum"
    name = "sum of margins"
    abbr = "Marg"

    function = "SUM"
    field = "margin"


class AverageMarginMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for average margin, excluding forfeit ballots."""
    key = "margin_avg"
    name = "average margin"
    abbr = "AWM"

    function = "AVG"
    field = "margin"
    exclude_forfeits = True


class DrawStrengthMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for draw strength."""
    key = "draw_strength"
    name = "draw strength"
    abbr = "DS"

    def annotate(self, queryset, standings, round=None):
        if not queryset.exists():
            return

        logger.info("Running points query for draw strength:")
        full_queryset = TeamScoreQuerySetMetricAnnotator.get_annotated_queryset(
            queryset[0].tournament.team_set.all(), "points", "points", "SUM", round)

        for team in queryset:
            draw_strength = 0
            debateteam_set = team.debateteam_set.all()
            if round is not None:
                debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
            populate_opponents(debateteam_set)
            for dt in debateteam_set:
                points = full_queryset.get(id=dt.opponent.team_id).points
                if points is not None: # points is None when no debates have happened
                    draw_strength += points
            standings.add_metric(team, self.key, draw_strength)


class NumberOfAdjudicatorsMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for number of adjudicators."""

    key = "num_adjs"
    name = "number of adjudicators"
    abbr = "Adjs"

    def __init__(self, adjs_per_debate=3):
        self.adjs_per_debate = 3

    def annotate(self, queryset, standings, round=None):
        raise NotImplementedError("number of adjudicators doesn't work yet")


class WhoBeatWhomMetricAnnotator(RepeatedMetricAnnotator):
    """Metric annotator for who-beat-whom. Use once for every who-beat-whom in
    the precedence."""

    key_prefix = "wbw"
    name_prefix = "Who-beat-whom"
    abbr_prefix = "WBW"
    choice_name = "who-beat-whom"

    def __init__(self, index, keys):
        if len(keys) == 0:
            raise ValueError("keys must not be empty")
        super(WhoBeatWhomMetricAnnotator, self).__init__(index, keys)

    def get_team_scores(self, key, equal_teams, tsi, round):
        equal_teams.remove(tsi)
        other = equal_teams[0]
        ts = TeamScore.objects.filter(
            ballot_submission__confirmed=True,
            debate_team__team=tsi.team,
            debate_team__debate__debateteam__team=other.team)

        if round is not None:
            ts = ts.filter(debate_team__debate__round__seq__lte=round.seq)

        ts = ts.aggregate(Sum('points'))
        logger.info("who beat whom, {0} {3} vs {1} {4}: {2}".format(
            tsi.team.short_name, other.team.short_name,
            ts["points__sum"], key(tsi), key(other)))
        return ts

    def annotate(self, queryset, standings, round=None):
        key = metricgetter(*self.keys)

        def who_beat_whom(tsi):
            equal_teams = [x for x in standings.infoview() if key(x) == key(tsi)]
            if len(equal_teams) != 2:
                return "n/a"  # fail fast if attempt to compare with an int

            ts = self.get_team_scores(key, equal_teams, tsi, round)
            return ts["points__sum"] or 0

        for tsi in standings.infoview():
            wbw = who_beat_whom(tsi)
            tsi.add_metric(self.key, wbw)


class DivisionsWhoBeatWhomMetricAnnotator(WhoBeatWhomMetricAnnotator):
    """Metric annotator for who-beat-whom within divisions. Use once for
    every who-beat-whom in the precedence."""

    key_prefix = "wbwd"
    name_prefix = "Who-beat-whom (in division)"
    abbr_prefix = "WBWD"
    choice_name = "who-beat-whom (in divisions)"

    def annotate(self, queryset, standings, round=None):
        key = metricgetter(*self.keys)

        def who_beat_whom_divisions(tsi):
            equal_teams = [x for x in standings.infoview() if key(x) == key(tsi) and x.team.division == tsi.team.division]
            if len(equal_teams) != 2:
                return 0  # Fail fast if attempt to compare with an int

            ts = self.get_team_scores(key, equal_teams, tsi, round)
            return ts["points__sum"] or 0

        for tsi in standings.infoview():
            wbwd = who_beat_whom_divisions(tsi)
            tsi.add_metric(self.key, wbwd)


# ==============================================================================
# Ranking annotators
# ==============================================================================

class DivisionRankAnnotator(BaseRankAnnotator):

    key = "division_rank"
    name = "division rank"
    abbr = "DivR"

    def __init__(self, metrics):
        self.rank_key = metricgetter(*metrics)

    def annotate(self, standings):
        division_key = lambda x: x.team.division.name  # flake8: noqa
        by_division = sorted(standings, key=division_key)
        for division, division_teams in groupby(by_division, key=division_key):
            rank = 1
            for key, group in groupby(division_teams, self.rank_key):
                group = list(group)
                for tsi in group:
                    tsi.add_ranking("division_rank", (rank, len(group) > 1))
                rank += len(group)


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
        "points"        : PointsMetricAnnotator,
        "points210"     : Points210MetricAnnotator,
        "wins"          : WinsMetricAnnotator,
        "speaks_sum"    : TotalSpeakerScoreMetricAnnotator,
        "speaks_avg"    : AverageSpeakerScoreMetricAnnotator,
        "draw_strength" : DrawStrengthMetricAnnotator,
        "margin_sum"    : SumMarginMetricAnnotator,
        "margin_avg"    : AverageMarginMetricAnnotator,
        # "num_adjs"      : NumberOfAdjudicatorsMetricAnnotator,
        "wbw"           : WhoBeatWhomMetricAnnotator,
        "wbwd"          : DivisionsWhoBeatWhomMetricAnnotator,
    }

    ranking_annotator_classes = {
        "rank"     : BasicRankAnnotator,
        "subrank"  : SubrankAnnotator,
        "division" : DivisionRankAnnotator,
    }
