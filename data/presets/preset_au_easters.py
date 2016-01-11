from .preset_australs import AustralsPreferences

class AustralianEastersPreferences(AustralsPreferences):

    def __init__(self):

        # Scoring: easters has a lower range
        self.scoring__score_min                        : 70.0,
        self.scoring__score_max                        : 80.0,

        # TODO: pretty sure this is constitutional
        self.scoring__maximum_margin                   : 15,

        # Debate Rules: no replies; singular motions
        self.debate_rules__reply_scores_enabled        : False,
        self.debate_rules__motion_vetoes_enabled       : False,

