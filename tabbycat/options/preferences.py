from django.core.validators import MinValueValidator, validate_slug
from django.forms import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django_summernote.widgets import SummernoteWidget
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import BooleanPreference, ChoicePreference, FloatPreference, IntegerPreference, LongStringPreference, StringPreference

from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator
from tournaments.utils import get_side_name_choices

from .models import tournament_preferences_registry
from .types import MultiValueChoicePreference


# ==============================================================================
scoring = Section('scoring', verbose_name=_("Score Rules"))
# ==============================================================================


@tournament_preferences_registry.register
class MinimumSpeakerScore(FloatPreference):
    help_text = _("Minimum allowed score for substantive speeches")
    section = scoring
    name = 'score_min'
    verbose_name = _("Minimum speaker score")
    default = 68.0


@tournament_preferences_registry.register
class MaximumSpeakerScore(FloatPreference):
    verbose_name = _("Maximum speaker score")
    help_text = _("Maximum allowed score for substantive speeches")
    section = scoring
    name = 'score_max'
    default = 82.0


@tournament_preferences_registry.register
class SpeakerScoreStep(FloatPreference):
    verbose_name = _("Speaker score step")
    help_text = _("Score steps allowed for substantive speeches, e.g. full points (1) or half points (0.5)")
    section = scoring
    name = 'score_step'
    default = 1.0


@tournament_preferences_registry.register
class MaximumMargin(FloatPreference):
    help_text = _("The largest amount by which one team can beat another (0 means no limit)")
    verbose_name = _("Maximum margin")
    section = scoring
    name = 'maximum_margin'
    default = 0.0
    field_kwargs = {'validators': [MinValueValidator(0.0)]}


@tournament_preferences_registry.register
class MinimumReplyScore(FloatPreference):
    help_text = _("Minimum allowed score for reply speeches")
    verbose_name = _("Minimum reply score")
    section = scoring
    name = 'reply_score_min'
    default = 34.0


@tournament_preferences_registry.register
class MaximumReplyScore(FloatPreference):
    help_text = _("Maximum allowed score for reply speeches")
    verbose_name = _("Maximum reply score")
    section = scoring
    name = 'reply_score_max'
    default = 41.0


@tournament_preferences_registry.register
class ReplyScoreStep(FloatPreference):
    help_text = _("Score steps allowed for reply speeches, e.g. full points (1) or half points (0.5)")
    verbose_name = _("Reply score step")
    section = scoring
    name = 'reply_score_step'
    default = 0.5


@tournament_preferences_registry.register
class MarginIncludesDissent(BooleanPreference):
    help_text = _("If checked, a team's winning margin includes dissenting adjudicators")
    verbose_name = _("Margin includes dissenters")
    section = scoring
    name = 'margin_includes_dissenters'
    default = False


# ==============================================================================
draw_rules = Section('draw_rules', verbose_name=_("Draw Rules"))
# ==============================================================================


@tournament_preferences_registry.register
class VotingScore(FloatPreference):
    help_text = _("The auto-allocator will only take adjudicators at or above this score as voting panellists")
    verbose_name = _("Minimum adjudicator score to vote")
    section = draw_rules
    name = 'adj_min_voting_score'
    default = 1.5


@tournament_preferences_registry.register
class AdjConflictPenalty(IntegerPreference):
    help_text = _("Penalty applied by adjudicator auto-allocator for conflicts")
    verbose_name = _("Adjudicator conflict penalty")
    section = draw_rules
    name = 'adj_conflict_penalty'
    default = 1000000


@tournament_preferences_registry.register
class AdjHistoryPenalty(IntegerPreference):
    help_text = _("Penalty applied by adjudicator auto-allocator for history")
    verbose_name = _("Adjudicator history penalty")
    section = draw_rules
    name = 'adj_history_penalty'
    default = 10000


@tournament_preferences_registry.register
class PreformedPanelMismatchPenalty(IntegerPreference):
    help_text = _("Penality applied by preformed panel auto-allocator for priority mismatch")
    verbose_name = _("Importance mismatch penalty")
    section = draw_rules
    name = 'preformed_panel_mismatch_penalty'
    default = 10000000


@tournament_preferences_registry.register
class TeamInstitutionPenalty(IntegerPreference):
    help_text = _("Penalty applied by conflict avoidance method for teams seeing their own institution")
    verbose_name = _("Team institution penalty")
    section = draw_rules
    name = 'team_institution_penalty'
    default = 1


@tournament_preferences_registry.register
class TeamHistoryPenalty(IntegerPreference):
    help_text = _("Penalty applied by conflict avoidance method for teams seeing each other twice or more")
    verbose_name = _("Team history penalty")
    section = draw_rules
    name = 'team_history_penalty'
    default = 1000


@tournament_preferences_registry.register
class AvoidSameInstitution(BooleanPreference):
    help_text = _("If checked, the draw will try to avoid pairing teams against their own institution")
    verbose_name = _("Avoid same institution")
    section = draw_rules
    name = 'avoid_same_institution'
    default = True


@tournament_preferences_registry.register
class AvoidTeamHistory(BooleanPreference):
    help_text = _("If checked, the draw will try to avoid having teams see each other twice")
    verbose_name = _("Avoid team history")
    section = draw_rules
    name = 'avoid_team_history'
    default = True


@tournament_preferences_registry.register
class DrawOddBracket(ChoicePreference):
    help_text = _("How odd brackets are resolved (see documentation for further details)")
    verbose_name = _("Odd bracket resolution method")
    section = draw_rules
    name = 'draw_odd_bracket'
    choices = (
        ('pullup_top', _("Pull up from top")),
        ('pullup_bottom', _("Pull up from bottom")),
        ('pullup_middle', _("Pull up from middle")),
        ('pullup_random', _("Pull up at random")),
        ('intermediate', _("Intermediate brackets")),
        ('intermediate_bubble_up_down', _("Intermediate brackets with bubble-up-bubble-down")),
        ('intermediate1', _("Intermediate 1 (pre-allocated sides)")),
        ('intermediate2', _("Intermediate 2 (pre-allocated sides)")),
    )
    default = 'intermediate_bubble_up_down'


@tournament_preferences_registry.register
class DrawSideAllocations(ChoicePreference):
    help_text = _("How affirmative/negative positions are assigned (see documentation for further details)")
    verbose_name = _("Side allocations method")
    section = draw_rules
    name = 'draw_side_allocations'
    choices = (
        ('random', _("Random")),
        ('balance', _("Balance")),
        ('preallocated', _("Pre-allocated")),
        ('manual-ballot', _("Manually enter from ballot")),
    )
    default = 'balance'


@tournament_preferences_registry.register
class DrawPairingMethod(ChoicePreference):
    help_text = _("Slide: 1 vs 6, 2 vs 7, …. Fold: 1 vs 10, 2 vs 9, …. Adjacent: 1 vs 2, 3 vs 4, ….")
    verbose_name = _("Pairing method")
    section = draw_rules
    name = 'draw_pairing_method'
    choices = (
        ('slide', _("Slide")),
        ('fold', _("Fold")),
        ('random', _("Random")),
        ('adjacent', _("Adjacent")),
        ('fold_top_adjacent_rest', _("Fold top, adjacent rest")),
    )
    default = 'slide'


@tournament_preferences_registry.register
class DrawAvoidConflicts(ChoicePreference):
    help_text = _("Method used to try to avoid teams facing each other multiple times or their "
        "own institution (see documentation for further details)")
    verbose_name = _("Conflict avoidance method")
    section = draw_rules
    name = 'draw_avoid_conflicts'
    choices = (
        ('off', _("Off")),
        ('one_up_one_down', _("One-up-one-down")),
    )
    default = 'one_up_one_down'


@tournament_preferences_registry.register
class DrawPullupRestriction(ChoicePreference):
    help_text = _("If using pull-ups, restrict which teams can be pulled up. "
        "Two-team formats only. Has no effect on BP or intermediate brackets.")
    verbose_name = _("Pullup restriction")
    section = draw_rules
    name = 'draw_pullup_restriction'
    choices = (
        ('none', _("No restriction")),
        ('least_to_date', _("Choose from teams who have been pulled up the fewest times so far")),
        ('lowest_ds_wins', _("Choose from teams with the lowest draw strength by wins so far")),
        ('lowest_ds_speaks', _("Choose from teams with the lowest draw strength by speaks so far")),
    )
    default = 'none'


@tournament_preferences_registry.register
class BPPullupDistribution(ChoicePreference):
    help_text = _("In BP, how pullups are distributed. Only \"Anywhere\" is WUDC-compliant.")
    verbose_name = _("BP pullup distribution")
    section = draw_rules
    name = 'bp_pullup_distribution'
    choices = (
        ('anywhere', _("Anywhere in bracket")),
        ('one_room', _("All in the same room (not WUDC-compliant)")),
    )
    default = 'anywhere'


@tournament_preferences_registry.register
class BPPositionCost(ChoicePreference):
    help_text = _("In BP, which position cost function to use (see documentation for details)")
    verbose_name = _("BP position cost")
    section = draw_rules
    name = 'bp_position_cost'
    choices = (
        ('simple', _("Simple")),
        ('entropy', _("Rényi entropy")),
        ('variance', _("Population variance")),
    )
    default = 'entropy'


@tournament_preferences_registry.register
class BPRenyiOrder(FloatPreference):
    help_text = _("Rényi order α, if BP position cost uses Rényi entropy. "
                  "Shannon is α = 1, Hartley is α = 0, collision is α = 2. "
                  "See documentation for details.")
    verbose_name = _("Rényi order (BP)")
    section = draw_rules
    name = 'bp_renyi_order'
    default = 1.0
    field_kwargs = {'validators': [MinValueValidator(0.0)]}


@tournament_preferences_registry.register
class BPPositionCostExponent(FloatPreference):
    help_text = _("The BP position cost is raised to this power; higher exponents "
                  "bias towards resolving fewer large position imbalances over more "
                  "small ones. See documentation for details.")
    verbose_name = _("BP position cost exponent")
    section = draw_rules
    name = 'bp_position_cost_exponent'
    default = 4.0
    field_kwargs = {'validators': [MinValueValidator(0.0)]}


@tournament_preferences_registry.register
class BPAssignmentMethod(ChoicePreference):
    help_text = _("In BP, which method to use to solve the assignment problem. "
                  "Only Hungarian with preshuffling is WUDC-compliant.")
    verbose_name = _("BP assignment method")
    section = draw_rules
    name = 'bp_assignment_method'
    choices = (
        ('hungarian', _("Hungarian algorithm (not WUDC-compliant)")),
        ('hungarian_preshuffled', _("Hungarian algorithm with preshuffling")),
    )
    default = 'hungarian_preshuffled'


@tournament_preferences_registry.register
class SkipAdjCheckins(BooleanPreference):
    help_text = _("Automatically make all adjudicators available for all rounds")
    verbose_name = _("Skip adjudicator check-ins")
    section = draw_rules
    name = 'draw_skip_adj_checkins'
    default = False


@tournament_preferences_registry.register
class HidePanellistPosition(BooleanPreference):
    help_text = _("Hide panellist positions in the UI (and don't allocate them)")
    verbose_name = _("No panellist adjudicators")
    section = draw_rules
    name = 'no_panellist_position'
    default = False


@tournament_preferences_registry.register
class HideTraineePosition(BooleanPreference):
    help_text = _("Hide trainee positions in the UI (and don't allocate them)")
    verbose_name = _("No trainee adjudicators")
    section = draw_rules
    name = 'no_trainee_position'
    default = False


# ==============================================================================
feedback = Section('feedback', verbose_name=_("Feedback"))
# ==============================================================================


@tournament_preferences_registry.register
class MinimumAdjScore(FloatPreference):
    help_text = _("Minimum possible adjudicator score that can be given")
    verbose_name = _("Minimum adjudicator score")
    section = feedback
    name = 'adj_min_score'
    default = 0.0


@tournament_preferences_registry.register
class MaximumAdjScore(FloatPreference):
    help_text = _("Maximum possible adjudicator score that can be given")
    verbose_name = _("Maximum adjudicator score")
    section = feedback
    name = 'adj_max_score'
    default = 5.0


@tournament_preferences_registry.register
class FeedbackPaths(ChoicePreference):
    help_text = _("Used to inform available choices in the feedback forms for adjudicators (both online and printed) and feedback progress")
    verbose_name = _("Allow and expect feedback to be submitted by")
    section = feedback
    name = 'feedback_paths'
    choices = (
        ('minimal', _("Chairs on panellists and trainees")),
        ('with-p-on-c', _("Panellists on chairs, chairs on panellists and trainees")),
        ('all-adjs', _("All adjudicators (including trainees) on each other")),
    )
    default = 'with-p-on-c'


@tournament_preferences_registry.register
class FeedbackFromTeams(ChoicePreference):
    verbose_name = _("Expect feedback to be submitted by teams on")
    help_text = _("Used to inform available choices in the feedback forms for teams (both online and printed) and feedback progress; this option is used by, e.g., UADC")
    section = feedback
    name = 'feedback_from_teams'
    choices = (
        ('orallist', _("Orallist only (voting panellists permitted, with prompts to select orallist)")),
        ('all-adjs', _("All adjudicators in their panels (including trainees)")),
    )
    default = 'orallist'


@tournament_preferences_registry.register
class ShowUnexpectedFeedback(BooleanPreference):
    verbose_name = _("Show unexpected feedback submissions in participants pages")
    help_text = _("Displays unexpected feedback with a question mark symbol; only relevant if public participants and feedback progress are both enabled")
    section = feedback
    name = 'show_unexpected_feedback'
    default = True


@tournament_preferences_registry.register
class ShowUnaccredited(BooleanPreference):
    help_text = _("Show if an adjudicator is a trainee (unaccredited)")
    verbose_name = _("Show unaccredited")
    section = feedback
    name = 'show_unaccredited'
    default = False


@tournament_preferences_registry.register
class FeedbackIntroduction(LongStringPreference):
    help_text = _("Any explanatory text needed to introduce the feedback form")
    verbose_name = _("Feedback introduction/explanation")
    section = feedback
    name = 'feedback_introduction'
    default = ''
    widget = SummernoteWidget(attrs={'height': 150, 'class': 'form-summernote'})
    field_kwargs = {'required': False}


# ==============================================================================
debate_rules = Section('debate_rules', verbose_name=_("Debate Rules"))
# ==============================================================================


@tournament_preferences_registry.register
class TeamsInDebate(ChoicePreference):
    help_text = _("Two-team format (e.g. Australs, WSDC) or British Parliamentary")
    verbose_name = _("Teams in debate")
    section = debate_rules
    name = 'teams_in_debate'
    choices = (
        ('two', _("Two-team format")),
        ('bp', _("British Parliamentary (four teams)")),
    )
    default = 'two'


@tournament_preferences_registry.register
class BallotsPerDebatePreliminary(ChoicePreference):
    help_text = _("Whether panels submit a ballot each or a single ballot for a debate during the preliminary rounds. Note: BP must use one per debate.")
    verbose_name = _("Ballots per debate, preliminary rounds")
    section = debate_rules
    name = 'ballots_per_debate_prelim'
    choices = (
        ('per-adj', _("One ballot per voting adjudicator")),
        ('per-debate', _("Consensus ballot (one ballot per debate)")),
    )
    default = 'per-adj'


@tournament_preferences_registry.register
class BallotsPerDebateElimination(ChoicePreference):
    help_text = _("Whether panels submit a ballot each or a single ballot for a debate during the elimination rounds. Note: BP must use one per debate.")
    verbose_name = _("Ballots per debate, elimination rounds")
    section = debate_rules
    name = 'ballots_per_debate_elim'
    choices = (
        ('per-adj', _("One ballot per voting adjudicator")),
        ('per-debate', _("Consensus ballot (one ballot per debate)")),
    )
    default = 'per-adj'


@tournament_preferences_registry.register
class BallotMustConfirmWinner(ChoicePreference):
    help_text = _("Whether adjudicator(s) must select the winning team in their ballot, and how it should be treated. Note: Not supported in BP.")
    verbose_name = _("Winner Declaration in ballot(s)")
    section = debate_rules
    name = 'winners_in_ballots'
    choices = (
        ('none', _("Do not require separate winner selection")),
        ('high-points', _("Require separate winner selection as a check on correct scores")),
        ('tied-points', _("Require winner selection to break tied-point debates")),
        ('low-points', _("Require winner selection, overriding scores")),
    )
    default = 'none'


@tournament_preferences_registry.register
class BallotUsesScores(ChoicePreference):
    help_text = _("When ballots should ask for speaker scores.")
    verbose_name = _("Require speaker scores")
    section = debate_rules
    name = 'speakers_in_ballots'
    choices = (
        ('always', _("Always require speaker scores")),
        ('prelim', _("Only require speaker scores in preliminary rounds")),
        ('never', _("Never require speaker scores")),
    )
    default = 'always'


@tournament_preferences_registry.register
class SubstantiveSpeakers(IntegerPreference):
    help_text = _("How many substantive speakers on a team")
    verbose_name = _("Substantive speakers")
    section = debate_rules
    name = 'substantive_speakers'
    default = 3


@tournament_preferences_registry.register
class SideNames(ChoicePreference):
    help_text = _("What to call the teams")
    verbose_name = _("Side names")
    section = debate_rules
    name = 'side_names'
    choices = get_side_name_choices()
    default = 'aff-neg'


@tournament_preferences_registry.register
class ReplyScores(BooleanPreference):
    help_text = _("Whether this style features scored reply speeches")
    verbose_name = _("Reply scores")
    section = debate_rules
    name = 'reply_scores_enabled'
    default = True


@tournament_preferences_registry.register
class RequireSubstantiveForReply(BooleanPreference):
    help_text = _("Whether to limit reply speeches to speakers who gave a substantive speech in the debate")
    verbose_name = _("Require reply speaker to have given a substantive speech")
    section = debate_rules
    name = 'require_substantive_for_reply'
    default = True


@tournament_preferences_registry.register
class MotionVetoes(BooleanPreference):
    help_text = _("Enables the motion veto field on ballots, to track veto statistics")
    verbose_name = _("Motion vetoes")
    section = debate_rules
    name = 'motion_vetoes_enabled'
    default = True


# ==============================================================================
standings = Section('standings', verbose_name=_("Standings"))
# ==============================================================================


@tournament_preferences_registry.register
class StandingsMissedDebates(IntegerPreference):
    help_text = _("The number of substantive speeches a speaker can miss and still be on the speaker tab (-1 means no limit)")
    verbose_name = _("Speeches missable for standings eligibility")
    section = standings
    name = 'standings_missed_debates'
    default = -1


@tournament_preferences_registry.register
class StandingsMissedReplies(IntegerPreference):
    help_text = _("The number of reply speeches a speaker can miss and still be on the replies tab (-1 means no limit)")
    verbose_name = _("Replies missable for standings eligibility")
    section = standings
    name = 'standings_missed_replies'
    default = -1


@tournament_preferences_registry.register
class TeamStandingsPrecedence(MultiValueChoicePreference):
    help_text = _("Metrics to use to rank teams (see documentation for further details)")
    verbose_name = _("Team standings precedence")
    section = standings
    name = 'team_standings_precedence'
    choices = TeamStandingsGenerator.get_metric_choices()
    nfields = 8
    allow_empty = True
    default = ['wins', 'speaks_avg']

    def validate(self, value):
        super().validate(value)

        # Check that non-repeatable metrics aren't listed twice
        classes = [TeamStandingsGenerator.metric_annotator_classes[metric] for metric in value]
        duplicates = [c for c in classes if c.repeatable is False and classes.count(c) > 1]
        if duplicates:
            duplicates_str = ", ".join(list(set(force_str(c.name) for c in duplicates)))
            raise ValidationError(_("The following metrics can't be listed twice: "
                    "%(duplicates)s") % {'duplicates': duplicates_str})


@tournament_preferences_registry.register
class TeamStandingsExtraMetrics(MultiValueChoicePreference):
    help_text = _("Metrics to calculate, but not used to rank teams")
    verbose_name = _("Team standings extra metrics")
    section = standings
    name = 'team_standings_extra_metrics'
    choices = TeamStandingsGenerator.get_metric_choices(ranked_only=False)
    nfields = 5
    allow_empty = True
    default = []


@tournament_preferences_registry.register
class SpeakerStandingsPrecedence(MultiValueChoicePreference):
    help_text = _("Metrics to use to rank speakers (see documentation for further details)")
    verbose_name = _("Speaker standings precedence")
    section = standings
    name = 'speaker_standings_precedence'
    choices = SpeakerStandingsGenerator.get_metric_choices()
    nfields = 4
    allow_empty = True
    default = ['average']

    def validate(self, value):
        super().validate(value)

        # Check that non-repeatable metrics aren't listed twice
        classes = [SpeakerStandingsGenerator.metric_annotator_classes[metric] for metric in value]
        duplicates = [c for c in classes if c.repeatable is False and classes.count(c) > 1]
        if duplicates:
            duplicates_str = ", ".join(list(set(force_str(c.name) for c in duplicates)))
            raise ValidationError(_("The following metrics can't be listed twice: "
                    "%(duplicates)s") % {'duplicates': duplicates_str})


@tournament_preferences_registry.register
class SpeakerStandingsExtraMetrics(MultiValueChoicePreference):
    help_text = _("Metrics to calculate, but not used to rank speakers")
    verbose_name = _("Speaker standings extra metrics")
    section = standings
    name = 'speaker_standings_extra_metrics'
    choices = SpeakerStandingsGenerator.get_metric_choices(ranked_only=False)
    nfields = 5
    allow_empty = True
    default = ['stdev', 'count']


# ==============================================================================
tab_release = Section('tab_release', verbose_name=_("Tab Release"))
# ==============================================================================


@tournament_preferences_registry.register
class TeamTabReleased(BooleanPreference):
    help_text = _("Enables public display of the team tab. Intended for use after the tournament.")
    verbose_name = _("Release team tab to public")
    section = tab_release
    name = 'team_tab_released'
    default = False


@tournament_preferences_registry.register
class TeamTabReleaseLimit(IntegerPreference):
    help_text = _("Only show scores for the top X teams in the public tab (set to 0 to show all teams).")
    verbose_name = _("Top teams cutoff")
    section = tab_release
    name = 'team_tab_limit'
    default = 0


@tournament_preferences_registry.register
class SpeakerTabReleased(BooleanPreference):
    help_text = _("Enables public display of the speaker tab. Intended for use after the tournament.")
    verbose_name = _("Release speaker tab to public")
    section = tab_release
    name = 'speaker_tab_released'
    default = False


@tournament_preferences_registry.register
class SpeakerTabReleaseLimit(IntegerPreference):
    help_text = _("Only show scores for the top X speakers in the public tab (set to 0 to show all speakers).")
    verbose_name = _("Top speakers cutoff")
    section = tab_release
    name = 'speaker_tab_limit'
    default = 0


@tournament_preferences_registry.register
class RepliesTabReleased(BooleanPreference):
    help_text = _("Enables public display of the replies tab. Intended for use after the tournament.")
    verbose_name = _("Release replies tab to public")
    section = tab_release
    name = 'replies_tab_released'
    default = False


@tournament_preferences_registry.register
class RepliesTabReleaseLimit(IntegerPreference):
    help_text = _("Only show scores for the top X repliers in the public tab (set to 0 to show all repliers).")
    verbose_name = _("Top replies cutoff")
    section = tab_release
    name = 'replies_tab_limit'
    default = 0


@tournament_preferences_registry.register
class BreakCategoryTabsReleased(BooleanPreference):
    help_text = "Enables public display of tabs for teams in each break category. Intended for use after the tournament."
    verbose_name = "Release break (team) category tabs to public"
    section = tab_release
    name = "break_category_tabs_released"
    default = False


@tournament_preferences_registry.register
class SpeakerCategoryTabsReleased(BooleanPreference):
    help_text = "Enables public display of those speaker category tabs that are marked to be public. Intended for use after the tournament."
    verbose_name = "Release speaker category tabs to public"
    section = tab_release
    name = "speaker_category_tabs_released"
    default = False


@tournament_preferences_registry.register
class MotionTabReleased(BooleanPreference):
    help_text = _("Enables public display of all motions and win/loss/selection information. "
                  "This includes all motions — whether they have been marked as released or not. "
                  "Intended for use after the tournament.")
    verbose_name = _("Release motions tab to public")
    section = tab_release
    name = 'motion_tab_released'
    default = False


@tournament_preferences_registry.register
class AdjudicatorsTabRelease(BooleanPreference):
    help_text = _("Enables public display of the feedback scores of all adjudicators")
    verbose_name = _("Release adjudicator tab to public")
    section = tab_release
    name = 'adjudicators_tab_released'
    default = False


@tournament_preferences_registry.register
class AdjudicatorsTabShows(ChoicePreference):
    help_text = _("What (if released) the adjudicator tab shows")
    verbose_name = _("Adjudicator tab displays")
    section = tab_release
    name = 'adjudicators_tab_shows'
    choices = (
        ('test', _("Only shows base score")),
        ('final', _("Only shows final score")),
        ('all', _("Shows base, final, and per-round scores")),
    )
    default = 'final'


@tournament_preferences_registry.register
class BallotsReleased(BooleanPreference):
    help_text = _("Enables public display of every adjudicator's ballot. Intended for use after the tournament.")
    verbose_name = _("Release ballots to public")
    section = tab_release
    name = 'ballots_released'
    default = False


@tournament_preferences_registry.register
class AllResultsReleased(BooleanPreference):
    help_text = _("This releases all the results for all rounds (including silent and break rounds). Do so only after the tournament is finished!")
    verbose_name = _("Release all round results to public")
    section = tab_release
    name = 'all_results_released'
    default = False


# ==============================================================================
data_entry = Section('data_entry', verbose_name=_("Data Entry"))
# ==============================================================================


@tournament_preferences_registry.register
class ParticipantBallotSubmissions(ChoicePreference):
    help_text = _("Whether adjudicators can submit ballots themselves, and how they do so")
    verbose_name = _("Ballot submissions from adjudicators")
    section = data_entry
    name = 'participant_ballots'
    choices = (
        ('off', _("Disabled (tab staff only)")),
        ('private-urls', _("Use private URLs")),
        ('public', _("Use publicly accessible form")),
    )
    default = 'off'


@tournament_preferences_registry.register
class ParticipantFeedbackSubmissions(ChoicePreference):
    help_text = _("Whether participants can submit feedback themselves, and how they do so")
    verbose_name = _("Feedback submissions from participants")
    section = data_entry
    name = 'participant_feedback'
    choices = (
        ('off', _("Disabled (tab staff only)")),
        ('private-urls', _("Use private URLs")),
        ('public', _("Use publicly accessible form")),
    )
    default = 'off'


@tournament_preferences_registry.register
class PublicUsePassword(BooleanPreference):
    help_text = _("If checked, users must enter a password when submitting public feedback and ballots")
    verbose_name = _("Require password for submission")
    section = data_entry
    name = 'public_use_password'
    default = False


@tournament_preferences_registry.register
class PublicPassword(StringPreference):
    help_text = _("Value of the password required for public submissions, if passwords are required")
    verbose_name = _("Password for public submission")
    section = data_entry
    name = 'public_password'
    default = 'Enter Password'


@tournament_preferences_registry.register
class DisableBallotConfirmation(BooleanPreference):
    help_text = _("Bypasses double checking by setting ballots to be automatically confirmed")
    verbose_name = _("Bypass double checking")
    section = data_entry
    name = 'disable_ballot_confirms'
    default = False


@tournament_preferences_registry.register
class EnableBlindBallotConfirmation(BooleanPreference):
    help_text = _("Requires scores of draft ballots to be re-entered as part of the confirmation stage (to create more stringent check). Only applies to BP formats.")
    verbose_name = _("Enforce blind confirmations")
    section = data_entry
    name = 'enable_blind_checks'
    default = False


@tournament_preferences_registry.register
class EnableMotions(BooleanPreference):
    help_text = _("If checked, ballots require a motion to be selected from a list of options. ")
    verbose_name = _("Enable motion selection")
    section = data_entry
    name = 'enable_motions'
    default = True


@tournament_preferences_registry.register
class AssistantAccess(ChoicePreference):
    help_text = _("Whether assistants can access pages that can reveal matchups "
                  "and motions ahead of public release (these pages are useful for "
                  "displaying draws/motions to the public and for printing ballots).")
    verbose_name = _("Assistant user access")
    section = data_entry
    name = 'assistant_access'
    default = 'all_areas'
    choices = (
        ('all_areas', _("All areas (results entry, draw display, and motions)")),
        ('results_draw', _("Just results entry and draw display")),
        ('results_only', _("Only results entry")),
    )


@tournament_preferences_registry.register
class CheckInParticipantSubmit(BooleanPreference):
    help_text = _("Whether participants can check themselves in/out through their private URL.")
    verbose_name = _("Participant self-checkin")
    section = data_entry
    name = 'public_checkins_submit'
    default = False


@tournament_preferences_registry.register
class CheckInWindowPeople(FloatPreference):
    help_text = _("The amount of time (in hours) before a speaker or adjudicator's check-in event expires")
    section = data_entry
    name = 'checkin_window_people'
    verbose_name = _("Check-In Window (People)")
    default = 12.0


@tournament_preferences_registry.register
class CheckInWindowVenues(FloatPreference):
    help_text = _("The amount of time (in hours) before a room's check-in event expires")
    section = data_entry
    name = 'checkin_window_venues'
    verbose_name = _("Check-In Window (Rooms)")
    default = 2.0


@tournament_preferences_registry.register
class BallotsConfirmDigits(BooleanPreference):
    help_text = _("Whether the printed scoresheets should show the 'circle digits' prompt to help check bad handwriting")
    verbose_name = _("Ballot Digit Checks")
    section = data_entry
    name = 'ballots_confirm_digits'
    default = True


@tournament_preferences_registry.register
class BallotsHideMotions(BooleanPreference):
    help_text = _("Whether the printed scoresheets should hide the text of motions (even if they have been entered and released)")
    verbose_name = _("Ballot Hide Motions")
    section = data_entry
    name = 'ballots_hide_motions'
    default = False


@tournament_preferences_registry.register
class ScoreReturnLocation(StringPreference):
    help_text = _("The location to return scoresheets to, printed on pre-printed ballots. Set to 'TBA' to hide.")
    verbose_name = _("Score return location")
    section = data_entry
    name = 'score_return_location'
    default = 'TBA'


@tournament_preferences_registry.register
class FeedbackReturnLocation(StringPreference):
    help_text = _("The location to return feedback to, printed on pre-printed feedback forms. Set to 'TBA' to hide.")
    verbose_name = _("Feedback return location")
    section = data_entry
    name = 'feedback_return_location'
    default = 'TBA'


@tournament_preferences_registry.register
class EnablePostponements(BooleanPreference):
    help_text = _("Lets debates have their status as postponed, as to not block draw generation.")
    verbose_name = _("Enable postponements")
    section = data_entry
    name = 'enable_postponements'
    default = False


# ==============================================================================
public_features = Section('public_features', verbose_name=_("Public Features"))
# ==============================================================================


@tournament_preferences_registry.register
class PublicParticipants(BooleanPreference):
    help_text = _("Enables the public page listing all participants in the tournament")
    verbose_name = _("Enable public view of participants list")
    section = public_features
    name = 'public_participants'
    default = False


@tournament_preferences_registry.register
class PublicInstitutionsList(BooleanPreference):
    help_text = _("Enables the public page listing all institutions in the tournament")
    verbose_name = _("Enable public view of institutions list")
    section = public_features
    name = 'public_institutions_list'
    default = False


@tournament_preferences_registry.register
class PublicDiversity(BooleanPreference):
    help_text = _("Enables the public page listing diversity statistics")
    verbose_name = _("Enable public view of diversity info")
    section = public_features
    name = 'public_diversity'
    default = False


@tournament_preferences_registry.register
class PublicCheckinStatuses(BooleanPreference):
    help_text = _("Enables the public page showing checkin statuses for "
                  "individuals, institutions, and teams. Note that this page "
                  "can be slow when used at very large tournaments.")
    verbose_name = _("Enable public view of the checkin statuses")
    section = public_features
    name = 'public_checkins'
    default = False


@tournament_preferences_registry.register
class PublicBreakCategories(BooleanPreference):
    help_text = _("If the participants list is enabled, displays break category eligibility on that page")
    verbose_name = _("Show break categories on participants page")
    section = public_features
    name = 'public_break_categories'
    default = False


@tournament_preferences_registry.register
class PublicSideAllocations(BooleanPreference):
    help_text = _("Enables the public page listing pre-allocated sides")
    verbose_name = _("Show pre-allocated sides to public")
    section = public_features
    name = 'public_side_allocations'
    default = False


@tournament_preferences_registry.register
class PublicDraw(ChoicePreference):
    help_text = _("Enables the public page showing released draws")
    verbose_name = _("Enable public view of draw")
    section = public_features
    name = 'public_draw'
    choices = (
        ('off', _("Disabled")),
        ('current', _("Show a single page for the current round's draw")),
        ('all-released', _("Show individual pages for all released draws")),
    )
    default = 'off'


@tournament_preferences_registry.register
class PublicResults(BooleanPreference):
    help_text = _("Enables the public page showing results of non-silent rounds")
    verbose_name = _("Enable public view of results")
    section = public_features
    name = 'public_results'
    default = False


@tournament_preferences_registry.register
class PublicMotions(BooleanPreference):
    help_text = _("Enables the public page showing motions that have been explicitly released to the public")
    verbose_name = _("Enable public view of motions")
    section = public_features
    name = 'public_motions'
    default = False


@tournament_preferences_registry.register
class PublicTeamStandings(BooleanPreference):
    help_text = _("Enables the public page showing team standings, showing wins only (not speaker scores or ranking)")
    verbose_name = _("Enable public view of team standings")
    section = public_features
    name = 'public_team_standings'
    default = False


@tournament_preferences_registry.register
class PublicRecordPages(BooleanPreference):
    help_text = _("Enables the public page for each team and adjudicator showing their records")
    verbose_name = _("Enable public record pages")
    section = public_features
    name = 'public_record'
    default = True


@tournament_preferences_registry.register
class PublicBreakingTeams(BooleanPreference):
    help_text = _("Enables the public page showing the team breaks. Intended for use after the break announcement.")
    verbose_name = _("Release team breaks to public")
    section = public_features
    name = 'public_breaking_teams'
    default = False


@tournament_preferences_registry.register
class PublicBreakingAdjs(BooleanPreference):
    help_text = _("Enables the public page showing breaking adjudicators. Intended for use after the break announcement.")
    verbose_name = _("Release adjudicators break to public")
    section = public_features
    name = 'public_breaking_adjs'
    default = False


@tournament_preferences_registry.register
class FeedbackProgress(BooleanPreference):
    help_text = _("Enables the public page detailing who has unsubmitted feedback")
    verbose_name = _("Enable public view of unsubmitted feedback")
    section = public_features
    name = 'feedback_progress'
    default = False


@tournament_preferences_registry.register
class TournamentStaff(LongStringPreference):
    help_text = _("List of tournament staff, to be displayed on the tournament home page. Leave this blank or with the default text if you want to not show this information.")
    verbose_name = _("Tournament staff")
    section = public_features
    name = 'tournament_staff'
    default = ""
    widget = SummernoteWidget(attrs={'height': 150, 'class': 'form-summernote'})
    field_kwargs = {'required': False}


@tournament_preferences_registry.register
class WelcomeMessage(LongStringPreference):
    help_text = _("Message to be displayed on the tournament home page")
    verbose_name = _("Welcome message")
    section = public_features
    name = 'welcome_message'
    default = ""
    widget = SummernoteWidget(attrs={'height': 150, 'class': 'form-summernote'})
    field_kwargs = {'required': False}


# ==============================================================================
ui_options = Section('ui_options', verbose_name=_("UI Options"))
# ==============================================================================


@tournament_preferences_registry.register
class ShowSplittingAdjudicators(BooleanPreference):
    help_text = _("If showing results to public, show splitting adjudicators in them")
    verbose_name = _("Show splitting adjudicators")
    name = 'show_splitting_adjudicators'
    section = ui_options
    default = False


@tournament_preferences_registry.register
class ShowMotionsInResults(BooleanPreference):
    help_text = _("If showing results to public, show which motions were selected in the record")
    verbose_name = _("Show motions in results")
    section = ui_options
    name = 'show_motions_in_results'
    default = False


@tournament_preferences_registry.register
class TeamCodeNames(ChoicePreference):
    help_text = _("Whether and how to use code names for teams")
    verbose_name = _("Team code names")
    section = ui_options
    name = 'team_code_names'
    default = 'off'
    choices = (
        ('off',                 _("Do not use code names")),
        ('all-tooltips',        _("Use real names everywhere, and show code names in tooltips")),
        ('admin-tooltips-code', _("Use code names for public; real names with code names in "
                                  "tooltips for admins")),
        ('admin-tooltips-real', _("Use code names for public; code names with real names in "
                                  "tooltips for admins")),
        ('everywhere',          _("Use code names everywhere; do not use tooltips (real names show in some admin views)")),
    )


@tournament_preferences_registry.register
class ShowEmoji(BooleanPreference):
    help_text = _("Display team emoji in the public and admin interfaces")
    verbose_name = _("Show emoji")
    section = ui_options
    name = 'show_emoji'
    default = True


@tournament_preferences_registry.register
class ShowTeamInstitutions(BooleanPreference):
    help_text = _("In tables listing teams, adds a column showing their institutions")
    verbose_name = _("Show team institutions")
    section = ui_options
    name = 'show_team_institutions'
    default = True


@tournament_preferences_registry.register
class ShowAdjudicatorInstitutions(BooleanPreference):
    help_text = _("Hide the institutions of adjudicators on public pages and on printed ballots")
    verbose_name = _("Show adjudicator institutions")
    section = ui_options
    name = 'show_adjudicator_institutions'
    default = True


@tournament_preferences_registry.register
class ShowSpeakersInDraw(BooleanPreference):
    help_text = _("Enables a hover element on every team's name showing that team's speakers")
    verbose_name = _("Show speakers in draw")
    section = ui_options
    name = 'show_speakers_in_draw'
    default = True


@tournament_preferences_registry.register
class PublicMotionsOrder(ChoicePreference):
    help_text = _("Order in which are listed by round in the public view")
    verbose_name = _("Order to display motions")
    section = ui_options
    name = 'public_motions_order'
    choices = (
        ('forward', _("Earliest round first")),
        ('reverse', _("Latest round first")),
    )
    default = 'reverse'


# ==============================================================================
email = Section('email', verbose_name=_("Notifications"))
# ==============================================================================


@tournament_preferences_registry.register
class ReplyToEmailName(StringPreference):
    help_text = _("The name of the organizer tasked with managing emails (in case of replies)")
    verbose_name = _("Reply-to name")
    section = email
    name = 'reply_to_name'
    default = "Tabulation Team"


@tournament_preferences_registry.register
class ReplyToEmailAddress(StringPreference):
    help_text = _("The email address for handling replies")
    verbose_name = _("Reply-to address")
    section = email
    name = 'reply_to_address'
    default = ""


@tournament_preferences_registry.register
class EmailWebhookKey(StringPreference):
    help_text = _("A secret key to accept email status events")
    verbose_name = _("Email status secret key")
    section = email
    name = 'email_hook_key'
    default = ""
    required = False
    field_kwargs = {'validators': [validate_slug]}


@tournament_preferences_registry.register
class EnableEmailBallotReceipts(BooleanPreference):
    help_text = _("Enables a copy of adjudicators' ballots to be automatically sent to them (by email) after they are entered in Tabbycat (for confirmation or checking)")
    verbose_name = _("Ballot receipts")
    section = email
    name = 'enable_ballot_receipts'
    default = False


@tournament_preferences_registry.register
class BallotEmailSubjectLine(StringPreference):
    help_text = _("The subject line for emails sent to adjudicators with their submitted ballot. "
                  "Use '{{ DEBATE }}' as a placeholder for the associated debate")
    verbose_name = _("Ballot receipt subject line")
    section = email
    name = 'ballot_email_subject'
    default = "Your ballot for {{ DEBATE }} has been received"


@tournament_preferences_registry.register
class BallotEmailMessageBody(LongStringPreference):
    help_text = _("The message body for emails sent to adjudicators with their submitted ballot.")
    verbose_name = _("Ballot receipt message")
    section = email
    name = 'ballot_email_message'
    default = ("<p>Hi {{ USER }},</p>"
        "<p>Your ballot for {{ DEBATE }} has been successfully received, with these scores:</p>"
        "{{ SCORES }}"
        "<p>If there are any problems, please contact the tab team.</p>")
    widget = SummernoteWidget(attrs={'height': 150, 'class': 'form-summernote'})


# -----
# Email-related but unattached for use in separate inline forms
# -----

@tournament_preferences_registry.register
class PointsEmailSubjectLine(StringPreference):
    help_text = _("The subject line for emails sent to speakers with their team points.")
    verbose_name = _("Team points subject line")
    name = 'team_points_email_subject'
    default = "{{ TEAM }}'s current wins after {{ ROUND }}: {{ POINTS }}"


@tournament_preferences_registry.register
class PointsEmailMessageBody(LongStringPreference):
    help_text = _("The message body for emails sent to speakers with their team points.")
    verbose_name = _("Team points message")
    name = 'team_points_email_message'
    default = ("<p>Hi {{ USER }},</p>"
        "After {{ ROUND }}, your team ({{ TEAM }}) currently has <strong>{{ POINTS }}</strong> wins in the {{ TOURN }}.</p>"
        "<p>Current Standings: <a href='{{ URL }}'>{{ URL }}</a></p>")


@tournament_preferences_registry.register
class AdjudicatorDrawNotificationSubject(StringPreference):
    help_text = _("The subject-line for emails sent to adjudicators with their assignments.")
    verbose_name = _("Adjudicator draw subject line")
    name = 'adj_email_subject'
    default = "Your assigned debate for {{ ROUND }}: {{ VENUE }}"


@tournament_preferences_registry.register
class AdjudicatorDrawNotificationMessage(LongStringPreference):
    help_text = _("The message body for emails sent to adjudicators with their assignments.")
    verbose_name = _("Adjudicator draw message")
    name = 'adj_email_message'
    default = ("<p>Hi {{ USER }},</p>"
        "<p>You have been assigned as <strong>{{ POSITION }}</strong> adjudicator for {{ ROUND }} in <strong>{{ VENUE }}</strong> with the following panel: {{ PANEL }}</p>"
        "<p>The debate is between these teams: {{ DRAW }}</p>")


@tournament_preferences_registry.register
class TeamDrawNotificationSubject(StringPreference):
    help_text = _("The subject-line for emails sent to teams with their draw.")
    verbose_name = _("Team draw subject line")
    name = 'team_draw_email_subject'
    default = "Your assigned debate for {{ ROUND }}: {{ VENUE }}"


@tournament_preferences_registry.register
class TeamDrawNotificationMessage(LongStringPreference):
    help_text = _("The message body for emails sent to participants with their private URLs.")
    verbose_name = _("Private URL notification message")
    name = 'team_draw_email_message'
    default = ("<p>Hi {{ USER }},</p>"
        "<p>You have been assigned as <strong>{{ SIDE }}</strong> for {{ ROUND }} in <strong>{{ VENUE }}</strong> with the following panel: {{ PANEL }}</p>"
        "<p>The debate is between: {{ DRAW }}</p>")


@tournament_preferences_registry.register
class PrivateUrlEmailSubject(StringPreference):
    help_text = _("The subject-line for emails sent to participants with their private URLs.")
    verbose_name = _("Private URL notification subject line")
    name = 'url_email_subject'
    default = "Your personal private URL for {{ TOURN }}"


@tournament_preferences_registry.register
class PrivateUrlEmailMessage(LongStringPreference):
    help_text = _("The message body for emails sent to participants with their private URLs.")
    verbose_name = _("Private URL notification message")
    name = 'url_email_message'
    default = ("<p>Hi {{ USER }},</p>"
        "<p>At {{ TOURN }}, we are using an online tabulation system. You can submit "
        "your ballots and/or feedback at the following URL. This URL is unique to you — do not share it with "
        "anyone, as anyone who knows it can submit forms on your behalf. This URL "
        "will not change throughout this tournament, so we suggest bookmarking it.</p>"
        "<p>Your personal private URL is:<br />"
        "<a href='{{ URL }}'>{{ URL }}</a></p>")


@tournament_preferences_registry.register
class MotionReleaseEmailSubject(StringPreference):
    help_text = _("The subject-line for emails sent to participants on motion release.")
    verbose_name = _("Motion release notification subject line")
    name = 'motion_email_subject'
    default = "Motions for {{ ROUND }}"


@tournament_preferences_registry.register
class MotionReleaseEmailMessage(LongStringPreference):
    help_text = _("The message body for emails sent to participants on motion release.")
    verbose_name = _("Motion release notification message")
    name = 'motion_email_message'
    default = ("<p>The motion(s) for {{ ROUND }} are:</p>"
        "{{ MOTIONS }}")


@tournament_preferences_registry.register
class TeamNameEmailSubject(StringPreference):
    help_text = _("The subject-line for emails sent to participants informing them of their team registration.")
    verbose_name = _("Team registration notification subject line")
    name = 'team_email_subject'
    default = "Registration for {{ SHORT }}"


@tournament_preferences_registry.register
class TeamNameEmailMessage(LongStringPreference):
    help_text = _("The message body for emails sent to participants informing them of their team registration.")
    verbose_name = _("Team registration notification message")
    name = 'team_email_message'
    default = ("<p>Hi {{ USER }},</p>"
        "<p>You are registered as <strong>{{ LONG }}</strong> in {{ TOURN }} with {{ SPEAKERS }}.</p>")


# ==============================================================================
global_settings = Section('global', verbose_name=_('Global Settings'))
# ==============================================================================


@global_preferences_registry.register
class EnableAPIAccess(BooleanPreference):
    help_text = _("Enables external applications to access the site through a dedicated interface, subject to public information settings.")
    verbose_name = _("Enable API access")
    section = global_settings
    name = 'enable_api'
    default = True
