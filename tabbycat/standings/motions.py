from utils.tables import TabbycatTableBuilder

# Critical Values / Determination
BALANCES = [
    {'critical': 0.455,  'label': 'Balanced', 'freedom': .5},
    {'critical': 2.706,  'label': 'Slightly imbalanced', 'freedom': .1},
    {'critical': 3.841,  'label': 'Somewhat imbalanced', 'freedom': .05},
    {'critical': 5.412,  'label': 'Imbalanced', 'freedom': .02},
    {'critical': 6.635,  'label': 'Very imbalanced', 'freedom': .01},
    {'critical': 10.827, 'label': 'Badly imbalanced', 'freedom': .001},
]


class MotionsStandingsTableBuilder(TabbycatTableBuilder):

    def add_balance_column(self, motions, is_bp):
        overall_header = {
            'key': 'Balance',
            'tooltip': """A chi-squared test measuring the null hypothesis the
                motion is fair (in this context). A range of tests at different
                levels of significance classify the likelihood of balance. More
                details in our documentation.""",
        }
        overall_data = []
        for motion in motions:
            c_stat, label, info = get_balance(motion, is_bp)
            overall_data.append({'text': label, 'sort': c_stat, 'tooltip': info})
        self.add_column(overall_header, overall_data)


def get_balance(motion, is_bp):
    if motion.chosen_in < 10:
        return 0, 'Inconclusive', 'Too few debates to determine meaningful balance'
    if is_bp:
        return four_team_balance(motion)
    else:
        return two_team_balance(motion)


def two_team_balance(motion):
    # Test and confidence levels contributed by Viran Weerasekera
    # TODO: work in vetoes; better account for sample size
    n_2 = int(motion.chosen_in / 2)
    aff_wins = motion.aff_wins
    neg_wins = motion.neg_wins
    aff_c_stat = pow(aff_wins - n_2, 2) / n_2
    neg_c_stat = pow(neg_wins - n_2, 2) / n_2
    c_stat = round(aff_c_stat + neg_c_stat, 2)
    balance = next((ir for ir in BALANCES if c_stat <= ir['critical']), None)
    info = "%s critical value; %s degrees of freedom" % (c_stat, balance['freedom'])
    return c_stat, balance['label'], info


def four_team_balance(motion):
    return ""
