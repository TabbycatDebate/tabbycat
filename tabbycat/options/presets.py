
class PreferencesPreset:
    def __init__(self):
        self.show_in_list                               = False


class AustralsPreferences(PreferencesPreset):
    """ 3 vs 3 with replies, chosen motions, intermediary bubbles and 1up/1down. Compliant to AIDA rules. """
    def __init__(self):
        self.name                                       = "Australs Rules"
        self.show_in_list                               = True
        # Scoring
        self.scoring__score_min                         = 68.0
        self.scoring__score_max                         = 82.0
        self.scoring__score_step                        = 1.0
        self.scoring__reply_score_min                   = 34.0
        self.scoring__reply_score_max                   = 41.0
        self.scoring__reply_score_step                  = 0.5
        self.scoring__maximum_margin                    = 15.0  # TODO= check this
        # Draws
        self.draw_rules__avoid_same_institution         = True
        self.draw_rules__avoid_team_history             = True
        self.draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
        self.draw_rules__draw_side_allocations          = 'balance'
        self.draw_rules__draw_pairing_method            = 'slide'
        self.draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
        # Debate Rules
        self.debate_rules__substantive_speakers         = 3
        self.debate_rules__reply_scores_enabled         = True
        self.debate_rules__motion_vetoes_enabled        = True
        self.data_entry__enable_motions                 = True
        # Standings Rules
        self.standings__standings_missed_debates        = 2  # TODO= check this
        self.standings__team_standings_precedence       = ['wins', 'speaks_sum']
        self.standings__rank_speakers_by                = 'total'


class AustralianEastersPreferences(AustralsPreferences):
    """ 3 vs 3 without replies, with set motions, novices, intermediary bubbles and 1up/1down. Compliant to AIDA rules. """
    def __init__(self):
        self.name                                       = "Australian Easters Rules"
        self.show_in_list                               = True
        self.scoring__score_min                         = 70.0
        self.scoring__score_max                         = 80.0
        self.scoring__maximum_margin                    = 15.0
        # Debate Rules
        self.debate_rules__reply_scores_enabled         = False
        self.debate_rules__motion_vetoes_enabled        = True
        self.data_entry__enable_motions                 = True
        # UI Options
        self.ui_options__show_novices                   = True


class NZEastersPreferences(AustralsPreferences):
    """ 2 vs 2 with replies, chosen motions, chosen sides, and novice statuses."""
    def __init__(self):
        self.name                                       = "New Zealand Easters Rules"
        self.show_in_list                               = True
        # Scoring
        self.scoring__score_min                         = 60.0
        self.scoring__score_max                         = 80.0
        self.scoring__reply_score_min                   = 30.0
        self.scoring__reply_score_max                   = 40.0
        # Debate Rules
        self.debate_rules__reply_scores_enabled         = True
        self.debate_rules__motion_vetoes_enabled        = True
        self.data_entry__enable_motions                 = True
        self.debate_rules__substantive_speakers         = 2
        # Standings
        self.standings__team_standings_precedence       = ['wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw']
        # Draw Rules
        self.draw_rules__draw_side_allocations          = 'manual-ballot'
        self.draw_rules__draw_odd_bracket               = 'intermediate'
        self.draw_rules__draw_pairing_method            = 'fold'
        self.draw_rules__draw_avoid_conflicts           = 'off'
        self.draw_rules__avoid_same_institution         = False  # TODO: CHECK
        self.draw_rules__avoid_team_history             = False  # TODO: CHECK
        # UI Options
        self.ui_options__show_novices                   = True


class JoyntPreferences(AustralsPreferences):
    """ 3 vs 3 with replies, set sides, publicly displayed sides and motions, and novice statuses."""
    def __init__(self):
        self.name                                       = "Joynt Scroll Rules"
        self.show_in_list                               = True
        # Scoring
        self.scoring__score_min                         = 60.0
        self.scoring__score_max                         = 80.0
        self.scoring__reply_score_min                   = 30.0
        self.scoring__reply_score_max                   = 40.0
        # Debate Rules
        self.debate_rules__reply_scores_enabled         = True
        self.debate_rules__motion_vetoes_enabled        = False
        self.data_entry__enable_motions                 = False
        self.debate_rules__substantive_speakers         = 3
        # Draw Rules
        self.draw_rules__draw_side_allocations          = 'preallocated'
        self.draw_rules__draw_odd_bracket               = 'intermediate2'
        self.draw_rules__draw_pairing_method            = 'fold'
        self.draw_rules__draw_avoid_conflicts           = 'off'
        self.draw_rules__avoid_same_institution         = False
        self.draw_rules__avoid_team_history             = False
        # Standings
        self.standings__team_standings_precedence       = ['wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw']
        # Public Features
        self.public_features__public_side_allocations   = True
        # UI Options
        self.ui_options__show_novices                   = True


class UADCPreferences(AustralsPreferences):
    """ 3 vs 3 with replies, chosen motions, and all adjudicators can receive feedback from teams."""
    def __init__(self):
        self.name                                       = "UADC Rules"
        self.show_in_list                               = True
        # Rules source = http://www.alcheringa.in/pdrules.pdf
        # Scoring
        self.scoring__score_min                         = 69.0  # From Rules Book
        self.scoring__score_max                         = 81.0  # From Rules Book
        self.scoring__score_step                        = 1.0
        self.scoring__reply_score_min                   = 34.5  # Not specified; assuming half of substantive
        self.scoring__reply_score_max                   = 42.0  # Not specified; assuming  half of substantive
        self.scoring__reply_score_step                  = 0.5
        self.scoring__maximum_margin                    = 0.0   # TODO= check this
        self.scoring__margin_includes_dissenters        = True  # From Rules:10.9.5
        # Draws
        self.draw_rules__avoid_same_institution         = False
        self.draw_rules__avoid_team_history             = True
        self.draw_rules__draw_odd_bracket               = 'pullup_top'  # From Rules 10.3.1
        self.draw_rules__draw_side_allocations          = 'balance'  # From Rules 10.6
        self.draw_rules__draw_pairing_method            = 'slide'  # From rules 10.5
        self.draw_rules__draw_avoid_conflicts           = 'one_up_one_down'  # From rules 10.6.4
        # Debate Rules
        self.debate_rules__substantive_speakers         = 3
        self.debate_rules__reply_scores_enabled         = True
        self.debate_rules__motion_vetoes_enabled        = True
        # Standings Rules
        # self.standings__team_standings_precedence     = 'australs' # TODO: need a new standings rule
        self.standings__team_standings_precedence       = ['wins', 'speaks_sum', 'margin_avg']
        # Feedback
        self.feedback__adj_min_score                    = 1.0  # Explicit in the rules
        self.feedback__adj_max_score                    = 10.0  # Explicit in the rules
        self.feedback__feedback_from_teams              = 'all-adjs' # Kinda a big deal
        # UI Options
        self.public_features__feedback_progress         = True  # Feedback is compulsory


class WSDCPreferences(AustralsPreferences):
    """ 3 vs 3 with replies, chosen motions, and all adjudicators can receive feedback from teams."""
    def __init__(self):
        self.name                                       = "WSDC Rules"
        self.show_in_list                               = True
        # Rules source = http://mkf2v40tlr04cjqkt2dtlqbr.wpengine.netdna-cdn.com/wp-content/uploads/2014/05/WSDC-Debate-Rules-U-2015.pdf
        # Score (strictly specified in the rules)
        self.scoring__score_min                         = 60.0
        self.scoring__score_max                         = 80.0
        self.scoring__score_step                        = 1.0
        self.scoring__reply_score_min                   = 30.0
        self.scoring__reply_score_max                   = 40.0
        self.scoring__reply_score_step                  = 0.5
        # Data
        self.data_entry__enable_motions                 = False # Single motions per round
        # Debates
        self.debate_rules__motion_vetoes_enabled        = False # Single motions per round
        # Draws (exact mechanism is up to the host)
        self.draw_rules__avoid_same_institution         = False
        # Standings
        self.standings__team_standings_precedence       = ['wins', 'num_adjs', 'speaks_avg']
        # UI Options
        self.ui_options__show_institutions              = False


class WADLPreferences(PreferencesPreset):
    """ Example high school league setup. Many features not supported in conjunction with other settings."""
    def __init__(self):
        self.name                                       = "WADL Options"
        self.show_in_list                               = True
        # Debate Rules= no replies; singular motions
        self.debate_rules__substantive_speakers         = 3
        self.debate_rules__reply_scores_enabled         = False
        self.debate_rules__motion_vetoes_enabled        = False
        self.data_entry__enable_motions                 = False
        # Standings Rules
        self.standings__standings_missed_debates        = 0
        self.standings__team_standings_precedence       = ['points210', 'wbwd', 'margin_avg', 'speaks_avg']
        self.standings__rank_speakers_by                = 'average'
        # Draws
        self.draw_rules__avoid_same_institution         = False
        self.draw_rules__avoid_team_history             = False
        self.draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
        self.draw_rules__draw_side_allocations          = 'balance'
        self.draw_rules__draw_pairing_method            = 'slide'
        self.draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
        # UI Options
        self.ui_options__show_novices                   = True
        self.ui_options__show_emoji                     = False
        self.ui_options__show_institutions              = False
        self.ui_options__show_speakers_in_draw          = False
        self.ui_options__public_motions_order           = 'reverse'
        self.ui_options__show_all_draws                 = True
        self.public_features__public_draw               = True
        self.public_features__public_results            = True
        self.public_features__public_motions            = True
        self.public_features__public_record             = False
        # League Options
        self.league_options__enable_flagged_motions     = True
        self.league_options__enable_adj_notes           = True
        self.league_options__enable_venue_groups        = True
        self.league_options__enable_debate_scheduling   = True
        self.league_options__enable_venue_overlaps      = True
        self.league_options__share_adjs                 = True
        self.league_options__share_venues               = True
        self.league_options__duplicate_adjs             = True
        self.league_options__public_divisions           = True
        self.league_options__enable_divisions           = True
        self.league_options__enable_postponements       = True
        self.league_options__enable_forfeits            = True
        self.league_options__enable_division_motions    = True
        self.league_options__allocation_confirmations   = True
        self.league_options__enable_mass_draws          = True


class PublicInformation(PreferencesPreset):
    """ For tournaments hosted online: this sets it up so that people can access the draw and other information via the tab site."""
    def __init__(self):
        self.name                                       = "Public Information Options"
        self.show_in_list                               = True
        self.public_features__public_draw               = True
        self.public_features__public_break_categories   = True
        self.public_features__public_results            = True
        self.public_features__public_motions            = True
        self.public_features__public_team_standings     = True
        self.public_features__public_breaking_teams     = True
        self.public_features__public_breaking_adjs      = True
