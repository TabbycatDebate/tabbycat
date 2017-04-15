from dynamic_preferences.types import BooleanPreference, ChoicePreference, FloatPreference, IntegerPreference, Section, StringPreference

from standings.teams import TeamStandingsGenerator
from tournaments.utils import get_position_name_choices

from .types import MultiValueChoicePreference
from .models import tournament_preferences_registry


# ==============================================================================
scoring = Section('scoring')
# ==============================================================================


@tournament_preferences_registry.register
class MinimumSpeakerScore(FloatPreference):
    help_text = "Minimum allowed score for substantive speeches"
    section = scoring
    name = 'score_min'
    verbose_name = 'Minimum speaker score'
    default = 68.0


@tournament_preferences_registry.register
class MaximumSpeakerScore(FloatPreference):
    verbose_name = 'Maximum speaker score'
    help_text = "Maximum allowed score for substantive speeches"
    section = scoring
    name = 'score_max'
    default = 82.0


@tournament_preferences_registry.register
class SpeakerScoreStep(FloatPreference):
    verbose_name = 'Speaker score step'
    help_text = "Score steps allowed for substantive speeches, e.g. full points (1) or half points (0.5)"
    section = scoring
    name = 'score_step'
    default = 1.0


@tournament_preferences_registry.register
class MinimumReplyScore(FloatPreference):
    help_text = "Minimum allowed score for reply speeches"
    verbose_name = 'Minimum reply score'
    section = scoring
    name = 'reply_score_min'
    default = 34.0


@tournament_preferences_registry.register
class MaximumReplyScore(FloatPreference):
    help_text = "Maximum allowed score for reply speeches"
    verbose_name = 'Maximum reply score'
    section = scoring
    name = 'reply_score_max'
    default = 41.0


@tournament_preferences_registry.register
class ReplyScoreStep(FloatPreference):
    help_text = "Score steps allowed for reply speeches, e.g. full points (1) or half points (0.5)"
    verbose_name = 'Reply score step'
    section = scoring
    name = 'reply_score_step'
    default = 0.5


@tournament_preferences_registry.register
class MaximumMargin(FloatPreference):
    help_text = "The largest amount by which one team can beat another (0 means no limit)"
    verbose_name = 'Maximum margin'
    section = scoring
    name = 'maximum_margin'
    default = 0.0


@tournament_preferences_registry.register
class MarginIncludesDissent(BooleanPreference):
    help_text = "If checked, a team's winning margin includes dissenting adjudicators"
    verbose_name = 'Margin includes dissenters'
    section = scoring
    name = 'margin_includes_dissenters'
    default = False

# ==============================================================================
draw_rules = Section('draw_rules')
# ==============================================================================


@tournament_preferences_registry.register
class VotingScore(FloatPreference):
    help_text = "The auto-allocator will only take adjudicators at or above this score as voting panellists"
    verbose_name = 'Minimum adjudicator score to vote'
    section = draw_rules
    name = 'adj_min_voting_score'
    default = 1.5


@tournament_preferences_registry.register
class AdjConflictPenalty(IntegerPreference):
    help_text = "Penalty applied by auto-allocator for adjudicator-team conflict"
    verbose_name = "Adjudicator-team conflict penalty"
    section = draw_rules
    name = "adj_conflict_penalty"
    default = 1000000


@tournament_preferences_registry.register
class AdjHistoryPenalty(IntegerPreference):
    help_text = "Penalty applied by auto-allocator for adjudicator-team history"
    verbose_name = "Adjudicator-team history penalty"
    section = draw_rules
    name = "adj_history_penalty"
    default = 10000


@tournament_preferences_registry.register
class AvoidSameInstitution(BooleanPreference):
    help_text = "If checked, the draw will try to avoid pairing teams against their own institution"
    verbose_name = "Avoid same institution"
    section = draw_rules
    name = "avoid_same_institution"
    default = True


@tournament_preferences_registry.register
class AvoidTeamHistory(BooleanPreference):
    help_text = "If checked, the draw will try to avoid having teams see each other twice"
    verbose_name = "Avoid team history"
    section = draw_rules
    name = "avoid_team_history"
    default = True


@tournament_preferences_registry.register
class TeamInstitutionPenalty(IntegerPreference):
    help_text = "Penalty applied by conflict avoidance method for teams seeing their own institution"
    verbose_name = "Team institution penalty"
    section = draw_rules
    name = "team_institution_penalty"
    default = 1


@tournament_preferences_registry.register
class TeamHistoryPenalty(IntegerPreference):
    help_text = "Penalty applied by conflict avoidance method for teams seeing each other twice or more"
    verbose_name = "Team history penalty"
    section = draw_rules
    name = "team_history_penalty"
    default = 1000


@tournament_preferences_registry.register
class DrawOddBracket(ChoicePreference):
    help_text = "How odd brackets are resolved (see documentation for further details)"
    verbose_name = "Odd bracket resolution method"
    section = draw_rules
    name = "draw_odd_bracket"
    choices = (
        ('pullup_top', 'Pull up from top'),
        ('pullup_bottom', 'Pull up from bottom'),
        ('pullup_random', 'Pull up at random'),
        ('intermediate', 'Intermediate bubbles'),
        ('intermediate_bubble_up_down', 'Intermediate with bubble-up-bubble-down'),
        ('intermediate1', 'Intermediate 1 (pre-allocated sides)'),
        ('intermediate2', 'Intermediate 2 (pre-allocated sides)'),
    )
    default = 'intermediate_bubble_up_down'


@tournament_preferences_registry.register
class DrawSideAllocations(ChoicePreference):
    help_text = "How affirmative/negative positions are assigned (see documentation for further details)"
    verbose_name = "Side allocations method"
    section = draw_rules
    name = "draw_side_allocations"
    choices = (
        ('random', 'Random'),
        ('balance', 'Balance'),
        ('preallocated', 'Pre-allocated'),
        ('manual-ballot', 'Manually enter from ballot'),
    )
    default = 'balance'


@tournament_preferences_registry.register
class DrawPairingMethod(ChoicePreference):
    help_text = "Slide: 1 vs 6, 2 vs 7, …. Fold: 1 vs 10, 2 vs 9, …. Adjacent: 1 vs 2, 3 vs 4, …."
    verbose_name = "Pairing method"
    section = draw_rules
    name = "draw_pairing_method"
    choices = (
        ('slide', 'Slide'),
        ('fold', 'Fold'),
        ('random', 'Random'),
        ('adjacent', 'Adjacent'),
        ('fold_top_adjacent_rest', 'Fold top, adjacent rest'),
    )
    default = 'slide'


@tournament_preferences_registry.register
class DrawAvoidConflicts(ChoicePreference):
    help_text = "Method used to try to avoid teams facing each other multiple times or their own institution (see documentation for further details)"
    verbose_name = "Conflict avoidance method"
    section = draw_rules
    name = "draw_avoid_conflicts"
    choices = (
        ('off', 'Off'),
        ('one_up_one_down', 'One-up-one-down'),
    )
    default = 'one_up_one_down'


@tournament_preferences_registry.register
class SkipAdjCheckins(BooleanPreference):
    help_text = "Automatically make all adjudicators available for all rounds"
    verbose_name = "Skip adjudicator check-ins"
    section = draw_rules
    name = "draw_skip_adj_checkins"
    default = False


@tournament_preferences_registry.register
class HidePanellistPosition(BooleanPreference):
    help_text = "Hide panellist positions in the UI (and don't allocate them)"
    verbose_name = "No panellist adjudicators"
    section = draw_rules
    name = "no_panellist_position"
    default = False


@tournament_preferences_registry.register
class HideTraineePosition(BooleanPreference):
    help_text = "Hide trainee positions in the UI (and don't allocate them)"
    verbose_name = "No trainee adjudicators"
    section = draw_rules
    name = "no_trainee_position"
    default = False

# ==============================================================================
feedback = Section('feedback')
# ==============================================================================


@tournament_preferences_registry.register
class FeedbackIntroduction(StringPreference):
    help_text = "Any explanatory text needed to introduce the feedback form"
    verbose_name = "Feedback introduction/explanation"
    section = feedback
    name = 'feedback_introduction'
    default = ''

    def get_field_kwargs(self):
        kwargs = super().get_field_kwargs()
        kwargs['required'] = False
        return kwargs


@tournament_preferences_registry.register
class MinimumAdjScore(FloatPreference):
    help_text = "Minimum possible adjudicator score that can be given"
    verbose_name = 'Minimum adjudicator score'
    section = feedback
    name = 'adj_min_score'
    default = 0.0


@tournament_preferences_registry.register
class MaximumAdjScore(FloatPreference):
    help_text = "Maximum possible adjudicator score that can be given"
    verbose_name = 'Maximum adjudicator score'
    section = feedback
    name = 'adj_max_score'
    default = 5.0


@tournament_preferences_registry.register
class ShowUnaccredited(BooleanPreference):
    help_text = "Show if an adjudicator is a novice (unaccredited)"
    verbose_name = "Show unaccredited"
    section = feedback
    name = 'show_unaccredited'
    default = False


@tournament_preferences_registry.register
class ScoreReturnLocation(StringPreference):
    help_text = "The location to return scoresheets to, printed on pre-printed ballots"
    verbose_name = "Score return location"
    section = feedback
    name = 'score_return_location'
    default = 'TBA'


@tournament_preferences_registry.register
class FeedbackReturnLocation(StringPreference):
    help_text = "The location to return feedback to, printed on pre-printed feedback forms"
    verbose_name = "Feedback return location"
    section = feedback
    name = 'feedback_return_location'
    default = 'TBA'


@tournament_preferences_registry.register
class FeedbackPaths(ChoicePreference):
    help_text = "Used to inform available choices in the feedback forms for adjudicators (both online and printed) and feedback progress"
    verbose_name = "Allow and expect feedback to be submitted by"
    section = feedback
    name = 'feedback_paths'
    choices = (
        ('minimal', 'Chairs on panellists and trainees'),
        ('with-p-on-c', 'Panellists on chairs, chairs on panellists and trainees'),
        ('all-adjs', 'All adjudicators (including trainees) on each other'),
    )
    default = 'minimal'


@tournament_preferences_registry.register
class FeedbackFromTeams(ChoicePreference):
    verbose_name = "Expect feedback to be submitted by teams on"
    help_text = "Used to inform available choices in the feedback forms for teams (both online and printed) and feedback progress; this option is used by, e.g., UADC"
    section = feedback
    name = 'feedback_from_teams'
    choices = (
        ('orallist', 'Orallist only (voting panellists permitted, with prompts to select orallist)'),
        ('all-adjs', 'All adjudicators in their panels (including trainees)'),
    )
    default = 'orallist'


@tournament_preferences_registry.register
class ShowUnexpectedFeedback(BooleanPreference):
    verbose_name = "Show unexpected feedback submissions in participants pages"
    help_text = "Displays unexpected feedback with a question mark symbol; only relevant if public participants and feedback progress are both enabled"
    section = feedback
    name = 'show_unexpected_feedback'
    default = True


# ==============================================================================
debate_rules = Section('debate_rules')
# ==============================================================================


@tournament_preferences_registry.register
class SubstantiveSpeakers(IntegerPreference):
    help_text = "How many substantive speakers on a team"
    verbose_name = 'Substantive speakers'
    section = debate_rules
    name = 'substantive_speakers'
    default = 3


@tournament_preferences_registry.register
class ReplyScores(BooleanPreference):
    help_text = "Whether this style features reply speeches"
    verbose_name = 'Reply scores'
    section = debate_rules
    name = 'reply_scores_enabled'
    default = True


@tournament_preferences_registry.register
class MotionVetoes(BooleanPreference):
    help_text = "Enables the motion veto field on ballots, to track veto statistics"
    verbose_name = 'Motion vetoes'
    section = debate_rules
    name = 'motion_vetoes_enabled'
    default = True


@tournament_preferences_registry.register
class PositionNames(ChoicePreference):
    help_text = "What to call the teams"
    verbose_name = "Position names"
    section = debate_rules
    name = 'position_names'
    choices = get_position_name_choices()
    default = 'aff-neg'


# ==============================================================================
standings = Section('standings')
# ==============================================================================


@tournament_preferences_registry.register
class StandingsMissedDebates(IntegerPreference):
    help_text = "The number of debates a speaker can miss and still be on the speaker tab"
    verbose_name = "Debates missable for standings eligibility"
    section = standings
    name = "standings_missed_debates"
    default = 1


@tournament_preferences_registry.register
class RankSpeakersBy(ChoicePreference):
    help_text = "How speakers are ranked on the speaker tab"
    verbose_name = "Rank speakers by"
    section = standings
    name = "rank_speakers_by"
    choices = (
        ('average', 'Average'),
        ('total', 'Total'),
    )
    default = 'total'


@tournament_preferences_registry.register
class TeamStandingsPrecedence(MultiValueChoicePreference):
    help_text = "Metrics to use to rank teams (see documentation for further details)"
    verbose_name = "Team standings precedence"
    section = standings
    name = "team_standings_precedence"
    choices = TeamStandingsGenerator.get_metric_choices()
    nfields = 8
    allow_empty = True
    default = ['wins', 'speaks_avg']


@tournament_preferences_registry.register
class TeamStandingsExtraMetrics(MultiValueChoicePreference):
    help_text = "Metrics not used to rank teams"
    verbose_name = "Team standings extra metrics"
    section = standings
    name = "team_standings_extra_metrics"
    choices = TeamStandingsGenerator.get_metric_choices(ranked_only=False)
    nfields = 5
    allow_empty = True
    default = []

# ==============================================================================
tab_release = Section('tab_release')
# ==============================================================================


@tournament_preferences_registry.register
class TeamTabReleased(BooleanPreference):
    help_text = "Enables public display of the team tab. Intended for use after the tournament."
    verbose_name = "Release team tab to public"
    section = tab_release
    name = "team_tab_released"
    default = False


@tournament_preferences_registry.register
class TeamTabReleaseLimit(IntegerPreference):
    help_text = "Only show scores for the top X teams in the public tab (set to 0 to show all teams)."
    verbose_name = "Top teams cutoff"
    section = tab_release
    name = "team_tab_limit"
    default = 0


@tournament_preferences_registry.register
class SpeakerTabReleased(BooleanPreference):
    help_text = "Enables public display of the speaker tab. Intended for use after the tournament."
    verbose_name = "Release speaker tab to public"
    section = tab_release
    name = "speaker_tab_released"
    default = False


@tournament_preferences_registry.register
class SpeakerTabReleaseLimit(IntegerPreference):
    help_text = "Only show scores for the top X speakers in the public tab (set to 0 to show all speakers)."
    verbose_name = "Top speakers cutoff"
    section = tab_release
    name = "speaker_tab_limit"
    default = 0


@tournament_preferences_registry.register
class ProsTabReleased(BooleanPreference):
    help_text = "Enables public display of a pro-speakers only tab. Intended for use after the tournament."
    verbose_name = "Release pros tab to public"
    section = tab_release
    name = "pros_tab_released"
    default = False


@tournament_preferences_registry.register
class ProsTabReleaseLimit(IntegerPreference):
    help_text = "Only show scores for the top X pro speakers in the public tab (set to 0 to show all pro speakers)."
    verbose_name = "Top pros cutoff"
    section = tab_release
    name = "pros_tab_limit"
    default = 0


@tournament_preferences_registry.register
class NovicesTabReleased(BooleanPreference):
    help_text = "Enables public display of a novice-speakers only tab. Intended for use after the tournament."
    verbose_name = "Release novices tab to public"
    section = tab_release
    name = "novices_tab_released"
    default = False


@tournament_preferences_registry.register
class NovicesTabReleaseLimit(IntegerPreference):
    help_text = "Only show scores for the top X novices in the public tab (set to 0 to show all novices)."
    verbose_name = "Top novices cutoff"
    section = tab_release
    name = "novices_tab_limit"
    default = 0


@tournament_preferences_registry.register
class RepliesTabReleased(BooleanPreference):
    help_text = "Enables public display of the replies tab. Intended for use after the tournament."
    verbose_name = "Release replies tab to public"
    section = tab_release
    name = "replies_tab_released"
    default = False


@tournament_preferences_registry.register
class RepliesTabReleaseLimit(IntegerPreference):
    help_text = "Only show scores for the top X repliers in the public tab (set to 0 to show all repliers)."
    verbose_name = "Top replies cutoff"
    section = tab_release
    name = "replies_tab_limit"
    default = 0


@tournament_preferences_registry.register
class MotionTabReleased(BooleanPreference):
    help_text = ("Enables public display of all motions and win/loss/selection information. "
        "This includes all motions — whether they have been marked as released or not. "
        "Intended for use after the tournament.")
    verbose_name = "Release motions tab to public"
    section = tab_release
    name = "motion_tab_released"
    default = False


@tournament_preferences_registry.register
class BallotsReleased(BooleanPreference):
    help_text = "Enables public display of every adjudicator's ballot. Intended for use after the tournament."
    verbose_name = "Release ballots to public"
    section = tab_release
    name = "ballots_released"
    default = False


@tournament_preferences_registry.register
class AllResultsReleased(BooleanPreference):
    help_text = "This releases all the results for all rounds (including silent and break rounds). Do so only after the tournament is finished!"
    verbose_name = "Release all round results to public"
    section = tab_release
    name = "all_results_released"
    default = False


# ==============================================================================
data_entry = Section('data_entry')
# ==============================================================================


@tournament_preferences_registry.register
class PublicBallots(BooleanPreference):
    help_text = "Enables public interface to add ballots using normal URLs"
    verbose_name = "Enable public ballots with normal URLs"
    section = data_entry
    name = "public_ballots"
    default = False


@tournament_preferences_registry.register
class PublicBallotsRandomised(BooleanPreference):
    help_text = "Enables public interface to add ballots using randomised URLs"
    verbose_name = "Enable public ballots with randomised URLs"
    section = data_entry
    name = "public_ballots_randomised"
    default = False


@tournament_preferences_registry.register
class PublicFeedback(BooleanPreference):
    help_text = "Enables public interface to add feedback using normal URLs"
    verbose_name = "Enable public feedback with normal URLs"
    section = data_entry
    name = "public_feedback"
    default = False


@tournament_preferences_registry.register
class PublicFeedbackRandomised(BooleanPreference):
    help_text = "Enables public interface to add feedback using randomised URLs"
    verbose_name = "Enable public feedback with randomised URLs"
    section = data_entry
    name = "public_feedback_randomised"
    default = False


@tournament_preferences_registry.register
class PublicUsePassword(BooleanPreference):
    help_text = "If checked, users must enter a password when submitting public feedback and ballots"
    verbose_name = "Require password for submission"
    section = data_entry
    name = "public_use_password"
    default = False


@tournament_preferences_registry.register
class PublicPassword(StringPreference):
    help_text = "Value of the password required for public submissions, if passwords are required"
    verbose_name = "Password for public submission"
    section = data_entry
    name = "public_password"
    default = 'Enter Password'


@tournament_preferences_registry.register
class DisableBallotConfirmation(BooleanPreference):
    help_text = "Bypasses double checking by setting ballots to be automatically confirmed"
    verbose_name = "Bypass double checking"
    section = data_entry
    name = "disable_ballot_confirms"
    default = False


@tournament_preferences_registry.register
class EnableMotions(BooleanPreference):
    help_text = "If checked, ballots require a motion to be entered"
    verbose_name = "Enable motions"
    section = data_entry
    name = "enable_motions"
    default = True

# ==============================================================================
public_features = Section('public_features')
# ==============================================================================


@tournament_preferences_registry.register
class PublicParticipants(BooleanPreference):
    help_text = "Enables the public page listing all participants in the tournament"
    verbose_name = "Enable public view of participants list"
    section = public_features
    name = "public_participants"
    default = False


@tournament_preferences_registry.register
class PublicDiversity(BooleanPreference):
    help_text = "Enables the public page listing diversity statistics"
    verbose_name = "Enable public view of diversity info"
    section = public_features
    name = "public_diversity"
    default = False


@tournament_preferences_registry.register
class PublicBreakCategories(BooleanPreference):
    help_text = "If the participants list is enabled, displays break category eligibility on that page"
    verbose_name = "Show break categories on participants page"
    section = public_features
    name = "public_break_categories"
    default = False


@tournament_preferences_registry.register
class PublicSideAllocations(BooleanPreference):
    help_text = "Enables the public page listing pre-allocated sides"
    verbose_name = "Show pre-allocated sides to public"
    section = public_features
    name = "public_side_allocations"
    default = False


@tournament_preferences_registry.register
class PublicDraw(BooleanPreference):
    help_text = "Enables the public page showing released draws"
    verbose_name = "Enable public view of draw"
    section = public_features
    name = "public_draw"
    default = False


@tournament_preferences_registry.register
class PublicResults(BooleanPreference):
    help_text = "Enables the public page showing results of non-silent rounds"
    verbose_name = "Enable public view of results"
    section = public_features
    name = "public_results"
    default = False


@tournament_preferences_registry.register
class PublicMotions(BooleanPreference):
    help_text = "Enables the public page showing motions that have been explicitly released to the public"
    verbose_name = "Enable public view of motions"
    section = public_features
    name = "public_motions"
    default = False


@tournament_preferences_registry.register
class PublicTeamStandings(BooleanPreference):
    help_text = "Enables the public page showing team standings, showing wins only (not speaker scores or ranking)"
    verbose_name = "Enable public view of team standings"
    section = public_features
    name = "public_team_standings"
    default = False


@tournament_preferences_registry.register
class PublicRecordPages(BooleanPreference):
    help_text = "Enables the public page for each team and adjudicator showing their records"
    verbose_name = "Enable public record pages"
    section = public_features
    name = "public_record"
    default = True


@tournament_preferences_registry.register
class PublicBreakingTeams(BooleanPreference):
    help_text = "Enables the public page showing the team breaks. Intended for use after the break announcement."
    verbose_name = "Release team breaks to public"
    section = public_features
    name = "public_breaking_teams"
    default = False


@tournament_preferences_registry.register
class PublicBreakingAdjs(BooleanPreference):
    help_text = "Enables the public page showing breaking adjudicators. Intended for use after the break announcement."
    verbose_name = "Release adjudicators break to public"
    section = public_features
    name = "public_breaking_adjs"
    default = False


@tournament_preferences_registry.register
class FeedbackProgress(BooleanPreference):
    help_text = "Enables the public page detailing who has unsubmitted feedback"
    verbose_name = "Enable public view of unsubmitted feedback"
    section = public_features
    name = 'feedback_progress'
    default = False


@tournament_preferences_registry.register
class AssistantDisplayMotions(BooleanPreference):
    help_text = "Allows assistant users to see the page for displaying motions"
    verbose_name = "Enable assistant view of motion display"
    section = public_features
    name = 'assistant_display_motions'
    default = True

# ==============================================================================
ui_options = Section('ui_options')
# ==============================================================================


@tournament_preferences_registry.register
class ShowSplittingAdjudicators(BooleanPreference):
    help_text = "If showing results to public, show splitting adjudicators in them"
    verbose_name = 'Show splitting adjudicators'
    name = 'show_splitting_adjudicators'
    section = ui_options
    default = False


@tournament_preferences_registry.register
class ShowMotionsInResults(BooleanPreference):
    help_text = "If showing results to public, show which motions were selected in the record"
    verbose_name = 'Show motions in results'
    section = ui_options
    name = 'show_motions_in_results'
    default = False


@tournament_preferences_registry.register
class ShowEmoji(BooleanPreference):
    help_text = "Enables emoji in the draw"
    verbose_name = 'Show emoji'
    section = ui_options
    name = 'show_emoji'
    default = True


@tournament_preferences_registry.register
class ShowTeamInstitutions(BooleanPreference):
    help_text = "In tables listing teams, adds a column showing their institutions"
    verbose_name = 'Show team institutions'
    section = ui_options
    name = 'show_team_institutions'
    default = True


@tournament_preferences_registry.register
class ShowAdjudicatorInstitutions(BooleanPreference):
    help_text = "In tables listing adjudicators, adds a column showing their institutions"
    verbose_name = 'Show adjudicator institutions'
    section = ui_options
    name = 'show_adjudicator_institutions'
    default = True


@tournament_preferences_registry.register
class ShowNovices(BooleanPreference):
    help_text = "Indicates next to a speaker's name if they are a novice"
    verbose_name = 'Show novices'
    section = ui_options
    name = 'show_novices'
    default = False


@tournament_preferences_registry.register
class ShowSpeakersInDraw(BooleanPreference):
    help_text = "Enables a hover element on every team's name showing that team's speakers"
    verbose_name = 'Show speakers in draw'
    section = ui_options
    name = 'show_speakers_in_draw'
    default = True


@tournament_preferences_registry.register
class ShowAllDraws(BooleanPreference):
    help_text = "If showing draws to public, show all (past and future) released draws"
    verbose_name = 'Show all draws'
    section = ui_options
    name = 'show_all_draws'
    default = False


@tournament_preferences_registry.register
class PublicMotionsOrder(ChoicePreference):
    help_text = "Order in which are listed by round in the public view"
    verbose_name = "Order to display motions"
    section = ui_options
    name = "public_motions_order"
    choices = (
        ('forward', 'Earliest round first'),
        ('reverse', 'Latest round first'),
    )
    default = 'reverse'

# ==============================================================================
league_options = Section('league_options')
# ==============================================================================


@tournament_preferences_registry.register
class PublicDivisions(BooleanPreference):
    help_text = "Enables public interface to see divisions"
    verbose_name = "Show divisions to public"
    section = league_options
    name = "public_divisions"
    default = False


@tournament_preferences_registry.register
class EnableDivisions(BooleanPreference):
    help_text = "Enables the sorting and display of teams into divisions"
    verbose_name = "Enable divisions"
    section = league_options
    name = "enable_divisions"
    default = False


@tournament_preferences_registry.register
class EnablePostponements(BooleanPreference):
    help_text = "Enables debates to have their status set to postponed"
    verbose_name = "Enable postponements"
    section = league_options
    name = "enable_postponements"
    default = False


@tournament_preferences_registry.register
class EnableForfeits(BooleanPreference):
    help_text = "Allows debates to be marked as wins by forfeit"
    verbose_name = "Enable forfeits"
    section = league_options
    name = "enable_forfeits"
    default = False


@tournament_preferences_registry.register
class EnableDivisionMotions(BooleanPreference):
    help_text = "Enables assigning motions to a division"
    verbose_name = "Enable division motions"
    section = league_options
    name = "enable_division_motions"
    default = False


@tournament_preferences_registry.register
class MinimumDivisionSize(IntegerPreference):
    help_text = "Smallest allowed size for a division"
    verbose_name = "Minimum division size"
    section = league_options
    name = "minimum_division_size"
    default = 5


@tournament_preferences_registry.register
class IdealDivisionSize(IntegerPreference):
    help_text = "Ideal size for a division"
    verbose_name = "Ideal division size"
    section = league_options
    name = "ideal_division_size"
    default = 6


@tournament_preferences_registry.register
class MaximumDivisionSize(IntegerPreference):
    help_text = "Largest allowed size for a division"
    verbose_name = "Maximum division size"
    section = league_options
    name = "maximum_division_size"
    default = 8


@tournament_preferences_registry.register
class EnableFlaggedMotions(BooleanPreference):
    help_text = "Allow particular motions to be flagged as contentious"
    verbose_name = "Enable flagged motions"
    section = league_options
    name = "enable_flagged_motions"
    default = False


@tournament_preferences_registry.register
class EnableAdjNotes(BooleanPreference):
    help_text = "Enables a general-purpose notes field for adjudicators"
    verbose_name = "Enable adjudicator notes"
    section = league_options
    name = "enable_adj_notes"
    default = False


@tournament_preferences_registry.register
class EnableVenueTimes(BooleanPreference):
    help_text = "Enables specific dates and times to be set for debates"
    verbose_name = "Enable debate scheduling"
    section = league_options
    name = "enable_debate_scheduling"
    default = False


@tournament_preferences_registry.register
class ShareAdjs(BooleanPreference):
    help_text = 'Use shared adjudicators (those without a set tournament) in this tournament'
    verbose_name = "Share adjudicators"
    section = league_options
    name = "share_adjs"
    default = False


@tournament_preferences_registry.register
class ShareVenues(BooleanPreference):
    help_text = 'Use shared venues (those without a set tournament) in this tournament'
    verbose_name = "Share venues"
    section = league_options
    name = "share_venues"
    default = False


@tournament_preferences_registry.register
class DuplicateAdjs(BooleanPreference):
    help_text = "If unchecked, adjudicators can only be given one room per round"
    verbose_name = "Allow adjudicators to be allocated to multiple rooms"
    section = league_options
    name = "duplicate_adjs"
    default = False


@tournament_preferences_registry.register
class AdjAllocationConfirmations(BooleanPreference):
    help_text = 'Allow links to be sent to adjudicators that allow them to confirm shifts'
    verbose_name = "Adjudicator allocation confirmations"
    section = league_options
    name = "allocation_confirmations"
    default = False


@tournament_preferences_registry.register
class EnableCrossTournamentDrawPages(BooleanPreference):
    help_text = "Enables pages that show draws across tournaments (ie by institution)"
    verbose_name = "Public cross draw pages"
    section = league_options
    name = "enable_mass_draws"
    default = False
