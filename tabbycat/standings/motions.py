from utils.tables import TabbycatTableBuilder

# Critical Values / Determination
BALANCES = [
    {'critical': 0.455,  'label': 'Balanced'},            # .5 Degrees of freedom
    {'critical': 2.706,  'label': 'Slightly imbalanced'}, # .1
    {'critical': 3.841,  'label': 'Somewhat imbalance'},  # .05
    {'critical': 5.412,  'label': 'Imbalanced'},          # .02
    {'critical': 6.635,  'label': 'Very imbalanced'},     # .01
    {'critical': 10.827, 'label': 'Badly imbalanced'},    # .001
]


class MotionsStandingsTableBuilder(TabbycatTableBuilder):

    def add_balance_column(self, motions, is_bp):
        overall_header = {
            'key': 'Balance',
            'tooltip': 'Motion balance todo details',
        }
        overall_data = []
        for motion in motions:
            c_stat, stats = get_balance(motion, is_bp)
            overall_data.append({
                'text': stats['label'], 'sort': c_stat,
                'tooltip': '%s less than threshold %s' % (c_stat, stats['critical'])
            })
        self.add_column(overall_header, overall_data)


def get_balance(motion, is_bp):

    if motion.chosen_in < 10:
        return 0, {'critical': 0, 'label': 'Inconclusive'}
    if is_bp:
        return four_team_balance(motion)
    else:
        return two_team_balance(motion)


def two_team_balance(motion):
    n_2 = int(motion.chosen_in / 2)
    aff_wins = motion.aff_wins
    neg_wins = motion.neg_wins
    aff_c_stat = (((aff_wins - n_2) ^ 2) / n_2)
    neg_c_stat = (((neg_wins - n_2) ^ 2) / n_2)
    c_stat = aff_c_stat + neg_c_stat
    balance = next((ir for ir in BALANCES if c_stat <= ir['critical']), None)

    return c_stat, balance


def four_team_balance(motion):
    return ""
