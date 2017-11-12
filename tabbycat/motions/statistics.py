from django.utils.functional import cached_property


class MotionStats:

    def __init__(self, motion, t, results, all_vetoes=None):
        self.motion = motion
        self.round = motion.round # Needed for regroup
        self.sides = t.sides

        results_data_for_round = [r for r in results if r.ballot_submission.debate.round == self.round]
        if t.pref('enable_motions'):
            results_data_for_motion = [r for r in results_data_for_round if r.ballot_submission.motion == motion]
        else:
            results_data_for_motion = results_data_for_round

        if all_vetoes and len(all_vetoes) > 0:
            vetoes_data = [v for v in all_vetoes if v.motion == motion]

        if t.pref('teams_in_debate') == 'two':
            self.isBP = False
            self.round_rooms = int(len(results_data_for_round) / 2)
            self.debate_rooms = int(len(results_data_for_motion) / 2)
        else:
            self.isBP = True
            self.round_rooms = int(len(results_data_for_round) / 4)
            self.debate_rooms = int(len(results_data_for_motion) / 4)

        self.placings = self.gather_placings(self.points_dict(), results_data_for_motion)
        self.result_balance = self.determine_balance()

        if all_vetoes and len(all_vetoes) > 0:
            self.vetoes = self.gather_vetoes(self.points_dict(), vetoes_data)
            self.veto_balance = self.determine_balance(True)
        else:
            self.vetoes = False
            self.veto_balance = False

    def points_dict(self):
        if self.isBP:
            return dict((s, {3: 0, 2: 0, 1: 0, 0: 0}) for s in self.sides)
        else:
            return dict((s, {1: 0, 0: 0}) for s in self.sides)

    # Calculate points per position and debate
    def gather_placings(self, placings, results_data):
        for result in results_data:
            if result.points is not None: # Some finals rounds etc wont have points
                placings[result.debate_team.side][result.points] += 1
            elif result.win is True: # Out rounds
                placings[result.debate_team.side][3] += 1
            elif result.win is False: # Out rounds
                placings[result.debate_team.side][0] += 1

        return placings

    # Calculate points per position and debate
    def gather_vetoes(self, vetoes, vetoes_data):
        for veto in vetoes_data:
            vetoes[veto.debate_team.side][1] += 1
        return vetoes

    def determine_balance(self, for_vetoes=False):
        if self.debate_rooms < 10: # Too few wins/vetoes to calculate
            return 'balance inconclusive', 'Too few debate to determine meaningful balance'
        elif self.isBP:
            return None
            # return self.four_team_balance(for_vetoes) # Not implemented
        else:
            return self.two_team_balance(for_vetoes)

    def two_team_balance(self, for_vetoes):
        # Test and confidence levels contributed by Viran Weerasekera
        if for_vetoes:
            # Swap keys as we assume vetos favour the opposite side
            affs = self.vetoes['neg'][1]
            negs = self.vetoes['aff'][1]
        else:
            affs = self.placings['aff'][1]
            negs = self.placings['neg'][1]

        n_2 = int(self.debate_rooms)
        aff_c_stat = pow(affs - n_2, 2) / n_2
        neg_c_stat = pow(negs - n_2, 2) / n_2
        c_stat = round(aff_c_stat + neg_c_stat, 2)

        threshold = next((ir for ir in self.BALANCES_2V2 if c_stat <= ir['critical']), None)
        info = "%s critical value; %s level of signficance" % (c_stat, threshold['freedom'])

        if affs > negs:
            return threshold['label'].replace('TEAM', 'aff'), info
        elif affs < negs:
            return threshold['label'].replace('TEAM', 'neg'), info
        else:
            return threshold['label'], info

    def four_team_balance(self):
        # For reference here we have self.placings dictionary of positions { 'og': X, 'oo': Y }
        # Within each position key there is a list of points and the total number of times that side
        # received those points; ie { 'og': {3: 9, 2: 10, 1: 5, 0: 8}
        # threshold = next((ir for ir in self.BALANCES if c_stat <= ir['critical']), None)
        # info = "%s critical value; %s level of signficance" % (c_stat, threshold['freedom'])
        # return threshold['label'], info
        raise NotImplementedError

    @cached_property
    def results_rates(self):
        return self.points_rates(self.placings)

    @cached_property
    def veto_rates(self):
        return self.points_rates(self.vetoes, True)

    # For a given point figure out what % of total results it was
    def points_rates(self, data_set, vetoes=False):
        if self.round_rooms == 0 or self.debate_rooms == 0 or not data_set:
            return None

        if vetoes:
            print("%s\n\tround_rooms %s / debate_rooms %s" % (self.motion, self.round_rooms, self.debate_rooms))

        rates_for_side = dict(self.points_dict())
        for side in self.sides:
            for points, count in data_set[side].items():
                # Measuring vetoes (per-team) not wins (per room)
                if vetoes and self.isBP:
                    denominator = self.round_rooms * 2
                elif vetoes and not self.isBP:
                    denominator = self.round_rooms * 4
                else:
                    denominator = self.round_rooms

                percentage = (data_set[side][points] / denominator) * 100
                rates_for_side[side][points] = round(percentage, 1)
                if vetoes:
                    print("\t%s percent for %s (%s / %s)" % (round(percentage, 1), side, data_set[side][points], denominator))

        return rates_for_side

    @cached_property
    def points_average(self):
        if self.debate_rooms == 0:
            return None

        avgs_for_side = dict(self.points_dict())
        for side in self.sides:
            all_points = []
            counts = 0
            for points, count in self.placings[side].items():
                all_points.append(points * count)
                counts += count

            if counts > 0: # Avoid divide by zero
                avgs_for_side[side] = sum(all_points) / float(counts)
            else:
                avgs_for_side[side] = 1.5

        return avgs_for_side

    # Critical Values / Determination
    BALANCES_2V2 = [
        {'critical': 0.455,  'label': '50% (balanced)',             'freedom': .5},
        {'critical': 2.706,  'label': '90% likely TEAM favoured ',  'freedom': .1},
        {'critical': 3.841,  'label': '95% likely TEAM favoured',   'freedom': .05},
        {'critical': 5.412,  'label': '98% likely TEAM favoured',   'freedom': .02},
        {'critical': 6.635,  'label': '99% likely TEAM favoured',   'freedom': .01},
        # The last value is large enough to be a catch-all; ie over 99.9% confidence
        {'critical': 1000.0, 'label': '99.9% likely TEAM favoured', 'freedom': .001},
    ]

    BALANCES_BP = [

    ]
