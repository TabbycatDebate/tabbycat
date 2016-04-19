"""Standings generator for speakers."""

from .base import BaseStandingsGenerator, StandingsError
from .metrics import BaseMetricAnnotator, metricgetter
from .ranking import BasicRankAnnotator

# ==============================================================================
# Metric annotators
# ==============================================================================

class SpeakerScoreQuerySetMetricAnnotator(BaseMetricAnnotator):
    """Base class for annotators for metrics based on conditional aggregations
    of SpeakerScore instances."""

    function = None # must be set by subclasses
    field = None # must be set by subclasses
    replies = False

    @staticmethod
    def get_annotation_metric_query_str(function, round, replies=False):
        """Returns a string, being an SQL query that can be passed into RawSQL()."""
        # This is what might be more concisely expressed, if it were permissible
        # in Django, as:
        # teams = teams.annotate_if(
        #     models.Count('debateteam__teamscore__{field:s}'),
        #     condition={"debateteam__teamscore__ballot_submission__confirmed": True,
        #         "debateteam__debate__round__stage": Round.STAGE_PRELIMINARY}
        # )
        #
        # That is, it adds up the relevant field on *confirmed* ballots for each
        # team and adds them as columns to the table it returns. The standings
        # include only preliminary rounds.

        query = """
            SELECT DISTINCT {function}(score)
            FROM results_speakerscore
            JOIN results_ballotsubmission ON results_speakerscore.ballot_submission_id = results_ballotsubmission.id
            JOIN draw_debateteam ON results_speakerscore.debate_team_id = draw_debateteam.id
            JOIN draw_debate ON draw_debateteam.debate_id = draw_debate.id
            JOIN tournaments_round ON draw_debate.round_id = tournaments_round.id
            WHERE results_ballotsubmission.confirmed = TRUE
            AND results_speakerscore.speaker_id = participants_speaker.id
            AND tournaments_round.stage = '{stage:s}'
            AND tournaments_round.seq <= {round:d}""".format(stage=Round.STAGE_PRELIMINARY, round=round.seq)

        if replies:
            query += """
            AND results_speakerscore.position = {position:d}""".format(position=round.tournament.REPLY_POSITION)
        else:
            query += """
            AND results_speakerscore.position <= {position:d}""".format(position=round.tournament.LAST_SUBSTANTIVE_POSITION)

        return query.format(field=field, function=function)

    def get_annotation_metric_query_args(self, round):
        return (self.function, round, self.replies)


class TotalSpeakerScoreMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "speaks_sum"
    name = "total speaker score"
    abbr = "Total"
    function = "SUM"


class AverageSpeakerScoreMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for average speaker score."""
    key = "speaks_avg"
    name = "average speaker score"
    abbr = "Avg"
    function = "AVG"


class NumberOfSpeechesMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for number of speeches given."""
    key = "speaks_avg"
    name = "number of speeches"
    abbr = "Num"
    function = "COUNT"


class TotalReplyScoreMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for total reply score."""
    key = "replies_sum"
    name = "total reply score"
    abbr = "Total"
    function = "SUM"


class AverageReplyScoreMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for average reply score."""
    key = "replies_avg"
    name = "average reply score"
    abbr = "Avg"
    function = "AVG"


class NumberOfRepliesMetricAnnotator(BaseMetricAnnotator):
    """Metric annotator for number of replies given."""
    key = "replies_count"
    name = "number of replies"
    abbr = "Num"
    function = "COUNT"


# ==============================================================================
# Standings generator
# ==============================================================================

class SpeakerStandingsGenerator(BaseStandingsGenerator):
    """Class for generating speaker standings. An instance is configured with
    metrics and rankings in the constructor, and an iterable of Speaker objects
    is passed to its `generate()` method to generate standings. Example:

        generator = TeamStandingsGenerator(('points', 'speaker_score'), ('rank',))
        standings = generator.generate(teams)

    The generate() method returns a TeamStandings object.
    """

    TIEBREAK_FUNCTIONS = BaseStandingsGenerator.TIEBREAK_FUNCTIONS.copy()
    TIEBREAK_FUNCTIONS["name"] = lambda x: x.sort(key=lambda y: y.speaker.name)
    TIEBREAK_FUNCTIONS["institution"] = lambda x: x.sort(key=lambda y: y.speaker.team.institution.name)

    metric_annotator_classes = {
        "speaks_sum"    : TotalSpeakerScoreMetricAnnotator,
        "speaks_avg"    : AverageSpeakerScoreMetricAnnotator,
        "speeches_count": NumberOfSpeechesMetricAnnotator,
        "replies_sum"   : TotalReplyScoreMetricAnnotator,
        "replies_avg"   : AverageReplyScoreMetricAnnotator,
        "replies_count" : NumberOfRepliesMetricAnnotator,
    }

    ranking_annotator_classes = {
        "rank"     : BasicRankAnnotator,
    }
