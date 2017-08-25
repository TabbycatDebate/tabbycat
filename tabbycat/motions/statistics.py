from django.utils.functional import cached_property


class MotionStats:

    # Critical Values / Determination
    BALANCES = [
        {'critical': 0.455,  'label': '50% (balanced)',             'freedom': .5},
        {'critical': 2.706,  'label': '90% likely TEAM favoured ',  'freedom': .1},
        {'critical': 3.841,  'label': '95% likely TEAM favoured',   'freedom': .05},
        {'critical': 5.412,  'label': '98% likely TEAM favoured',   'freedom': .02},
        {'critical': 6.635,  'label': '99% likely TEAM favoured',   'freedom': .01},
        # The last value is large enough to be a catch-all; ie over 99.9% confidence
        {'critical': 1000.0, 'label': '99.9% likely TEAM favoured', 'freedom': .001},
    ]

    def __init__(self, motion, t, results, vetoes=False):
        self.motion = motion
        self.round = motion.round # Needed for regroup
        self.sides = t.sides

        if t.pref('enable_motions'):
            results_data = [r for r in results if r.ballot_submission.motion == motion]
            vetoes_data = [v for v in vetoes if v.motion == motion]
        else:
            results_data = [r for r in results if r.ballot_submission.debate.round == self.round]
            vetoes_data = [v for v in vetoes if v.motion.round == self.round]

        if t.pref('teams_in_debate') == 'two':
            self.isBP = False
            self.debate_rooms = len(results_data) / 2
            self.round_rooms = len(results) / 2
        else:
            self.isBP = True
            self.debate_rooms = len(results_data) / 4
            self.round_rooms = len(results) / 4

        self.placings = self.gather_placings(self.points_dict(), results_data)
        self.result_balance = self.determine_balance()

        if vetoes:
            self.vetoes = self.gather_vetoes(self.points_dict(), vetoes_data)
            self.veto_balance = self.determine_balance(True)

    def points_dict(self):
        if self.isBP:
            return dict((s, {3: 0, 2: 0, 1: 0, 0: 0}) for s in self.sides)
        else:
            return dict((s, {1: 0, 0: 0}) for s in self.sides)

    # Calculate points per position and debate
    def gather_placings(self, placings_data, results):
        for result in results:
            placings_data[result.debate_team.side][result.points] += 1

        return placings_data

    # Calculate points per position and debate
    def gather_vetoes(self, vetoes_data, vetoes):
        for veto in vetoes:
            vetoes_data[veto.debate_team.side][1] += 1
        return vetoes_data

    def determine_balance(self, for_vetoes=False):
        if self.debate_rooms < 10: # Too few wins/vetoes to calculate
            return 'inconclusive', 'Too few debate to determine meaningful balance'
        elif self.isBP:
            return self.two_team_balance(for_vetoes)
        else:
            return self.four_team_balance(for_vetoes)

    def two_team_balance(self, for_vetoes):
        # Test and confidence levels contributed by Viran Weerasekera
        if for_vetoes:
            affs = self.vetoes['aff']
            negs = self.vetoes['neg']
        else:
            affs = self.placings['aff'][1]
            negs = self.placings['neg'][1]

        n_2 = int(self.debate_rooms)
        aff_c_stat = pow(affs - n_2, 2) / n_2
        neg_c_stat = pow(negs - n_2, 2) / n_2
        c_stat = round(aff_c_stat + neg_c_stat, 2)

        # print('\tc_stat', c_stat)
        threshold = next((ir for ir in self.BALANCES if c_stat <= ir['critical']), None)

        info = "%s critical value; %s level of signficance" % (c_stat, threshold['freedom'])

        if affs > negs:
            return threshold['label'].replace('TEAM', 'aff'), info
        elif affs < negs:
            return threshold['label'].replace('TEAM', 'neg'), info
        else:
            return threshold['label'], info

    # def four_team_balance(results_for_motion, chosen_count):
    #     return None, None

    @cached_property
    def results_rates(self):
        return self.points_rates(self.placings)

    @cached_property
    def veto_rates(self):
        return self.points_rates(self.placings, True)

    # For a given point figure out what % of total results it was
    def points_rates(self, data_set, vetoes=False):
        if self.debate_rooms == 0:
            return data_set

        rates_for_side = dict(self.points_dict())
        for side in self.sides:
            for points, count in data_set[side].items():
                percentage = data_set[side][points] / self.round_rooms * 100
                rates_for_side[side][points] = percentage

        return rates_for_side
