from utils.tables import TabbycatTableBuilder

# Critical Values / Determination
BALANCES = [
    {'critical': 0.455,  'label': '50% (balanced)', 'freedom': .5},
    {'critical': 2.706,  'label': '90% likely TEAM favoured ', 'freedom': .1},
    {'critical': 3.841,  'label': '95% likely TEAM favoured', 'freedom': .05},
    {'critical': 5.412,  'label': '98% likely TEAM favoured', 'freedom': .02},
    {'critical': 6.635,  'label': '99% likely TEAM favoured', 'freedom': .01},
    # The last value is large enough to be a catch-all; ie over 99.9% confidence
    {'critical': 1000.0, 'label': '99.9% likely TEAM favoured', 'freedom': .001},
]


class MotionsStandingsTableBuilder(TabbycatTableBuilder):

    def add_debate_balance_column(self, motions):
        overall_header = {
            'key': 'Result Balance',
            'tooltip': """A chi-squared test measuring the null hypothesis the
                motion is fair (ie has an equal chance of either team winning
                in this context). A range of tests at different levels of
                significance classify the likelihood of balance. More
                details in our documentation.""",
        }
        overall_data = []
        for motion in motions:
            c_stat, label, info = get_balance(motion, self.tournament, False)
            overall_data.append({'text': label, 'sort': c_stat, 'tooltip': info})
        self.add_column(overall_header, overall_data)

    def add_veto_balance_column(self, motions):
        overall_header = {
            'key': 'Veto Balance',
            'tooltip': """The same test used for debate results; but applied
                to the null hypothesis that a motion is equally likely to be
                vetoed by either side.""",
        }
        overall_data = []
        for motion in motions:
            c_stat, label, info = get_balance(motion, self.tournament, True)
            overall_data.append({'text': label, 'sort': c_stat, 'tooltip': info})
        self.add_column(overall_header, overall_data)


def get_balance(motion, tournament, for_vetoes):
    inconclusive = 'Too few vetoes to determine meaningful balance'

    if tournament.pref('teams_in_debate') == 'two':
        if for_vetoes and (motion.aff_vetoes + motion.neg_vetoes) < 10:
            return 0, 'inconclusive', inconclusive
        if not for_vetoes and motion.chosen_in < 10:
            return 0, 'inconclusive', inconclusive
        else:
            return two_team_balance(motion, for_vetoes)
    else:
        return four_team_balance(motion)


def two_team_balance(motion, for_vetoes):
    # Test and confidence levels contributed by Viran Weerasekera
    if for_vetoes:
        affs = motion.neg_vetoes # 6
        negs = motion.aff_vetoes # 6
        n_2 = int((affs + negs) / 2)
    else:
        affs = motion.aff_wins
        negs = motion.neg_wins
        n_2 = int(motion.chosen_in / 2)

    aff_c_stat = pow(affs - n_2, 2) / n_2
    neg_c_stat = pow(negs - n_2, 2) / n_2
    c_stat = round(aff_c_stat + neg_c_stat, 2)
    balance = next((ir for ir in BALANCES if c_stat <= ir['critical']), None)
    info = "%s critical value; %s level of signficance" % (c_stat, balance['freedom'])

    if affs > negs:
        return c_stat, balance['label'].replace('TEAM', 'aff'), info
    elif affs < negs:
        return c_stat, balance['label'].replace('TEAM', 'neg'), info
    else:
        return c_stat, balance['label'], info


def four_team_balance(motion):
    return None, None, None
