from django.db.models import TextChoices
from rest_framework import serializers

from breakqual.models import BreakCategory
from participants.models import Adjudicator, Region, SpeakerCategory
from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator
from tournaments.models import Round

from . import fields


class InstitutionParamsSerializer(serializers.Serializer):
    region = serializers.SlugRelatedField(
        queryset=Region.objects.all(),
        slug_field='name',
        required=False,
    )


class AdjudicatorParamsSerializer(serializers.Serializer):
    vars()['break'] = serializers.BooleanField(required=False)


class StandingsParamsSerializer(serializers.Serializer):
    round = fields.TournamentSlugRelatedField(
        slug_field='seq', queryset=Round.objects.all(), required=False,
    )


class SpeakerStandingsParamsSerializer(serializers.Serializer):
    metrics = fields.CharacterSeparatedField(separator=",",
        child=serializers.ChoiceField(choices=SpeakerStandingsGenerator.get_metric_choices()),
        required=False, allow_null=True)
    extra_metrics = fields.CharacterSeparatedField(
        separator=",",
        child=serializers.ChoiceField(choices=SpeakerStandingsGenerator.get_metric_choices(ranked_only=False, for_extra=True)), required=False, allow_null=True)
    category = fields.TournamentPrimaryKeyRelatedField(queryset=SpeakerCategory.objects.all(), required=False)


class TeamStandingsParamsSerializer(serializers.Serializer):
    metrics = fields.CharacterSeparatedField(separator=",",
        child=serializers.ChoiceField(choices=TeamStandingsGenerator.get_metric_choices()),
        required=False, allow_null=True)
    extra_metrics = fields.CharacterSeparatedField(
        separator=",",
        child=serializers.ChoiceField(choices=TeamStandingsGenerator.get_metric_choices(ranked_only=False, for_extra=True)), required=False, allow_null=True)
    category = fields.TournamentPrimaryKeyRelatedField(queryset=BreakCategory.objects.all(), required=False)


class SpeakerRoundStandingsRoundsParamsSerializer(serializers.Serializer):
    ghost = serializers.BooleanField(required=False)
    replies = serializers.BooleanField(required=False)
    substantive = serializers.BooleanField(required=False)


class BallotParamsSerializer(serializers.Serializer):
    confirmed = serializers.BooleanField(required=False, allow_null=True)


class FeedbackQuestionParamsSerializer(serializers.Serializer):
    from_adj = serializers.BooleanField(required=False)
    from_team = serializers.BooleanField(required=False)


class FeedbackParamsSerializer(serializers.Serializer):
    class SourceType(TextChoices):
        ADJ = 'adjudicator', 'Adjudicator'
        TEAM = 'team', 'Team'

    source_type = serializers.ChoiceField(choices=SourceType.choices, required=False)
    source = serializers.IntegerField(required=False)
    round = fields.TournamentSlugRelatedField(
        slug_field='seq', queryset=Round.objects.all(), required=False,
    )
    target = fields.TournamentPrimaryKeyRelatedField(queryset=Adjudicator.objects.all(), required=False)


class AvailabilitiesParamsSerializer(serializers.Serializer):
    adjudicators = serializers.BooleanField(required=False)
    teams = serializers.BooleanField(required=False)
    venues = serializers.BooleanField(required=False)
