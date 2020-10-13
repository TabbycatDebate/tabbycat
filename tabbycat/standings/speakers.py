"""Standings generator for speakers."""

import logging

from django.db.models import Avg, Case, Count, F, FloatField, Max, Min, Q, StdDev, Sum, When
from django.utils.translation import gettext_lazy as _

from tournaments.models import Round

from .base import BaseStandingsGenerator
from .metrics import QuerySetMetricAnnotator
from .ranking import BasicRankAnnotator

logger = logging.getLogger(__name__)


# ==============================================================================
# Metric annotators
# ==============================================================================

class SpeakerScoreQuerySetMetricAnnotator(QuerySetMetricAnnotator):
    """Base class for annotators for metrics based on conditional aggregations
    of SpeakerScore instances."""

    function = None  # Must be set by subclasses
    replies = False

    def get_annotation(self, round):
        """Returns a QuerySet annotated with the metric given. All positional
        arguments from the third onwards, and all keyword arguments, are passed
        to get_annotation_metric_query_str()."""

        annotation_filter = Q(
            speakerscore__ballot_submission__confirmed=True,
            speakerscore__debate_team__debate__round__seq__lte=round.seq,
            speakerscore__debate_team__debate__round__stage=Round.STAGE_PRELIMINARY,
            speakerscore__ghost=False,
        )
        if self.replies:
            annotation_filter &= Q(speakerscore__position=round.tournament.reply_position)
        else:
            annotation_filter &= Q(speakerscore__position__lte=round.tournament.last_substantive_position)

        return self.function('speakerscore__score', filter=annotation_filter)


class TotalSpeakerScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for total speaker score."""
    key = "total"
    name = _("total")
    abbr = _("Total")
    function = Sum


class AverageSpeakerScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for average speaker score."""
    key = "average"
    name = _("average")
    abbr = _("Avg")
    function = Avg


class SpeakerTeamPointsMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):

    key = "team_points"
    name = _("team points")
    abbr = _("Team")

    def get_annotation(self, round):
        """Returns a QuerySet annotated with the metric given. All positional
        arguments from the third onwards, and all keyword arguments, are passed
        to get_annotation_metric_query_str()."""

        annotation_filter = Q(
            team__debateteam__teamscore__ballot_submission__confirmed=True,
            team__debateteam__debate__round__seq__lte=round.seq,
            team__debateteam__debate__round__stage=Round.STAGE_PRELIMINARY,
        )

        return Sum('team__debateteam__teamscore__points', filter=annotation_filter)


class StandardDeviationSpeakerScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for standard deviation of speaker score."""
    key = "stdev"
    name = _("standard deviation")
    abbr = _("Stdev")
    function = StdDev
    ascending = True


class NumberOfSpeechesMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for number of speeches given."""
    key = "count"
    name = _("number of speeches given")
    abbr = _("Num")
    function = Count


class TotalReplyScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for total reply score."""
    key = "replies_sum"
    name = _("total")
    abbr = _("Total")
    function = Sum
    replies = True
    listed = False


class AverageReplyScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for average reply score."""
    key = "replies_avg"
    name = _("average")
    abbr = _("Avg")
    function = Avg
    replies = True
    listed = False


class StandardDeviationReplyScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for standard deviation of reply score."""
    key = "replies_stddev"
    name = _("standard deviation")
    abbr = _("Stdev")
    function = StdDev
    replies = True
    listed = False
    ascending = True


class NumberOfRepliesMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for number of replies given."""
    key = "replies_count"
    name = _("replies given")
    abbr = _("Num")
    function = Count
    replies = True
    listed = False


class TrimmedMeanSpeakerScoreMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for trimmed mean speaker score."""
    key = "trimmed_mean"
    name = _("trimmed mean (high-low drop)")
    abbr = _("Trim")

    class SpeechCount(NumberOfSpeechesMetricAnnotator):
        key = 'speech_count'

    class MaximumScore(SpeakerScoreQuerySetMetricAnnotator):
        function = Max

    class MinimumScore(SpeakerScoreQuerySetMetricAnnotator):
        function = Min

    def get_annotated_queryset(self, queryset, round=None):
        # Slight breach of separation of concerns: add the 'count' annotation so
        # that the main annotation will know what 'count' means. We can't do
        # this inline in get_annotation() because Django doesn't support the
        # syntax F('count') > 2, and we're forced to use count__gt=2 instead.
        queryset = self.SpeechCount().get_annotated_queryset(queryset, round=round)
        return super().get_annotated_queryset(queryset, round=round)

    def get_annotation(self, round=None):
        total = TotalSpeakerScoreMetricAnnotator().get_annotation(round)
        highest = self.MaximumScore().get_annotation(round)
        lowest = self.MinimumScore().get_annotation(round)

        return Case(
            When(speech_count__gt=2, then=(total - highest - lowest) / (F('speech_count') - 2)),
            When(speech_count__gt=0, then=total / F('speech_count')),
            default=None,
            output_field=FloatField(),
        )


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
        "total"         : TotalSpeakerScoreMetricAnnotator,
        "average"       : AverageSpeakerScoreMetricAnnotator,
        "trimmed_mean"  : TrimmedMeanSpeakerScoreMetricAnnotator,
        "team_points"   : SpeakerTeamPointsMetricAnnotator,
        "stdev"         : StandardDeviationSpeakerScoreMetricAnnotator,
        "count"         : NumberOfSpeechesMetricAnnotator,
        "replies_sum"   : TotalReplyScoreMetricAnnotator,
        "replies_avg"   : AverageReplyScoreMetricAnnotator,
        "replies_stddev": StandardDeviationReplyScoreMetricAnnotator,
        "replies_count" : NumberOfRepliesMetricAnnotator,
    }

    ranking_annotator_classes = {
        "rank"     : BasicRankAnnotator,
    }
