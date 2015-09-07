from participants.models import Round
import logging
logger = logging.getLogger(__name__)

METRIC_ANNOTATORS = {
    "points": PointsMetricAnnotator,
    "margin": MarginMetricAnnotator,
    "draw_strength": DrawStrengthMetricAnnotator,
    "speaker_score": SpeakerScoreMetricAnnotator,
    "num_adjs": NumberOfAdjudicatorsMetricAnnotator,
}

class MetricAnnotator:
    adds = NotImplemented

    def annotate(self, queryset, standings, round=None):
        """Annotates the given `standings` by calling `add_metric()` on every
        `TeamStandingInfo` object in `standings`.

        `queryset` is the queryset of teams.
        `standings` is a `TeamStandings` object.
        `round`, if specified, is a `Round` object that is assumed to be in the
            relevant tournament.
        """
        raise NotImplementedError("MetricAnnotator subclasses must implement annotate()")

class TeamScoreQuerySetMetricAnnotator(MetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations
    of TeamScore instances.

    Other annotators can use this class as a mixin, using
    `get_annotated_queryset()` but overriding `annotate()`."""

    function = NotImplemented
    field = NotImplemented

    @staticmethod
    def get_annotated_queryset(queryset, field, function, round=None, column_name="metric"):
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
            EXTRA_QUERY += """ AND "tournaments_round"."seq" <= {round:d}""".format(round=round.seq)

        sql = RawSQL(TEAM_SCORE_ANNOTATION_QUERY.format(field=field, function=function), ())
        return queryset.annotate(**{column_name: sql}).distinct()

    def annotate(self, queryset, standings, round=None):
        for team in self.get_annotated_queryset(queryset, self.field, self.function, round):
            standings.add_metric(team, self.adds[0], team.metric)


class PointsMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total number of points."""
    function = "SUM"
    field = "points"
    adds = ["points"]

class SpeakerScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    function = "SUM"
    field = "score"
    adds = ["speaker_score"]

class MarginMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    """Metric annotator for sum of margins."""
    function = "SUM"
    field = "margin"
    adds = ["margin"]


class DrawStrengthMetricAnnotator(MetricAnnotator):
    """Metric annotator for draw strength."""
    adds = ["draw_strength"]

    def annotate(self, queryset, standings, round=None):
        full_queryset = TeamScoreQuerySetMetricAnnotator.get_annotated_queryset(
                queryset[0].tournament.team_set.all(), "points", "SUM", round, "points")

        for team in queryset:
            draw_strength = 0
            debateteam_set = team.debateteam_set.all()
            if round is not None:
                debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
            for dt in debateteam_set:
                draw_strength += full_queryset.get(id=dt.opposition.team_id).points
            standings.add_metric(team, "draw_strength", draw_strength)

register("draw_strength", PointsMetricAnnotator)


class NumberOfAdjudicatorsMetricAnnotator(MetricAnnotator):
    pass


class WhoBeatWhomMetricAnnotator(MetricAnnotator):
    """Adds a who-beat-whom metric. Use once for every who-beat-whom in the
    precedence."""

    def __init__(self, index, keys):
        self.index = index
        self.keys = keys
        self.metricname = "wbw" + str(self.index)

    @property
    def adds(self):
        return [self.metricname]

    def annotate(self, queryset, standings, round=None):
        key = lambda x: itemgetter(*self.keys)(x.metrics)

        def who_beat_whom(tsi):
            equal_teams = [x for x in standings if key(x) == key(tsi)]
            if len(equal_teams) != 2:
                return "n/a" # fail fast if attempt to compare with an int
            equal_teams.remove(tsi)
            other = equal_teams[0]
            ts = TeamScore.objects.filter(
                    ballot_submission__confirmed=True,
                    debate_team__team=team,
                    debate_team__debate__debateteam__team=other)
            if round is not None:
                ts = ts.filter(debate_team__debate__round__seq__lte=round.seq)
            ts = ts.aggregate(Sum('points'))
            logger.info("who beat whom, {0} {3} vs {1} {4}: {2}".format(team.short_name, other.short_name, ts["points__sum"], key(team), key(other)))
            return ts["points__sum"] or 0

        for tsi in standings.infoview():
            wbw = who_beat_whom(tsi)
            tsi.add_metric(self.metricname, wbw)


class WhoBeatWhomDisplayMetricAnnotator(MetricAnnotator):
    """Adds the 'who_beat_whom_display' annotation. Should be run after all
    WhoBeatWhomMetricAnnotators are run."""
    adds = ["who_beat_whom_display"]

    def annotate(self, queryset, standings, round=None):
        for tsi in standings.infoview():
            wbws = [(k, str(v)) for k, v in tsi.metrics if k.startswith("wbw") and k[3:].isdigit()]
            wbws.sort(key=itemgetter(0))
            tsi.add_metric("who_beat_whom_display", ", ".join(i[1] for i in wbws))
