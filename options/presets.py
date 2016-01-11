
class PreferencesPreset:
    def __init__(self):
        self.show_in_list                             = False

class AustralsPreferences(PreferencesPreset):

    def __init__(self):
        self.name                                     = "Australs"
        self.show_in_list                             = True

        # Scoring
        self.scoring__score_min                        = 68.0,
        self.scoring__score_max                        = 82.0,
        self.scoring__score_step                       = 1.0,

        self.scoring__reply_score_min                  = 34.0,
        self.scoring__reply_score_max                  = 41.0,
        self.scoring__reply_score_step                 = 0.5,
        self.scoring__maximum_margin                   = 15.0, # TODO= check this

        # Draws
        self.draw_rules__avoid_same_institution        = True,
        self.draw_rules__avoid_team_history            = True,
        self.draw_rules__draw_odd_bracket              = 'intermediate_bubble_up_down',
        self.draw_rules__draw_side_allocations         = 'balance',
        self.draw_rules__draw_pairing_method           = 'slide',
        self.draw_rules__draw_avoid_conflicts          = 'one_up_one_down',

        # Debate Rules
        self.debate_rules__substantive_speakers        = 3,
        self.debate_rules__reply_scores_enabled        = True,
        self.debate_rules__motion_vetoes_enabled       = True,

        # Standings Rules
        self.standings__standings_missed_debates       = 2, # TODO= check this
        self.standings__team_standings_rule            = 'australs',
        self.standings__speaker_standings_rule         = 'australs',


class AustralianEastersPreferences(AustralsPreferences):

    def __init__(self):
        self.name                                      = "Australian Easters"
        self.show_in_list                              = True

        # Scoring= easters has a lower range
        self.scoring__score_min                        = 70.0,
        self.scoring__score_max                        = 80.0,

        # TODO= pretty sure this is constitutional
        self.scoring__maximum_margin                   = 15.0,

        # Debate Rules= no replies; singular motions
        self.debate_rules__reply_scores_enabled        = False,
        self.debate_rules__motion_vetoes_enabled       = False,




class WADLPreferences(PreferencesPreset):

    def __init__(self):
        self.name                                      = "WADL"
        self.show_in_list                              = True

        # Debate Rules= no replies; singular motions
        self.debate_rules__reply_scores_enabled        = False,
        self.debate_rules__motion_vetoes_enabled       = False,

        # Standings Rules
        self.standings__standings_missed_debates       = 0,
        self.standings__team_standings_rule            = 'wadl',
        self.standings__speaker_standings_rule         = 'wadl',


        # Draws
        self.draw_rules__avoid_same_institution        = True,
        self.draw_rules__avoid_team_history            = True,
        self.draw_rules__draw_odd_bracket              = 'intermediate_bubble_up_down',
        self.draw_rules__draw_side_allocations         = 'balance',
        self.draw_rules__draw_pairing_method           = 'slide',
        self.draw_rules__draw_avoid_conflicts          = 'one_up_one_down',

        # Debate Rules
        self.debate_rules__substantive_speakers        = 3,
        self.debate_rules__reply_scores_enabled        = True,
        self.debate_rules__motion_vetoes_enabled       = True,

