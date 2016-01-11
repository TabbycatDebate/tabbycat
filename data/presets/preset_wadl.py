from .preset import Preset

class WADLPreferences(PreferencesPreset):

    def __init__(self):

        # Debate Rules: no replies; singular motions
        self.debate_rules__reply_scores_enabled        : False,
        self.debate_rules__motion_vetoes_enabled       : False,

        # Standings Rules
        self.standings__standings_missed_debates       : 0,
        self.standings__team_standings_rule            : 'wadl',
        self.standings__speaker_standings_rule         : 'wadl',


        # Draws
        self.draw_rules__avoid_same_institution        : True,
        self.draw_rules__avoid_team_history            : True,
        self.draw_rules__intermediate_bubble_up_down   : 'intermediate_bubble_up_down',
        self.draw_rules__draw_side_allocations         : 'balance',
        self.draw_rules__draw_pairing_method           : 'slide',
        self.draw_rules__draw_avoid_conflicts          : 'one_up_one_down',

        # Debate Rules
        self.debate_rules__debate_rules                : 3,
        self.debate_rules__reply_scores_enabled        : True,
        self.debate_rules__motion_vetoes_enabled       : True,

