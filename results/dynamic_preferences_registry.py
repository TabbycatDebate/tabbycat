

# Config settings

from dynamic_preferences.types import BooleanPreference, StringPreference, Section
from dynamic_preferences import user_preferences_registry, global_preferences_registry



from tournaments.models import Tournament
from django.db import models
from dynamic_preferences.models import PerInstancePreferenceModel
class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = 'dynamic_preferences' # Can't change this
        verbose_name = "Tournament Preference"
        verbose_name_plural = "Tournament Preferencess"



from dynamic_preferences.registries import PreferenceRegistry, PerInstancePreferenceRegistry
tournament_preferences_registry = PerInstancePreferenceRegistry()

from dynamic_preferences.registries import autodiscover, preference_models
preference_models.register(TournamentPreferenceModel, tournament_preferences_registry)


# now we declare a per-tournament preference
# @tournament_preferences_registry.register
# class CommentNotificationsEnabled(BooleanPreference):
#     """Do you want to be notified on comment publication ?"""
#     section = scoring
#     name = 'comment_notifications_enabled'
#     default = True


from dynamic_preferences.serializers import BaseSerializer
class FloatSerializer(BaseSerializer):

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, float):
            raise cls.exception('FloatSerializer can only serialize float values')
        return value

    @classmethod
    def to_python(cls, value, **kwargs):
        try:
            return float(value)
        except:
            raise cls.exception("Value {0} cannot be converted to a float")

from dynamic_preferences.types import BasePreferenceType
from django import forms
class FloatPreference(BasePreferenceType):

    field_class = forms.FloatField
    serializer = FloatSerializer


scoring = Section('scoring')
public = Section('public')

@tournament_preferences_registry.register
class MinimumSpeakerScore(FloatPreference):
    help_text = "Minimum allowed score for subststantive speeches"
    section = scoring
    name = 'score_min'
    verbose_name = 'Minimum Speaker Score'
    default = 68.0


@tournament_preferences_registry.register
class MaximumSpeakerScore(FloatPreference):
    help_text = "Maximum allowed score for subststantive speeches"
    section = scoring
    name = 'score_max'
    verbose_name = 'Maximum Speaker Score'
    default = 82.0

@tournament_preferences_registry.register
class SpeakerScoreStep(FloatPreference):
    help_text = "Score steps allowed for substantive speeches, ie full points (1) or half points (0.5)"
    section = scoring
    name = 'score_step'
    verbose_name = 'Speaker Score Step'
    default = 1.0


@tournament_preferences_registry.register
class ReplySpeakerScore(FloatPreference):
    """Minimum allowed score for reply speeches"""
    section = scoring
    name = 'reply_score_min'
    default = 34.0


@tournament_preferences_registry.register
class ReplySpeakerScore(FloatPreference):
    """Maximum allowed score for reply speeches"""
    section = scoring
    name = 'reply_score_max'
    default = 41.0

@tournament_preferences_registry.register
class ReplyScoreStep(FloatPreference):
    """Score steps allowed for reply speeches, ie full points (1) or half points (0.5)"""
    section = scoring
    name = 'reply_score_step'
    default = 0.5


@tournament_preferences_registry.register
class ShowTest(BooleanPreference):
    """test"""
    section = public
    name = 'public'
    default = False
