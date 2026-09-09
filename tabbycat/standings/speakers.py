"""Standings generator for speakers."""

import logging
from functools import partialmethod

from django.db.models import Avg, Case, Count, F, FloatField, Max, Min, Q, StdDev, Sum, When
from django.db.models.functions import Cast, NullIf
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

    function = None
    replies = False
    field = 'speakerscore__score'
    where_value = None

    def get_annotation_filter(self, round):
        """Returns the Q object restricting which speeches the metric counts."""
        annotation_filter = Q(
            speakerscore__ballot_submission__confirmed=True,
            speakerscore__debate_team__debate__round__seq__lte=round.seq,
            speakerscore__debate_team__debate__round__stage=Round.Stage.PRELIMINARY,
            speakerscore__ghost=False,
        )
        if self.replies:
            annotation_filter &= Q(speakerscore__position=round.tournament.reply_position)
        else:
            annotation_filter &= Q(speakerscore__position__lte=round.tournament.last_substantive_position)

        return annotation_filter

    def get_annotation(self, round):
        """Returns a QuerySet annotated with the metric given. All positional
        arguments from the third onwards, and all keyword arguments, are passed
        to get_annotation_metric_query_str()."""
        return self.function(self.field, filter=self.get_annotation_filter(round))


class TeamMetricQuerySetMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):

    combinable = False

    def get_annotation(self, round):
        """Returns a QuerySet annotated with the metric."""
        annotation_filter = Q(
            team__debateteam__teamscore__ballot_submission__confirmed=True,
            team__debateteam__debate__round__seq__lte=round.seq,
            team__debateteam__debate__round__stage=Round.Stage.PRELIMINARY,
        )
        if self.where_value is not None:
            annotation_filter &= Q(**{self.field: self.where_value})

        return self.function(self.field, filter=annotation_filter)


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


class SpeakerTeamPointsMetricAnnotator(TeamMetricQuerySetMetricAnnotator):
    """Metric annotator for team points."""
    key = "team_points"
    name = _("team points")
    abbr = _("Team")

    field = 'team__debateteam__teamscore__points'
    function = Sum


class SpeakerTeamWinsMetricAnnotator(TeamMetricQuerySetMetricAnnotator):
    """Metric annotator for total number of wins for the team that the speaker is in."""
    key = "team_wins"
    name = _("Wins")
    abbr = _("Wins")

    function = Count
    field = 'team__debateteam__teamscore__win'
    where_value = True


class SpeakerFirstsMetricAnnotator(TeamMetricQuerySetMetricAnnotator):
    """Metric annotator for counting the number of first-place finishes (points = 3) for a speaker's team."""
    key = "firsts"
    name = _("number of firsts")
    abbr = _("1sts")

    function = Count
    field = 'team__debateteam__teamscore__points'
    where_value = 3


class SpeakerNumberOfSecondsMetricAnnotator(TeamMetricQuerySetMetricAnnotator):
    """Metric annotator for counting the number of second-place finishes (points = 2) for a speaker's team."""
    key = "seconds"
    name = _("number of seconds")
    abbr = _("2nds")

    function = Count
    field = 'team__debateteam__teamscore__points'
    where_value = 2


class SpeakerNumberOfThirdsMetricAnnotator(TeamMetricQuerySetMetricAnnotator):
    """Metric annotator for counting the number of third-place finishes (points = 1) for a speaker's team."""
    key = "thirds"
    name = _("number of thirds")
    abbr = _("3rds")

    function = Count
    field = 'team__debateteam__teamscore__points'
    where_value = 1


class NumberOfAdjudicatorsMetricAnnotator(TeamMetricQuerySetMetricAnnotator):
    key = "num_adjs"
    name = _("number of adjudicators who voted for this team")
    abbr = _("Ballots")
    choice_name = _("votes/ballots carried")
    function = Sum

    def __init__(self, adjs_per_debate=3):
        self.adjs_per_debate = adjs_per_debate

    def get_field(self):
        return (Cast('team__debateteam__teamscore__votes_given', FloatField()) /
            NullIf('team__debateteam__teamscore__votes_possible', 0, output_field=FloatField()) *
            self.adjs_per_debate)

    def annotate_with_queryset(self, queryset, standings):
        cast = int if all(t.num_adjs == int(t.num_adjs) for t in queryset if t.num_adjs is not None) else float
        for item in queryset:
            metric = item.num_adjs or 0
            standings.add_metric(item, self.key, cast(metric))


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
            output_field=FloatField(),
        )


class SpeakerScoreRankingsMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Metric annotator for standard deviation of speaker score."""
    key = "srank"
    name = _("speech ranks")
    abbr = _("SRank")
    function = Sum
    ascending = True
    field = 'speakerscore__rank'


# ==============================================================================
# Score criterion metric annotators
# ==============================================================================

class BaseCriterionMetricAnnotator(SpeakerScoreQuerySetMetricAnnotator):
    """Base class for metrics on a single score criterion. These are keyed by
    the criterion's seq, so use criterion_metric_annotator_classes() to build
    them for a tournament rather than instantiating these directly."""

    field = 'speakerscore__speakercriterionscore__score'
    key_prefix = None  # must be set by subclasses
    name_format = None  # must be set by subclasses
    abbr_format = None  # must be set by subclasses

    # The criterion join gives one row per criterion per speech, which would
    # inflate other aggregations if combined into the shared query.
    combinable = False

    # Set by views dedicated to a single criterion, where the criterion's name
    # is already in the page title and would just repeat in every column.
    standalone = False

    def __init__(self, criterion):
        self.criterion = criterion
        self.key = self.build_key(criterion.seq)
        self.name = self.name_format % {'criterion': criterion.name}
        self.abbr = self.short_abbr if self.standalone else (
            self.abbr_format % {'criterion': criterion.name})

    @classmethod
    def build_key(cls, seq):
        return '%s%d' % (cls.key_prefix, seq)

    @classmethod
    def choice_label(cls):
        return (cls.name_format % {'criterion': cls.criterion_name}).capitalize()

    def get_annotation_filter(self, round):
        # The inherited filter restricts this to the substantive speeches, as
        # for the other speaker metrics. The criterion's own speech_type
        # doesn't narrow it further: a criterion is only ever scored on the
        # speeches it applies to, and one scored only on replies has no
        # standings of its own.
        return super().get_annotation_filter(round) & Q(
            speakerscore__speakercriterionscore__criterion=self.criterion)


class TotalCriterionScoreMetricAnnotator(BaseCriterionMetricAnnotator):
    """Metric annotator for total score on a single criterion."""
    key_prefix = "criterion_total_"
    name_format = _("total for %(criterion)s")
    abbr_format = _("%(criterion)s Total")
    short_abbr = _("Total")
    function = Sum


class AverageCriterionScoreMetricAnnotator(BaseCriterionMetricAnnotator):
    """Metric annotator for average score on a single criterion."""
    key_prefix = "criterion_avg_"
    name_format = _("average for %(criterion)s")
    abbr_format = _("%(criterion)s Avg")
    short_abbr = _("Avg")
    function = Avg


def is_criterion_metric_key(key):
    """Whether `key` names a score criterion metric. The criteria themselves are
    per-tournament, so preference validation, which has no tournament to hand,
    checks the key's shape only; unknown criteria are ignored when the standings
    are generated."""
    for base in (AverageCriterionScoreMetricAnnotator, TotalCriterionScoreMetricAnnotator):
        if key.startswith(base.key_prefix) and key[len(base.key_prefix):].isdigit():
            return True
    return False


def criterion_metric_annotator_classes(tournament, standalone_criterion=None):
    """Returns the metric annotator classes for every score criterion in the
    tournament, keyed by metric key. Each binds its criterion, so that they can
    be used like the classes in SpeakerStandingsGenerator's static dict.

    `standalone_criterion`, if given, is the criterion whose page this is, and
    so whose metrics should be labelled without repeating its name."""
    classes = {}
    for criterion in tournament.scorecriterion_set.all():
        for base in (AverageCriterionScoreMetricAnnotator, TotalCriterionScoreMetricAnnotator):
            key = base.build_key(criterion.seq)
            classes[key] = type(base.__name__, (base,), {
                '__init__': partialmethod(base.__init__, criterion),
                'key': key,
                'criterion_name': criterion.name,
                'standalone': criterion == standalone_criterion,
            })
    return classes


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

    QUERYSET_TIEBREAK_FIELDS = BaseStandingsGenerator.QUERYSET_TIEBREAK_FIELDS.copy()
    QUERYSET_TIEBREAK_FIELDS["name"] = 'name'
    QUERYSET_TIEBREAK_FIELDS["institution"] = 'team__institution__name'

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
        "srank"         : SpeakerScoreRankingsMetricAnnotator,
        "team_wins"     : SpeakerTeamWinsMetricAnnotator,
        "firsts"        : SpeakerFirstsMetricAnnotator,
        "seconds"       : SpeakerNumberOfSecondsMetricAnnotator,
        "thirds"        : SpeakerNumberOfThirdsMetricAnnotator,
        "num_adjs"      : NumberOfAdjudicatorsMetricAnnotator,
    }

    ranking_annotator_classes = {
        "rank"     : BasicRankAnnotator,
    }

    tournament_field = 'team__tournament'

    def __init__(self, metrics, rankings, extra_metrics=(), tournament=None,
            standalone_criterion=None, **options):
        # Score criteria are per-tournament rows, so their annotator classes
        # can't live in the class-level dict; build them per instance.
        if tournament is not None:
            self.metric_annotator_classes = {
                **self.metric_annotator_classes,
                **criterion_metric_annotator_classes(tournament, standalone_criterion),
            }
        super().__init__(metrics, rankings, extra_metrics, **options)

    @classmethod
    def get_metric_choices(cls, ranked_only=True, for_extra=False, tournament=None):
        """Adds this tournament's score criteria to the standard choices."""
        choices = super().get_metric_choices(ranked_only=ranked_only, for_extra=for_extra)
        if tournament is None:
            return choices

        criterion_choices = [
            (key, annotator.choice_label())
            for key, annotator in criterion_metric_annotator_classes(tournament).items()
        ]
        criterion_choices.sort(key=lambda x: x[1])
        return choices + criterion_choices
