"""Metric annotators for the standings generator.

Each metric annotator is responsible for computing a particular metric for each
team and annotating team standings with them, for example, number of wins
(points), or draw strength.

Note: There's a registry at the bottom of the file. If you add a new
MetricAnnotator subclass, be sure to add it to the registry.
"""

from django.db.models import Sum
from django.db.models.expressions import RawSQL
from participants.models import Round
from results.models import TeamScore
from operator import itemgetter

import random
import logging
logger = logging.getLogger(__name__)

def metricgetter(*items):
    """Returns a callable object that fetches `item` from its operand's
    `metrics` attribute. If multiple items are specified, returns a tuple.
    For example:
     - After `f = metricgetter("a")`, the call `f(x)` returns `x.metrics["a"]`.
     - After `g = metricgetter(4, 9)`, the call `g(x)` returns `(x.metrics[4], x.metrics[9])`.
    """
    return lambda x: itemgetter(*items)(x.metrics)

def get_metric_choices():
    choices = []
    for key, annotator in registry.items():
        if hasattr(annotator, 'choice_name'):
            choice_name = annotator.choice_name.capitalize()
        else:
            choice_name = annotator.name.capitalize()
        choices.append((key, choice_name))
    choices.sort(key=lambda x: x[1])
    return choices

def MetricAnnotator(name, *args, **kwargs):
    """Factory function. Returns an instance of an appropriate subclass of
    BaseMetricAnnotator, with the given arguments passed to the constructor."""
    klass = registry[name]
    return klass(*args, **kwargs)


class BaseMetricAnnotator:
    """Base class for all metric annotators.

    A metric annotator is a class that adds a metric to a TeamStandings object.
    Subclasses must implement the method `annotate_teams()`. Every annotator
    must add precisely one metric.

    Subclasses must set the `key`, `name` and `abbr` attributes.

    The default constructor does nothing, but subclasses may have constructors
    that initialise themselves with parameters."""

    key = None # must be set by subclasses
    name = None # must be set by subclasses
    abbr = None # must be set by subclasses
    glyphicon = None

    def annotate(self, queryset, standings, round=None):
        standings.record_added_metric(self.key, self.name, self.abbr, self.glyphicon)
        self.annotate_teams(queryset, standings, round)

    def annotate_teams(self, queryset, standings, round=None):
        """Annotates the given `standings` by calling `add_metric()` on every
        `TeamStandingInfo` object in `standings`.

        `queryset` is the queryset of teams.
        `standings` is a `TeamStandings` object.
        `round`, if specified, is a `Round` object that is assumed to be in the
            relevant tournament.
        """
        raise NotImplementedError("BaseMetricAnnotator subclasses must implement annotate_teams()")


class RepeatedMetricAnnotator(BaseMetricAnnotator):
    """Base class for metric annotators that can be used multiple times.

    Subclasses should set the `key_prefix`, `name_prefix` and `abbr_prefix`
    class attributes, and use the `key` attribute when adding metrics in
    implementing `annotate_teams()`."""

    def __init__(self, index):
        self.index = index
        self.key = self.key_prefix + str(index)
        self.name = self.name_prefix + " " + str(index)
        self.abbr = self.abbr_prefix + str(index)


class TeamScoreQuerySetMetricAnnotator(BaseMetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations
    of TeamScore instances.

    Other annotators can use this class as a mixin, using
    `get_annotated_queryset()` but overriding `annotate()`."""

    function = None # must be set by subclasses
    field = None # must be set by subclasses

    exclude_forfeits = False
    where_value = None

    @classmethod
    def get_annotated_queryset(cls, queryset, field, function, round=None, column_name="metric"):
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
            FROM "results_teamscore"
            JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
            JOIN "draw_debateteam" ON "results_teamscore"."debate_team_id" = "draw_debateteam"."id"
            JOIN "draw_debate" ON "draw_debateteam"."debate_id" = "draw_debate"."id"
            JOIN "tournaments_round" ON "draw_debate"."round_id" = "tournaments_round"."id"
            WHERE "results_ballotsubmission"."confirmed" = True
            AND "draw_debateteam"."team_id" = "participants_team"."id"
            AND "tournaments_round"."stage" = '""" + str(Round.STAGE_PRELIMINARY) + "\'"

        if round is not None:
            TEAM_SCORE_ANNOTATION_QUERY += """
            AND "tournaments_round"."seq" <= {round:d}""".format(round=round.seq)

        if cls.exclude_forfeits:
            TEAM_SCORE_ANNOTATION_QUERY += """
            AND "results_teamscore"."forfeit" = FALSE"""

        if cls.where_value is not None:
            TEAM_SCORE_ANNOTATION_QUERY += """
            AND "{field:s}" = """ + str(cls.where_value)

        query = TEAM_SCORE_ANNOTATION_QUERY.format(field=field, function=function)
        logger.info("Running query: " + query)

        sql = RawSQL(query, ())
        return queryset.annotate(**{column_name: sql}).distinct()

    def annotate_teams(self, queryset, standings, round=None):
        for team in self.get_annotated_queryset(queryset, self.field, self.function, round):
            standings.add_metric_to_team(team, self.key, team.metric)


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

    def annotate_teams(self, queryset, standings, round=None):
        if not queryset.exists():
            return

        logger.info("Running points query for draw strength:")
        full_queryset = TeamScoreQuerySetMetricAnnotator.get_annotated_queryset(
                queryset[0].tournament.team_set.all(), "points", "SUM", round, "points")

        for team in queryset:
            draw_strength = 0
            debateteam_set = team.debateteam_set.all()
            if round is not None:
                debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
            for dt in debateteam_set:
                points = full_queryset.get(id=dt.opposition.team_id).points
                if points is not None: # points is None when no debates have happened
                    draw_strength += points
            standings.add_metric_to_team(team, self.key, draw_strength)


class NumberOfAdjudicatorsMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for number of adjudicators."""

    key = "num_adjs"
    name = "number of adjudicators"
    abbr = "Adjs"

    def __init__(self, adjs_per_debate=3):
        self.adjs_per_debate = 3

    def annotate_teams(self, queryset, standings, round=None):
        raise NotImplementedError("number of adjudicators doesn't work yet")


class WhoBeatWhomMetricAnnotator(RepeatedMetricAnnotator):
    """Metric annotator for who-beat-whom. Use once for every who-beat-whom in
    the precedence."""

    key_prefix = "wbw"
    name_prefix = "WBW"
    abbr_prefix = "WBW"
    choice_name = "who-beat-whom"

    def __init__(self, index, keys):
        super(WhoBeatWhomMetricAnnotator, self).__init__(index)
        if len(keys) == 0:
            raise ValueError("keys must not be empty")
        self.keys = keys

    def annotate_teams(self, queryset, standings, round=None):
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


registry = {
    "points"        : PointsMetricAnnotator,
    "wins"          : WinsMetricAnnotator,
    "speaks_sum"    : TotalSpeakerScoreMetricAnnotator,
    "speaks_avg"    : AverageSpeakerScoreMetricAnnotator,
    "draw_strength" : DrawStrengthMetricAnnotator,
    "margin_sum"    : SumMarginMetricAnnotator,
    "margin_avg"    : AverageMarginMetricAnnotator,
    # "num_adjs"      : NumberOfAdjudicatorsMetricAnnotator,
    "wbw"           : WhoBeatWhomMetricAnnotator,
}
