"""Standings generator for teams."""

import random
import logging
logger = logging.getLogger(__name__)
from itertools import groupby

from django.db.models import Sum
from django.db.models.expressions import RawSQL

from participants.models import Round
from participants.models import Team
from results.models import TeamScore

from .base import BaseStandingsGenerator, StandingsError
from .metrics import BaseMetricAnnotator, RepeatedMetricAnnotator, metricgetter
from .ranking import BaseRankAnnotator, BasicRankAnnotator, SubrankAnnotator

# ==============================================================================
# Metric annotators
# ==============================================================================

class TeamScoreQuerySetMetricAnnotator(BaseMetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations
    of TeamScore instances.

    Other annotators can use this class as a mixin, using
    `get_annotated_queryset()` but overriding `annotate()`."""

    function = None # must be set by subclasses
    field = None # must be set by subclasses

    exclude_forfeits = False
    where_value = None

    @staticmethod
    def get_annotation_metric_query_str(field, function, round=None,
            exclude_forfeits=False, where_value=None):
        """Returns a string, being an SQL query that can be passed into RawSQL()."""
        # This is what might be more concisely expressed, if it were permissible
        # in Django, as:
        # teams = teams.annotate_if(
        #     models.Count('debateteam__teamscore__{field:s}'),
        #     condition={"debateteam__teamscore__ballot_submission__confirmed": True}
        # )
        #
        # That is, it adds up the relevant field on *confirmed* ballots for each
        # team and adds them as columns to the table it returns. The standings
        # include only preliminary rounds.

        TEAM_SCORE_ANNOTATION_QUERY = """
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
            TEAM_SCORE_ANNOTATION_QUERY += """
            AND tournaments_round.seq <= {round:d}""".format(round=round.seq)

        if exclude_forfeits:
            TEAM_SCORE_ANNOTATION_QUERY += """
            AND results_teamscore.forfeit = FALSE"""

        if where_value is not None:
            TEAM_SCORE_ANNOTATION_QUERY += """
            AND {field:s} = """ + str(where_value)

        return TEAM_SCORE_ANNOTATION_QUERY.format(field=field, function=function)

    @classmethod
    def get_annotated_queryset(cls, queryset, column_name, *args, **kwargs):
        """Returns a QuerySet annotated with the metric given. All positional
        arguments from the third onwards, and all keyword arguments, are passed
        to get_annotation_metric_query_str()."""
        query = cls.get_annotation_metric_query_str(*args, **kwargs)
        logger.info("Running query: " + query)
        sql = RawSQL(query, ())
        return queryset.annotate(**{column_name: sql}).distinct()

    def annotate_with_queryset(self, queryset, standings, round=None):
        """Annotates teams with the given QuerySet, using the "metric" field."""
        for team in queryset:
            if team.metric is None:
                logger.warning("Metric {metric!r} for team {team} was None, setting to 0".format(
                        metric=self.key, team=team.short_name))
                team.metric = 0
            standings.add_metric(team, self.key, team.metric)

    def annotate(self, queryset, standings, round=None):
        queryset = self.get_annotated_queryset(queryset, "metric", self.field,
                self.function, round, self.exclude_forfeits, self.where_value)
        self.annotate_with_queryset(queryset, standings, round)


class Points210MetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for team points using win = 2, loss = 1, loss by forfeit = 0."""
    key = "points210"
    name = "points"
    abbr = "Pts"

    choice_name = "Points (2/1/0)"

    def annotate(self, queryset, standings, round=None):
        wins_query = self.get_annotation_metric_query_str("win", "COUNT", round, False, "TRUE") # includes forfeits
        losses_query = self.get_annotation_metric_query_str("win", "COUNT", round, True, "FALSE") # excludes forfeits
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
            for dt in debateteam_set:
                points = full_queryset.get(id=dt.opposition.team_id).points
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
    name_prefix = "WBW"
    abbr_prefix = "WBW"
    choice_name = "who-beat-whom"

    def __init__(self, index, keys):
        if len(keys) == 0:
            raise ValueError("keys must not be empty")
        super(WhoBeatWhomMetricAnnotator, self).__init__(index, keys)

    def annotate(self, queryset, standings, round=None):
        key = metricgetter(*self.keys)

        def who_beat_whom(tsi):
            equal_teams = [x for x in standings.infoview() if key(x) == key(tsi)]
            if len(equal_teams) != 2:
                return "n/a" # fail fast if attempt to compare with an int
            equal_teams.remove(tsi)
            team = tsi
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
            return ts["points__sum"] or 0

        for tsi in standings.infoview():
            wbw = who_beat_whom(tsi)
            tsi.add_metric(self.key, wbw)


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
        division_key = lambda x: x.team.division.name
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
    }

    ranking_annotator_classes = {
        "rank"     : BasicRankAnnotator,
        "subrank"  : SubrankAnnotator,
        "division" : DivisionRankAnnotator,
    }
