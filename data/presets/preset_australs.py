from .preset import PreferencesPreset

class AustralsPreferences(PreferencesPreset):

    def __init__(self):

        # Scoring
        self.scoring__score_min                        : 68.0,
        self.scoring__score_max                        : 82.0,
        self.scoring__score_step                       : 1.0,

        self.scoring__reply_score_min                  : 34,
        self.scoring__reply_score_max                  : 41,
        self.scoring__reply_score_step                 : 0.5,
        self.scoring__maximum_margin                   : 15, # TODO: check this

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

        # Standings Rules
        self.standings__standings_missed_debates       : 2, # TODO: check this
        self.standings__team_standings_rule            : 'australs',
        self.standings__speaker_standings_rule         : 'australs',
