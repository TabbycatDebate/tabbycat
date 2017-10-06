import logging
from collections import OrderedDict

from .common import BasePairDrawGenerator
from .pairing import Pairing

logger = logging.getLogger(__name__)


class RoundRobinDrawGenerator(BasePairDrawGenerator):
    """ Class for round-robin stype matchups using divisions """

    requires_rrseq = True
    requires_even_teams = False

    PAIRING_FUNCTIONS = {
        "random": "_pairings_random"
    }

    DEFAULT_OPTIONS = {"max_swap_attempts": 20, "avoid_conflicts": "off"}

    def generate(self):
        self.teams = self._exclude_teams_without_divisions()
        self._brackets = self._make_raw_brackets_from_divisions()
        # TODO: resolving brackets with odd numbers here (see resolve_odd_brackets)
        self._pairings = self.generate_pairings(self._brackets)
        # TODO: avoiding history conflicts here
        self._draw = list()
        for bracket in self._pairings.values():
            self._draw.extend(bracket)

        self.allocate_sides(self._draw)  # Operates in-place
        return self._draw

    def _exclude_teams_without_divisions(self):
        teams_with_divisions = [t for t in self.teams if t.division]
        if len(self.teams) - len(teams_with_divisions) > 1:
            logger.info("There are %d teams lacking a division (and thus excluded from the draw)"
                        % len(teams_with_divisions))
        return teams_with_divisions

    def _make_raw_brackets_from_divisions(self):
        """Returns an OrderedDict mapping bracket names (normally numbers)
        to lists."""
        brackets = OrderedDict()
        teams = list(self.teams)
        for team in teams:
            # Using the division ID as the division identifier
            division = float(team.division.id)
            if division in brackets:
                brackets[division].append(team)
            else:
                brackets[division] = [team]

        # Assigning subranks - fixed based on alphabetical
        for bracket in brackets.values():
            bracket.sort(key=lambda x: x.short_name, reverse=False)
            for i, team in enumerate(bracket):
                i += 1
                team.subrank = i

        return brackets

    def generate_pairings(self, brackets):
        pairings = OrderedDict()

        # Determine the effective iteration we are on wrt number of RR draws
        effective_round_seq = self.rrseq
        # print("Taking as effective round of %s" % effective_round_seq)

        for bracket in brackets.items():
            teams_list = bracket[1]  # Team Array is second item
            division_seq = bracket[0]
            total_debates = len(teams_list) // 2
            # print("DIVISION %s with %s teams" % (division_seq, len(teams_list)))

            fold_top = teams_list[:total_debates]
            fold_bottom = teams_list[total_debates:]
            fold_bottom.reverse() # Bottom half ranks high to low

            # Reforming the list for the shuffle
            folded_list = list(fold_top)
            folded_list.extend(fold_bottom)

            # print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[:total_debates]])
            # print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[total_debates:]])

            for i in range(1, effective_round_seq):
                # Left-most bottom goes to position[1] on the top
                folded_list.insert(1, (folded_list.pop(total_debates)))
                # Right-most top goes to right-most bottom
                folded_list.append(folded_list.pop(total_debates))
                # Print "popping %s iteration %s" % (i, total_debates)

            # print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[:total_debates]])
            # print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[total_debates:]])

            # IE For Round 2 - before and after
            # ['1 - Aquinas 1', '2 - Aquinas 2', '3 - Penrhos 1']
            # ['6 - Santa Maria 1', '5 - Rossmoyne 2', '4 - Rossmoyne 1']
            # popping 1 iteration 3
            # ['1 - Aquinas 1', '6 - Santa Maria 1', '2 - Aquinas 2']
            # ['5 - Rossmoyne 2', '4 - Rossmoyne 1', '3 - Penrhos 1']

            assigned_teams = []
            assigned_pairings = []
            for paired_teams in zip(folded_list[:total_debates], folded_list[total_debates:]):
                aff = paired_teams[0]
                neg = paired_teams[1]
                # Iterating through each half and matching - ie 1-4, 2-5, 3-6
                if neg:
                    pairing = Pairing(
                        teams=(paired_teams),
                        bracket=division_seq,
                        room_rank=division_seq,
                        division=aff.division
                    )
                    # print("\t matchup is %s (%s) vs %s (%s)" % (aff, teams_list.index(aff) + 1, neg, teams_list.index(neg) + 1))
                    assigned_pairings.append(pairing)
                    assigned_teams.append(aff)
                    assigned_teams.append(neg)
                else:
                    # Need to deal with Byes and the like here
                    print("couldn't find an opponent")

            pairings[division_seq] = assigned_pairings

        return pairings
