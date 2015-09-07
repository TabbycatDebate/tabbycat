from participants.models import Round

_registry = {}

def register(name, annotator):
    if name in _registry:
        raise ValueError("There is already an annotator called {!r}".format(name))
    _register[name] = annotator

def get_annotator(name):
    try:
        return _register[name]
    except KeyError:
        raise ValueError("There is no annotator {!r}".format(name))

class MetricAnnotator:
    name = NotImplemented
    type = None
    dependencies = []
    adds = []

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
    function = "SUM"
    field = "points"
    adds = ["points"]
register("points", PointsMetricAnnotator)

class SpeakerScoreMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    function = "SUM"
    field = "score"
    adds = ["speaker_score"]
register("speaker_score", SpeakerScoreMetricAnnotator)

class MarginMetricAnnotator(TeamScoreQuerySetMetricAnnotator):
    function = "SUM"
    field = "margin"
    adds = ["margin"]
register("margin", MarginMetricAnnotator)


class DrawStrengthMetricAnnotator(MetricAnnotator):
    dependencies = ["points"]
    adds = ["draw_strength"]

    def annotate(self, queryset, standings, round=None):

        # QuerySets aren't evaluated until needed, so just construct now
        full_queryset = TeamScoreQuerySetMetricAnnotator.get_annotated_queryset(
                queryset[0].tournament.team_set.all(), "points", "SUM", round, "points")

        def get_points(team):
            try:
                return standings.get_team_standing(team).metrics["points"]
            except ValueError:
                return full_queryset.get(id=team.id).points

        for team in queryset:
            draw_strength = 0
            debateteam_set = team.debateteam_set.all()
            if round is not None:
                debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
            for dt in debateteam_set:
                draw_strength += get_points(dt.opposition.team)
            standings.add_metric(team, "draw_strength", draw_strength)

register("draw_strength", PointsMetricAnnotator)


class NumberOfAdjudicatorsMetricAnnotator(MetricAnnotator):
    pass
register("num_adjs", PointsMetricAnnotator)


class WhoBeatWhomMetricAnnotator(MetricAnnotator):
    def __init__(self, key):
        self.key = key

    def annotate(self, queryset, standings, round=None):
        pass

register("wbw", PointsMetricAnnotator)


