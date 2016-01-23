
class PreferencesPreset:
    def __init__(self):
        self.show_in_list                             = False

class AustralsPreferences(PreferencesPreset):
    """ 3v3 with replies, chosen motions, intermediary bubbles and 1up/1down. Compliant to AIDA rules """
    def __init__(self):
        self.name                                     = "Australs"
        self.show_in_list                             = True
        # Scoring
        self.scoring__score_min                        = 68.0
        self.scoring__score_max                        = 82.0
        self.scoring__score_step                       = 1.0
        self.scoring__reply_score_min                  = 34.0
        self.scoring__reply_score_max                  = 41.0
        self.scoring__reply_score_step                 = 0.5
        self.scoring__maximum_margin                   = 15.0 # TODO= check this
        # Draws
        self.draw_rules__avoid_same_institution        = True
        self.draw_rules__avoid_team_history            = True
        self.draw_rules__draw_odd_bracket              = 'intermediate_bubble_up_down'
        self.draw_rules__draw_side_allocations         = 'balance'
        self.draw_rules__draw_pairing_method           = 'slide'
        self.draw_rules__draw_avoid_conflicts          = 'one_up_one_down'
        # Debate Rules
        self.debate_rules__substantive_speakers        = 3
        self.debate_rules__reply_scores_enabled        = True
        self.debate_rules__motion_vetoes_enabled       = True
        self.data_entry__enable_motions                = True
        # Standings Rules
        self.standings__standings_missed_debates       = 2 # TODO= check this
        self.standings__team_standings_rule            = 'australs'
        self.standings__speaker_standings_rule         = 'australs'


class AustralianEastersPreferences(AustralsPreferences):
    """ 3v3 without replies, with set motions, novices, intermediary bubbles and 1up/1down. Compliant to AIDA rules """
    def __init__(self):
        self.name                                      = "Australian Easters"
        self.show_in_list                              = True
        self.scoring__score_min                        = 70.0
        self.scoring__score_max                        = 80.0
        self.scoring__maximum_margin                   = 15.0
        # Debate Rules
        self.debate_rules__reply_scores_enabled        = False
        self.debate_rules__motion_vetoes_enabled       = False
        self.data_entry__enable_motions                = False
        # UI Options
        self.ui_options__show_novices                  = True

class NZEastersPreferences(AustralsPreferences):
    """ 2vs2 with replies, chosen motions, chosen sides, novices, and... UNCOMPLETE """
    def __init__(self):
        self.name                                      = "NZ Easters"
        self.show_in_list                              = True
        # Scoring
        self.scoring__score_min                        = 60.0
        self.scoring__score_max                        = 80.0
        self.scoring__reply_score_min                  = 30.0
        self.scoring__reply_score_max                  = 40.0
        # Debate Rules
        self.debate_rules__reply_scores_enabled        = True
        self.debate_rules__motion_vetoes_enabled       = True
        self.data_entry__enable_motions                = True
        self.debate_rules__substantive_speakers        = 2
        # Standings
        self.standings__team_standings_rule            = 'nz'
        # Draw Rules
        self.draw_rules__draw_side_allocations         = 'manual-ballot'
        self.draw_rules__draw_odd_bracket              = 'intermediate'
        self.draw_rules__draw_pairing_method           = 'fold'
        self.draw_rules__draw_avoid_conflicts          = 'off'
        self.draw_rules__avoid_same_institution        = False # TODO: CHECK
        self.draw_rules__avoid_team_history            = False # TODO: CHECK
        # UI Options
        self.ui_options__show_novices                  = True


class JoyntPreferences(AustralsPreferences):
    """ 3vs3 with replies, set sides, publicly displayed sides and motions... UNCOMPLETE """
    def __init__(self):
        self.name                                      = "Joynt Scroll"
        self.show_in_list                              = True
        # Scoring
        self.scoring__score_min                        = 60.0
        self.scoring__score_max                        = 80.0
        self.scoring__reply_score_min                  = 30.0
        self.scoring__reply_score_max                  = 40.0
        # Debate Rules
        self.debate_rules__reply_scores_enabled        = True
        self.debate_rules__motion_vetoes_enabled       = False
        self.data_entry__enable_motions                = False
        self.debate_rules__substantive_speakers        = 3
        # Draw Rules
        self.draw_rules__draw_side_allocations         = 'preallocated'
        self.draw_rules__draw_odd_bracket              = 'intermediate2'
        self.draw_rules__draw_pairing_method           = 'fold'
        self.draw_rules__draw_avoid_conflicts          = 'off'
        self.draw_rules__avoid_same_institution        = False
        self.draw_rules__avoid_team_history            = False
        # Standings
        self.standings__team_standings_rule            = 'nz'
        # Public Features
        self.public_features__public_side_allocations   = True
        # UI Options
        self.ui_options__show_novices                  = True


class UADCPreferences(AustralsPreferences):
    """ Idk... UNCOMPLETE """
    def __init__(self):
        self.name                                        = "UADC"
        self.show_in_list                                = True
        # Rules source = http://www.alcheringa.in/pdrules.pdf
        # Scoring
        self.scoring__score_min                          = 69.0 # From Rules Book
        self.scoring__score_max                          = 81.0 # From Rules Book
        self.scoring__score_step                         = 1.0
        self.scoring__reply_score_min                    = 34.5 # Not specified; assuming half of substantive
        self.scoring__reply_score_max                    = 42.0 # Not specified; assuming  half of substantive
        self.scoring__reply_score_step                   = 0.5
        self.scoring__maximum_margin                     = 0 # TODO= check this
        self.scoring__margin_includes_dissenters         = True # From Rules:10.9.5
        # # Draws
        self.draw_rules__avoid_same_institution        = False
        self.draw_rules__avoid_team_history            = True
        self.draw_rules__draw_odd_bracket              = 'pullup_top' # From Rules 10.3.1
        self.draw_rules__draw_side_allocations         = 'balance' # From Rules 10.6
        self.draw_rules__draw_pairing_method           = 'slide' # From rules 10.5
        self.draw_rules__draw_avoid_conflicts          = 'one_up_one_down' # From rules 10.6.4
        # # Debate Rules
        self.debate_rules__substantive_speakers        = 3
        self.debate_rules__reply_scores_enabled        = True
        self.debate_rules__motion_vetoes_enabled       = True
        # # Standings Rules
        # self.standings__team_standings_rule            = 'australs' # TODO: need a new standings rule
        self.standings__speaker_standings_rule         = 'australs'
        # Feedback
        self.feedback__adj_min_score                      = 1.0 # Explicit in the rules
        self.feedback__adj_max_score                      = 5.0 # Explicit in the rules
        # UI Options
        self.public_features__feedback_progress          = True # Feedback is compulsory


class WADLPreferences(PreferencesPreset):
    """ Example high school league setup """
    def __init__(self):
        self.name                                      = "WADL"
        self.show_in_list                              = True
        # Debate Rules= no replies; singular motions
        self.debate_rules__substantive_speakers        = 3
        self.debate_rules__reply_scores_enabled        = False
        self.debate_rules__motion_vetoes_enabled       = False
        self.data_entry__enable_motions                = False
        # Standings Rules
        self.standings__standings_missed_debates       = 0
        self.standings__team_standings_rule            = 'wadl'
        self.standings__speaker_standings_rule         = 'wadl'
        # Draws
        self.draw_rules__avoid_same_institution        = False
        self.draw_rules__avoid_team_history            = False
        self.draw_rules__draw_odd_bracket              = 'intermediate_bubble_up_down'
        self.draw_rules__draw_side_allocations         = 'balance'
        self.draw_rules__draw_pairing_method           = 'slide'
        self.draw_rules__draw_avoid_conflicts          = 'one_up_one_down'
        # UI Options
        self.ui_options__show_novices                  = True
        self.ui_options__show_emoji                    = False
        self.ui_options__show_institutions             = False
        self.ui_options__show_speakers_in_draw         = False
        self.ui_options__public_motions_descending     = True
        self.ui_options__show_all_draws                = True
        # League Options
        self.league_options__enable_flagged_motions    = True
        self.league_options__enable_adj_notes          = True
        self.league_options__enable_venue_groups       = True
        self.league_options__enable_venue_times        = True
        self.league_options__enable_venue_overlaps     = True
        self.league_options__share_adjs                = True
        self.league_options__duplicate_adjs            = True
        self.league_options__public_divisions          = True
        self.league_options__show_avg_margin           = True
        self.league_options__enable_divisions          = True
        self.league_options__enable_postponements      = True
        self.league_options__enable_forfeits           = True
        self.league_options__enable_division_motions   = True
        self.league_options__team_points_rule          = 'wadl'



class PublicInformation(PreferencesPreset):
    """ For tournaments hosted online: this sets it up so that people can access the draw and other information via the tab site """
    def __init__(self):
        self.name                                      = "Public Information"
        self.show_in_list                              = True
        self.public_features__public_draw              = True
        self.public_features__public_break_categories  = True
        self.public_features__public_results           = True
        self.public_features__public_motions           = True
        self.public_features__public_team_standings    = True
        self.public_features__public_breaking_teams    = True
        self.public_features__public_breaking_adjs     = True










