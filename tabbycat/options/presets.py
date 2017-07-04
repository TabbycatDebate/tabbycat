def _all_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from _all_subclasses(subclass)
        yield subclass


def all_presets():
    yield from _all_subclasses(PreferencesPreset)


class PreferencesPreset:
    show_in_list                               = False


class AustralsPreferences(PreferencesPreset):
    name         = "Australs Rules"
    description  = ("3 vs 3 with replies, chosen motions, intermediate bubbles, "
        "one-up-one-down. Compliant with AIDA rules.")
    show_in_list = True

    # Scoring
    scoring__score_min                         = 68.0
    scoring__score_max                         = 82.0
    scoring__score_step                        = 1.0
    scoring__reply_score_min                   = 34.0
    scoring__reply_score_max                   = 41.0
    scoring__reply_score_step                  = 0.5
    scoring__maximum_margin                    = 15.0  # TODO= check this
    # Draws
    draw_rules__avoid_same_institution         = True
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'slide'
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
    # Debate Rules
    debate_rules__teams_in_debate              = 'two'
    debate_rules__ballots_per_debate           = 'per-adj'
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = True
    debate_rules__side_names                   = 'aff-neg'
    data_entry__enable_motions                 = True
    # Standings Rules
    standings__standings_missed_debates        = 2  # TODO= check this
    standings__team_standings_precedence       = ['wins', 'speaks_sum']
    standings__rank_speakers_by                = 'total'
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = True


class AustralianEastersPreferences(AustralsPreferences):
    name         = "Australian Easters Rules"
    show_in_list = True
    description  = ("3 vs 3 without replies, set motions, novices, intermediate "
        "bubbles, one-up-one-down. Compliant with AIDA rules.")

    # Scoring
    scoring__score_min                         = 70.0
    scoring__score_max                         = 80.0
    scoring__maximum_margin                    = 15.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = False
    debate_rules__motion_vetoes_enabled        = True
    data_entry__enable_motions                 = True
    # UI Options
    ui_options__show_novices                   = True


class NZEastersPreferences(AustralsPreferences):
    name         = "New Zealand Easters Rules"
    show_in_list = True
    description  = ("2 vs 2 with replies, chosen motions, chosen sides, and "
        "novice statuses.")

    # Scoring
    scoring__score_min                         = 60.0
    scoring__score_max                         = 80.0
    scoring__reply_score_min                   = 30.0
    scoring__reply_score_max                   = 40.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = True
    data_entry__enable_motions                 = True
    debate_rules__substantive_speakers         = 2
    # Standings
    standings__team_standings_precedence       = ['wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw']
    # Draw Rules
    draw_rules__draw_side_allocations          = 'manual-ballot'
    draw_rules__draw_odd_bracket               = 'intermediate'
    draw_rules__draw_pairing_method            = 'fold'
    draw_rules__draw_avoid_conflicts           = 'off'
    draw_rules__avoid_same_institution         = False  # TODO: CHECK
    draw_rules__avoid_team_history             = False  # TODO: CHECK
    # UI Options
    ui_options__show_novices                   = True


class JoyntPreferences(AustralsPreferences):
    name         = "Joynt Scroll Rules"
    show_in_list = True
    description  = ("3 vs 3 with replies, set sides, publicly displayed sides "
        "and motions, and novice statuses.")

    # Scoring
    scoring__score_min                         = 60.0
    scoring__score_max                         = 80.0
    scoring__reply_score_min                   = 30.0
    scoring__reply_score_max                   = 40.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = False
    data_entry__enable_motions                 = False
    debate_rules__substantive_speakers         = 3
    # Draw Rules
    draw_rules__draw_side_allocations          = 'preallocated'
    draw_rules__draw_odd_bracket               = 'intermediate2'
    draw_rules__draw_pairing_method            = 'fold'
    draw_rules__draw_avoid_conflicts           = 'off'
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = False
    # Standings
    standings__team_standings_precedence       = ['wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw']
    # Public Features
    public_features__public_side_allocations   = True
    # UI Options
    ui_options__show_novices                   = True


class UADCPreferences(AustralsPreferences):
    name         = "UADC Rules"
    show_in_list = True
    description  = ("3 vs 3 with replies, chosen motions, and all adjudicators "
        "can receive feedback from teams.")

    # Rules source = http://www.alcheringa.in/pdrules.pdf
    # Scoring
    scoring__score_min                         = 69.0  # From Rules Book
    scoring__score_max                         = 81.0  # From Rules Book
    scoring__score_step                        = 1.0
    scoring__reply_score_min                   = 34.5  # Not specified; assuming half of substantive
    scoring__reply_score_max                   = 42.0  # Not specified; assuming  half of substantive
    scoring__reply_score_step                  = 0.5
    scoring__maximum_margin                    = 0.0   # TODO= check this
    scoring__margin_includes_dissenters        = True  # From Rules:10.9.5
    # Draws
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'pullup_top'  # From Rules 10.3.1
    draw_rules__draw_side_allocations          = 'balance'  # From Rules 10.6
    draw_rules__draw_pairing_method            = 'slide'  # From rules 10.5
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'  # From rules 10.6.4
    # Debate Rules
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = True
    debate_rules__side_names                   = 'gov-opp'
    # Standings Rules
    standings__team_standings_precedence       = ['wins', 'speaks_sum', 'margin_avg']
    # Feedback
    feedback__adj_min_score                    = 1.0  # Explicit in the rules
    feedback__adj_max_score                    = 10.0  # Explicit in the rules
    feedback__feedback_from_teams              = 'all-adjs' # Kinda a big deal
    # UI Options
    public_features__feedback_progress         = True  # Feedback is compulsory


class WSDCPreferences(AustralsPreferences):
    name         = "WSDC Rules"
    show_in_list = True
    description  = ("3 vs 3 with replies, chosen motions, prop/opp side labels, "
        "and all adjudicators can receive feedback from teams.")

    # Rules source = http://mkf2v40tlr04cjqkt2dtlqbr.wpengine.netdna-cdn.com/wp-content/uploads/2014/05/WSDC-Debate-Rules-U-2015.pdf
    # Score (strictly specified in the rules)
    scoring__score_min                         = 60.0
    scoring__score_max                         = 80.0
    scoring__score_step                        = 1.0
    scoring__reply_score_min                   = 30.0
    scoring__reply_score_max                   = 40.0
    scoring__reply_score_step                  = 0.5
    # Data
    data_entry__enable_motions                 = False # Single motions per round
    # Debates
    debate_rules__motion_vetoes_enabled        = False # Single motions per round
    debate_rules__side_names                   = 'prop-opp'
    # Draws (exact mechanism is up to the host)
    draw_rules__avoid_same_institution         = False
    # Standings
    standings__team_standings_precedence       = ['wins', 'num_adjs', 'speaks_avg']
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = False


class WUDCPreferences(PreferencesPreset):
    name         = "WUDC Rules"
    show_in_list = True
    description  = "British Parliamentary."

    # Scoring
    scoring__score_min                         = 50.0
    scoring__score_max                         = 100.0
    scoring__score_step                        = 1.0
    scoring__maximum_margin                    = 0.0
    # Debate Rules
    debate_rules__teams_in_debate              = 'bp'
    debate_rules__ballots_per_debate           = 'per-debate'
    debate_rules__substantive_speakers         = 2
    debate_rules__reply_scores_enabled         = False
    debate_rules__motion_vetoes_enabled        = False
    debate_rules__side_names                   = 'gov-opp'
    data_entry__enable_motions                 = True
    # Draw Rules
    draw_rules__bp_pullup_distribution         = 'anywhere'
    draw_rules__bp_position_cost               = 'entropy'
    draw_rules__bp_renyi_order                 = 1.0
    draw_rules__bp_position_cost_exponent      = 4.0
    draw_rules__bp_assignment_method           = 'hungarian_preshuffled'
    # Standings Rules
    standings__standings_missed_debates        = 2  # TODO check this?
    standings__team_standings_precedence       = ['points', 'speaks_sum']
    standings__rank_speakers_by                = 'total'
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = True


class WADLPreferences(PreferencesPreset):
    name         = "WADL Options"
    show_in_list = True
    description  = ("Example high school league setup. Many features not "
        "supported in conjunction with other settings.")

    # Debate Rules= no replies; singular motions
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = False
    debate_rules__motion_vetoes_enabled        = False
    data_entry__enable_motions                 = False
    # Standings Rules
    standings__standings_missed_debates        = 0
    standings__team_standings_precedence       = ['points210', 'wbwd', 'margin_avg', 'speaks_avg']
    standings__rank_speakers_by                = 'average'
    # Draws
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = False
    draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'slide'
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
    # UI Options
    ui_options__show_novices                   = True
    ui_options__show_emoji                     = False
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = False
    ui_options__show_speakers_in_draw          = False
    ui_options__public_motions_order           = 'reverse'
    ui_options__show_all_draws                 = True
    public_features__public_draw               = True
    public_features__public_results            = True
    public_features__public_motions            = True
    public_features__public_record             = False
    # League Options
    league_options__enable_flagged_motions     = True
    league_options__enable_adj_notes           = True
    league_options__enable_debate_scheduling   = True
    league_options__share_adjs                 = True
    league_options__share_venues               = True
    league_options__division_venues            = True
    league_options__duplicate_adjs             = True
    league_options__public_divisions           = True
    league_options__enable_divisions           = True
    league_options__enable_postponements       = True
    league_options__enable_forfeits            = True
    league_options__enable_division_motions    = True
    league_options__allocation_confirmations   = True
    league_options__enable_mass_draws          = True


class PublicInformation(PreferencesPreset):
    name         = "Public Information Options"
    show_in_list = True
    description  = ("For tournaments hosted online: this sets it up so that "
        "people can access the draw and other generally useful information "
        "via the tab site.")

    public_features__public_draw               = True
    public_features__public_break_categories   = True
    public_features__public_results            = True
    public_features__public_motions            = True
    public_features__public_team_standings     = True


class TabRelease(PreferencesPreset):
    name         = "Tab Release Options"
    show_in_list = True
    description  = ("For when a tab is ready to be released. This will publicly "
        "display the results of all rounds, the team tab, the speaker tab, etc")

    tab_release__team_tab_released             = True
    tab_release__speaker_tab_released          = True
    tab_release__replies_tab_released          = True
    tab_release__motion_tab_released           = True
    tab_release__ballots_released              = True
    tab_release__all_results_released          = True
    public_features__public_diversity          = True
    public_features__public_results            = True
    public_features__public_breaking_teams     = True
    public_features__public_breaking_adjs      = True
