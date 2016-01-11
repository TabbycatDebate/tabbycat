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
    name = 'maximum_margin'
    default = 0.0

@tournament_preferences_registry.register
class MarginIncludesDissent(BooleanPreference):
    help_text = "Whether a teams winning margin includes dissenting adj scores"
    verbose_name = 'Margin Includes Dissent'
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

@tournament_preferences_registry.register
class AdjConflictPenalty(IntegerPreference):
    help_text = "Penalty for adjudicator-team conflict"
    verbose_name = "Adj Conflict Penalty"
    section = draw_rules
    name = "adj_conflict_penalty"
    default = 1000000

@tournament_preferences_registry.register
class AdjHistoryPenalty(IntegerPreference):
    help_text = "Penalty for adjudicator-team history"
    verbose_name = "Adj History Penalty"
    section = draw_rules
    name = "adj_history_penalty"
    default = 10000

@tournament_preferences_registry.register
class AvoidSameInstitution(BooleanPreference):
    help_text = "Avoid team-team institution conflicts in draw?"
    verbose_name = "Avoid Same Institution"
    section = draw_rules
    name = "avoid_same_institution"
    default = True

@tournament_preferences_registry.register
class AvoidTeamHistory(BooleanPreference):
    help_text = "Avoid team-team history conflicts in draw?"
    verbose_name = "Avoid Team History"
    section = draw_rules
    name = "avoid_team_history"
    default = True

@tournament_preferences_registry.register
class TeamInstitutionPenalty(IntegerPreference):
    help_text = "Penalty for team-team institution conflict"
    verbose_name = "Team Institution Penalty"
    section = draw_rules
    name = "team_institution_penalty"
    default = 1

@tournament_preferences_registry.register
class TeamHistoryPenalty(IntegerPreference):
    help_text = "Penalty for team-team history conflict"
    verbose_name = "Team History Penalty"
    section = draw_rules
    name = "team_history_penalty"
    default = 1000

@tournament_preferences_registry.register
class DrawOddBracket(StringPreference):
    help_text = "'Odd bracket resolution method, see wiki for allowed values"
    verbose_name = "Draw Odd Bracket"
    section = draw_rules
    name = "draw_odd_bracket"
    default = 'intermediate_bubble_up_down'

@tournament_preferences_registry.register
class DrawSideAllocations(StringPreference):
    help_text = "'Side allocations method, see wiki for allowed values"
    verbose_name = "Draw Side Allocations"
    section = draw_rules
    name = "draw_side_allocations"
    default = 'balance'

@tournament_preferences_registry.register
class DrawPairingMethod(StringPreference):
    help_text = "'Pairing method, see wiki for allowed values"
    verbose_name = "DrawPairingMethod"
    section = draw_rules
    name = "draw_pairing_method"
    default = 'slide'

@tournament_preferences_registry.register
class DrawAvoidConflicts(StringPreference):
    help_text = "Conflict avoidance method, see wiki for allowed values"
    verbose_name = "DrawAvoidConflicts"
    section = draw_rules
    name = "draw_avoid_conflicts"
    default = 'one_up_one_down'

@tournament_preferences_registry.register
class SkipAdjCheckins(BooleanPreference):
    help_text = "Automatically make all adjudicators available for all rounds"
    verbose_name = "Skip Adj Checkins"
    section = draw_rules
    name = "draw_skip_adj_checkins"
    default = False

# ==============================================================================
feedback = Section('feedback')
# ==============================================================================

@tournament_preferences_registry.register
class MinimumAdjScore(FloatPreference):
    help_text = "The minmum score an adj can receive"
    verbose_name = 'Minimum Adj Score'
    section = feedback
    name = 'adj_min_score'
    default = 0.0

@tournament_preferences_registry.register
class MaximumAdjScore(FloatPreference):
    help_text = "The maximum score an adj can receive"
    verbose_name = 'Maximum Adj Score'
    section = feedback
    name = 'adj_max_score'
    default = 5.0

@tournament_preferences_registry.register
class ShowUnaccredited(BooleanPreference):
    help_text = "Show if an adjudicator is a novice (unaccredited)"
    verbose_name = "Show Unaccredited"
    section = feedback
    name = 'show_unaccredited'
    default = False

@tournament_preferences_registry.register
class ScoreReturnLocation(StringPreference):
    help_text = "The location to return scoresheets to (put on preprinted ballot"
    verbose_name = "Score Return Location"
    section = feedback
    name = 'score_return_location'
    default = 'TBA'

@tournament_preferences_registry.register
class FeedbackReturnLocation(StringPreference):
    help_text = "The location to return feedback to (put on preprinted feedback"
    verbose_name = "Feedback Return Location"
    section = feedback
    name = 'feedback_return_location'
    default = 'TBA'

@tournament_preferences_registry.register
class PanellistFeedbackEnabled(BooleanPreference):
    help_text = "Allow public feedback to be submitted by panellists"
    verbose_name = "Panellist Feedback Enabled"
    section = feedback
    name = 'panellist_feedback_enabled'
    default = True



# ==============================================================================
debate_rules = Section('debate_rules')
# ==============================================================================

@tournament_preferences_registry.register
class SubstantiveSpeakers(IntegerPreference):
    help_text = "How many substantive speakers each team will feature"
    verbose_name = 'Substantive Speakers'
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
standings = Section('standings')
# ==============================================================================

@tournament_preferences_registry.register
class StandingsMissedDebates(IntegerPreference):
    help_text = 'The number of debates you can miss and still be on the speaker tab'
    verbose_name = "Standings Missed Debates"
    section = standings
    name = "standings_missed_debates"
    default = 1

@tournament_preferences_registry.register
class StandingsMethod(StringPreference):
    help_text = 'Speaker rankings are by total (Yes) or average score (No)'
    verbose_name = "Standings Method"
    section = standings
    name = "standings_method"
    default = 'australs'


@tournament_preferences_registry.register
class TeamStandingsRule(StringPreference):
    help_text = 'Rule for ordering teams, "australs" or "nz" or "wadl" see wiki'
    verbose_name = "Team Standings Rule"
    section = standings
    name = "team_standings_rule"
    default = 'australs'


# ==============================================================================
tab_release = Section('tab_release')
# ==============================================================================


@tournament_preferences_registry.register
class TabReleased(BooleanPreference):
    help_text = 'Displays the tab PUBLICLY. For AFTER the tournament'
    verbose_name = "Tab Released"
    section = tab_release
    name = "tab_released"
    default = False

@tournament_preferences_registry.register
class MotionTabReleased(BooleanPreference):
    help_text = 'Displays the motions tab PUBLICLY. For AFTER the tournament'
    verbose_name = "Motion Tab Released"
    section = tab_release
    name = "motion_tab_released"
    default = False

@tournament_preferences_registry.register
class BallotsReleased(BooleanPreference):
    help_text = 'Displays ballots PUBLICLY. For AFTER the tournament'
    verbose_name = "BallotsReleased"
    section = tab_release
    name = "ballots_released"
    default = False


# ==============================================================================
data_entry = Section('data_entry')
# ==============================================================================

@tournament_preferences_registry.register
class PublicBallots(BooleanPreference):
    help_text = 'Public interface to add ballots using normal URLs'
    verbose_name = "Public Ballots"
    section = data_entry
    name = "public_ballots"
    default = False

@tournament_preferences_registry.register
class PublicBallotsRandomised(BooleanPreference):
    help_text = 'Public interface to add ballots using randomised URLs'
    verbose_name = "Public Ballots Randomised"
    section = data_entry
    name = "public_ballots_randomised"
    default = False

@tournament_preferences_registry.register
class PublicFeedback(BooleanPreference):
    help_text = 'Public interface to add feedback using normal URLs'
    verbose_name = "PublicFeedback"
    section = data_entry
    name = "public_feedback"
    default = False

@tournament_preferences_registry.register
class PublicFeedbackRandomised(BooleanPreference):
    help_text ='Public interface to add feedback using randomised URLs'
    verbose_name = "PublicFeedbackRandomised"
    section = data_entry
    name = "public_feedback_randomised"
    default = False

@tournament_preferences_registry.register
class PublicUsePassword(BooleanPreference):
    help_text = 'Require password to submit public feedback and ballots'
    verbose_name = "PublicUsePassword"
    section = data_entry
    name = "public_use_password"
    default = False

@tournament_preferences_registry.register
class PublicPassword(StringPreference):
    help_text = 'Value of the password for public submissions'
    verbose_name = "Public Password"
    section = data_entry
    name = "public_password"
    default = 'Enter Password'

@tournament_preferences_registry.register
class EnableAssistantConfirms(BooleanPreference):
    help_text = 'Enables Assistant users to confirm their own ballots'
    verbose_name = "Enable Assistant Confirms"
    section = data_entry
    name = "enable_assistant_confirms"
    default = False


# ==============================================================================
public_features = Section('public_features')
# ==============================================================================

@tournament_preferences_registry.register
class PublicParticipants(BooleanPreference):
    help_text = 'Public interface to see all participants'
    verbose_name = "Public Participants"
    section = public_features
    name = "public_participants"
    default = False

@tournament_preferences_registry.register
class PublicBreakCategories(BooleanPreference):
    help_text = 'Show break categories on the participants page'
    verbose_name = "Public Break Categories"
    section = public_features
    name = "public_break_categories"
    default = False

@tournament_preferences_registry.register
class PublicSideAllocations(BooleanPreference):
    help_text = 'Public interface to see side pre-allocations'
    verbose_name = "Public Side Allocations"
    section = public_features
    name = "public_side_allocations"
    default = False

@tournament_preferences_registry.register
class PublicDraw(BooleanPreference):
    help_text = 'Public interface to see RELEASED draws'
    verbose_name = "Public Draw"
    section = public_features
    name = "public_draw"
    default = False

@tournament_preferences_registry.register
class PublicResults(BooleanPreference):
    help_text = 'Public interface to see results from previous rounds'
    verbose_name = "Public Results"
    section = public_features
    name = "public_results"
    default = False

@tournament_preferences_registry.register
class PublicMotions(BooleanPreference):
    help_text = 'Public interface to see RELEASED motions'
    verbose_name = "Public Motions"
    section = public_features
    name = "public_motions"
    default = True

@tournament_preferences_registry.register
class PublicTeamStandings(BooleanPreference):
    help_text = 'Public interface to see team standings DURING tournament'
    verbose_name = "Public Team Standings"
    section = public_features
    name = "public_team_standings"
    default = False

@tournament_preferences_registry.register
class PublicBreakingTeams(BooleanPreference):
    help_text = 'Public interface to see breaking teams, for AFTER the break announcement'
    verbose_name = "Public Breaking Teams"
    section = public_features
    name = "public_breaking_teams"
    default = False

@tournament_preferences_registry.register
class PublicBreakingAdjs(BooleanPreference):
    help_text = 'Public interface to see breaking adjudicators, for AFTER the break announcement'
    verbose_name = "Public Breaking Adjs"
    section = public_features
    name = "public_breaking_adjs"
    default = False

@tournament_preferences_registry.register
class FeedbackProgress(BooleanPreference):
    help_text = "Public interface to show who has unsubmitted ballots"
    verbose_name = "Feedback Progress"
    section = public_features
    name = 'feedback_progress'
    default = False

# ==============================================================================
ui_options = Section('ui_options')
# ==============================================================================

@tournament_preferences_registry.register
class ShowSplittingAdjudicators(BooleanPreference):
    help_text = 'If showing public results, show splitting adjudicators',
    verbose_name = 'Show Splitting Adjudicators'
    name = 'show_splitting_adjudicators'
    section = ui_options
    default = False

@tournament_preferences_registry.register
class ShowMotionsInResults(BooleanPreference):
    help_text = 'If showing public results, show motions with results',
    verbose_name = 'Show Motions In Results'
    section = ui_options
    name = 'show_motions_in_results'
    default = False

@tournament_preferences_registry.register
class ShowEmoji(BooleanPreference):
    help_text = 'Shows Emoji in the draw UI',
    verbose_name = 'Show Emoji'
    section = ui_options
    name = 'show_emoji'
    default = True

@tournament_preferences_registry.register
class ShowInstitutions(BooleanPreference):
    help_text = 'Shows the institutions column in draw and other UIs',
    verbose_name = 'Show Institutions'
    section = ui_options
    name = 'show_institutions'
    default = True

@tournament_preferences_registry.register
class ShowNovices(BooleanPreference):
    help_text = 'Show if a speaker is a novice',
    verbose_name = 'Show Novices'
    section = ui_options
    name = 'show_novices'
    default = False

@tournament_preferences_registry.register
class ShowSpeakersInDraw(BooleanPreference):
    help_text = 'Disable/Enable a hover element showing each teams speakers in the UI',
    verbose_name = 'Show Speakers In Draw'
    section = ui_options
    name = 'show_speakers_in_draw'
    default = True

@tournament_preferences_registry.register
class ShowAllDraws(BooleanPreference):
    help_text = 'If showing public draws, show all (past & future) RELEASED draws',
    verbose_name = 'Show All Draws'
    section = ui_options
    name = 'show_all_draws'
    default = False

@tournament_preferences_registry.register
class PublicMotionsDescending(BooleanPreference):
    help_text = 'List motions by round in descending order (as opposed to ascending)'
    verbose_name = "Public Motions Descending"
    section = ui_options
    name = "public_motions_descending"
    default = True

# ==============================================================================
league_options = Section('league_options')
# ==============================================================================

@tournament_preferences_registry.register
class PublicDivisions(BooleanPreference):
    help_text = 'Public interface to see divisions'
    verbose_name = "Public Divisions"
    section = league_options
    name = "public_divisions"
    default = False

@tournament_preferences_registry.register
class ShowAvgMmargin(BooleanPreference):
    help_text = 'Enables a display of average margins in the team standings'
    verbose_name = "Show Average Mmargin"
    section = league_options
    name = "show_avg_margin"
    default = False

@tournament_preferences_registry.register
class TeamPointsRule(StringPreference):
    help_text = '"normal" means 1 win = 1 point, "wadl" uses 2/1/0 for win/loss/forfeit'
    verbose_name = "TeamPointsRule"
    section = league_options
    name = "team_points_rule"
    default = 'normal'

@tournament_preferences_registry.register
class EnableDivisions(BooleanPreference):
    help_text = 'Enables the sorting and display of teams into divisions'
    verbose_name = "EnableDivisions"
    section = league_options
    name = "enable_divisions"
    default = False

@tournament_preferences_registry.register
class EnablePostponements(BooleanPreference):
    help_text = 'Enables debates to have their status set to postponed'
    verbose_name = "Enable Postponements"
    section = league_options
    name = "enable_postponements"
    default = False

@tournament_preferences_registry.register
class enable_forfeits(BooleanPreference):
    help_text = 'Enables one side of a debate to be in forfeit'
    verbose_name = "Enable Forfeits"
    section = league_options
    name = "enable_forfeits"
    default = False

@tournament_preferences_registry.register
class enable_division_motions(BooleanPreference):
    help_text = 'Enables assigning motions to a division'
    verbose_name = "Enable Division Motions"
    section = league_options
    name = "enable_division_motions"
    default = False

@tournament_preferences_registry.register
class minimum_division_size(IntegerPreference):
    help_text = 'Smallest allowed size for a division'
    verbose_name = "Minimum Division Size"
    section = league_options
    name = "minimum_division_size"
    default = 5

@tournament_preferences_registry.register
class ideal_division_size(IntegerPreference):
    help_text = 'Ideal size for a division'
    verbose_name = "Ideal Division Size"
    section = league_options
    name = "ideal_division_size"
    default = 6

@tournament_preferences_registry.register
class MaximumDivisionSize(IntegerPreference):
    help_text = 'Largest allowed size for a division'
    verbose_name = "Maximum Division Size"
    section = league_options
    name = "maximum_division_size"
    default = 8

@tournament_preferences_registry.register
class EnableFlaggedMotions(BooleanPreference):
    help_text = 'Allow particular motions to be flagged as contentious'
    verbose_name = "Enable Flagged Motions"
    section = league_options
    name = "enable_flagged_motions"
    default = False


@tournament_preferences_registry.register
class EnableAdjNotes(BooleanPreference):
    help_text = 'Enables a general-purpose notes field for adjudicators'
    verbose_name = "Enable Adj Notes"
    section = league_options
    name = "enable_adj_notes"
    default = False

@tournament_preferences_registry.register
class EnableVenueGroups(BooleanPreference):
    help_text = 'Enables the display of a venues grouping'
    verbose_name = "Enable Venue Groups"
    section = league_options
    name = "enable_venue_groups"
    default = False

@tournament_preferences_registry.register
class EnableVenueTimes(BooleanPreference):
    help_text = 'Enables dates and times to be set for venues'
    verbose_name = "Enable Venue Times"
    section = league_options
    name = "enable_venue_times"
    default = False

@tournament_preferences_registry.register
class EnableVenueOverlaps(BooleanPreference):
    help_text = 'Allow and automatically debates to be placed in the first room'
    verbose_name = "Enable Venue Overlaps"
    section = league_options
    name = "enable_venue_overlaps"
    default = False

@tournament_preferences_registry.register
class ShareAdjs(BooleanPreference):
    help_text = 'Display adjudicators from other tournaments'
    verbose_name = "Share Adjs"
    section = league_options
    name = "share_adjs"
    default = False

@tournament_preferences_registry.register
class DuplicateAdjs(BooleanPreference):
    help_text = 'Allow each adjudicator to be allocated to multiple rooms'
    verbose_name = "Duplicate Adjs"
    section = league_options
    name = "duplicate_adjs"
    default = False


