from .forms import FloatPreference
from .models import TournamentPreferenceModel
from dynamic_preferences.types import BooleanPreference, StringPreference, IntegerPreference, Section
from dynamic_preferences.registries import PreferenceRegistry, PerInstancePreferenceRegistry, preference_models

# Key
tournament_preferences_registry = PerInstancePreferenceRegistry()
preference_models.register(TournamentPreferenceModel, tournament_preferences_registry)

# ==============================================================================
scoring = Section('scoring')
# ==============================================================================

@tournament_preferences_registry.register
class MinimumSpeakerScore(FloatPreference):
    help_text = "Minimum allowed score for subststantive speeches"
    section = scoring
    name = 'score_min'
    verbose_name = 'Minimum Speaker Score'
    default = 68.0


@tournament_preferences_registry.register
class MaximumSpeakerScore(FloatPreference):
    verbose_name = 'Maximum Speaker Score'
    help_text = "Maximum allowed score for subststantive speeches"
    section = scoring
    name = 'score_max'
    default = 82.0

@tournament_preferences_registry.register
class SpeakerScoreStep(FloatPreference):
    verbose_name = 'Speaker Score Step'
    help_text = "Score steps allowed for substantive speeches, ie full points (1) or half points (0.5)"
    section = scoring
    name = 'score_step'
    default = 1.0

@tournament_preferences_registry.register
class MinimumReplyScore(FloatPreference):
    help_text = "Minimum allowed score for reply speeches"
    verbose_name = 'Minimum Reply Score'
    section = scoring
    name = 'reply_score_min'
    default = 34.0


@tournament_preferences_registry.register
class MaximumReplyScore(FloatPreference):
    help_text = "Maximum allowed score for reply speeches"
    verbose_name = 'Maximum Reply Score'
    section = scoring
    name = 'reply_score_max'
    default = 41.0

@tournament_preferences_registry.register
class ReplyScoreStep(FloatPreference):
    help_text = "Score steps allowed for reply speeches, ie full points (1) or half points (0.5)"
    verbose_name = 'Reply Score Step'
    section = scoring
    name = 'reply_score_step'
    default = 0.5

@tournament_preferences_registry.register
class MaximumMargin(FloatPreference):
    help_text = "The largest amount one team can beat another by (0 means no limit)"
    verbose_name = 'Maximum Margin'
    section = scoring
    name = 'reply_score_step'
    default = 0.0

@tournament_preferences_registry.register
class MarginIncludesDissent(BooleanPreference):
    help_text = "Whether a teams winning margin includes dissenting adj scores"
    verbose_name = 'MarginIncludesDissent'
    section = scoring
    name = 'margin_includes_dissenters'
    default = False

# ==============================================================================
draw_rules = Section('draw_rules')
# ==============================================================================

@tournament_preferences_registry.register
class ChairingScore(FloatPreference):
    help_text = "Minimum adjudicator score required to not trainee in auto-allocation"
    verbose_name = 'Minimum Chairing Score'
    section = draw_rules
    name = 'adj_min_voting_score'
    default = 0.0

@tournament_preferences_registry.register
class VotingScore(FloatPreference):
    help_text = "Minimum adjudicator score required to chair in auto-allocation"
    verbose_name = 'Maximum Chairing Score'
    section = draw_rules
    name = 'adj_chair_min_score'
    default = 0.0

# ==============================================================================
feedback = Section('feedback')
# ==============================================================================

@tournament_preferences_registry.register
class MinimumAdjScore(FloatPreference):
    help_text = "The minmum score an adj can receive"
    verbose_name = 'MinimumAdjScore'
    section = feedback
    name = 'adj_min_score'
    default = 0.0

@tournament_preferences_registry.register
class MaximumAdjScore(FloatPreference):
    help_text = "The maximum score an adj can receive"
    verbose_name = 'MaximumAdjScore'
    section = feedback
    name = 'adj_max_score'
    default = 5.0

@tournament_preferences_registry.register
class ShowUnaccredited(BooleanPreference):
    help_text = "Show if an adjudicator is a novice (unaccredited)"
    verbose_name = "ShowUnaccredited"
    section = feedback
    name = 'show_unaccredited'
    default = False

@tournament_preferences_registry.register
class ScoreReturnLocation(StringPreference):
    help_text = "The location to return scoresheets to (put on preprinted ballot"
    verbose_name = "ScoreReturnLocation"
    section = feedback
    name = 'score_return_location'
    default = 'TBA'

@tournament_preferences_registry.register
class FeedbackReturnLocation(StringPreference):
    help_text = "The location to return feedback to (put on preprinted feedback"
    verbose_name = "FeedbackReturnLocation"
    section = feedback
    name = 'feedback_return_location'
    default = 'TBA'

@tournament_preferences_registry.register
class PanellistFeedbackEnabled(BooleanPreference):
    help_text = "Allow public feedback to be submitted by panellists"
    verbose_name = "PanellistFeedbackEnabled"
    section = feedback
    name = 'panellist_feedback_enabled'
    default = True

@tournament_preferences_registry.register
class FeedbackProgress(BooleanPreference):
    help_text = "Public interface to show who has unsubmitted ballots"
    verbose_name = "FeedbackProgress"
    section = feedback
    name = 'feedback_progress'
    default = False


# ==============================================================================
debate_rules = Section('debate_rules')
# ==============================================================================

@tournament_preferences_registry.register
class SubstantiveSpeakers(IntegerPreference):
    help_text = "How many substantive speakers each team will feature"
    verbose_name = 'Number of substantive speakers in each team'
    section = debate_rules
    name = 'substantive_speakers'
    default = 3


@tournament_preferences_registry.register
class ReplyScores(BooleanPreference):
    help_text = "Whether this style features reply speeches"
    verbose_name = 'Reply Scores'
    section = debate_rules
    name = 'reply_scores_enabled'
    default = True


@tournament_preferences_registry.register
class MotionVetoes(BooleanPreference):
    help_text = "Whether teams rank/veto motions in this style"
    verbose_name = 'Motion Vetoes'
    section = debate_rules
    name = 'motion_vetoes_enabled'
    default = True


# ==============================================================================
break_standings = Section('break_standings')
# ==============================================================================


# ==============================================================================
break_standings = Section('tab__release')
# ==============================================================================



# ==============================================================================
break_standings = Section('data entry')
# ==============================================================================




# ==============================================================================
break_standings = Section('public website features')
# ==============================================================================


# ==============================================================================
break_standings = Section('public website tweaks')
# ==============================================================================



# ==============================================================================
break_standings = Section('league options')
# ==============================================================================