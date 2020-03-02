import random
from collections import OrderedDict

from django.utils.translation import gettext as _

from .common import BasePairDrawGenerator, DrawFatalError, DrawUserError
from .one_up_one_down import OneUpOneDownSwapper
from .pairing import Pairing


class PowerPairedDrawGenerator(BasePairDrawGenerator):
    """Power-paired draw.

    If there are allocated sides, use PowerPairedWithAllocatedSidesDrawGenerator
    instead.

    Options:
        "odd_bracket" - Odd bracket resolution method. Permitted values:

            "pullup_top"    - Pull up the top team from the next bracket down.
            "pullup_bottom" - Pull up the bottom team from the next bracket down.
            "pullup_random" - Pull up a random team from the next bracket down.
            "intermediate"  - The bottom team from the odd bracket and the top
                              team from the next bracket down face each other in
                              an intermediate bracket.
            "intermediate_bubble_up_down" - Like "intermediate", but will swap
                              teams that conflict by history or institution.

            or a function taking a dict mapping floats to lists of Team-like
            objects, and operating on the dict in-place.

        "pullup_restriction" - Restriction on who can be pulled up. Permitted values:

            "none"             - No restriction.
            "least_to_date"    - Choose from teams who have been pulled up the
                                 least number of times in previous rounds.
            "lowest_ds_wins"   - Choose from teams who have the lowest draw strength by
                                 wins (indicative of having been against easier teams)
            "lowest_ds_speaks" - Choose from teams who have the lowest draw strength by
                                 speaks (indicative of having been against easier teams)

        "pairing_method" - How to pair teams. Permitted values:
            (best explained by example, these examples have a ten-team bracket)

            "slide"  - 1 vs 6, 2 vs 7, ..., 5 vs 10.
            "fold"   - 1 vs 10, 2 vs 9, ..., 5 vs 6.
            "random" - Pairs chosen randomly.

            or a function taking a dict mapping floats to even-length lists of
            Team-like objects, and returning a list of Pairing objects with
            those teams.

        "avoid_conflicts" - How to avoid conflicts. Permitted values:

            "off"             - Do not attempt to avoid conflicts.
            "one_up_one_down" - Swap conflicted teams with the debate above or
                                below, in accordance with Australasian
                                Intervarsity Debating Association rules.
    """

    requires_even_teams = True
    requires_prev_results = False

    DEFAULT_OPTIONS = {
        "odd_bracket"           : "intermediate_bubble_up_down",
        "pairing_method"        : "slide",
        "avoid_conflicts"       : "one_up_one_down",
        "pullup_restriction"    : "none",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_teams_for_attribute("points")

        if self.options["odd_bracket"].startswith("intermediate"):
            noninteger = [team.points == int(team.points) for team in self.teams].count(False)
            if noninteger > 0:
                raise DrawUserError(_("%(noninteger)d out of %(total)d teams have a noninteger "
                    "first metric in the team standings. Intermediate brackets require the first "
                    "team standings metric to be an integer (typically points or wins).") % {
                    'noninteger': noninteger, 'total': len(self.teams)})

        pullup_metric = self.PULLUP_RESTRICTION_METRICS[self.options["pullup_restriction"]]
        if pullup_metric is not None:
            self.check_teams_for_attribute(pullup_metric, checkfunc=lambda x: isinstance(x, (int, float)))

    def generate(self):
        self._brackets = self._make_raw_brackets()
        self.resolve_odd_brackets(self._brackets)  # operates in-place
        self._pairings = self.generate_pairings(self._brackets)
        self.avoid_conflicts(self._pairings)  # operates in-place
        self._draw = list()
        for bracket in self._pairings.values():
            self._draw.extend(bracket)

        self.allocate_sides(self._draw)  # operates in-place
        self.annotate_team_flags(self._draw)  # operates in-place
        return self._draw

    def _make_raw_brackets(self):
        """Returns an OrderedDict mapping bracket names (normally numbers)
        to lists."""
        brackets = OrderedDict()
        teams = list(self.teams)
        while len(teams) > 0:
            top_team = teams.pop(0)
            points = top_team.points
            pool = [top_team]
            while len(teams) > 0 and teams[0].points == points:
                pool.append(teams.pop(0))
            brackets[points] = pool
        return brackets

    # Pullup restrictions

    PULLUP_RESTRICTION_METRICS = {
        "least_to_date": "npullups",
        "lowest_ds_wins": "draw_strength",
        "lowest_ds_speaks": "draw_strength_speaks",
        "none": None,
    }

    def _pullup_filter(self, teams):
        """Returns a function that takes one argument, a team, and returns a
        bool, indicating whether that team is eligible to be pulled up."""
        option = self.options["pullup_restriction"]
        try:
            metric = self.PULLUP_RESTRICTION_METRICS[option]
        except KeyError:
            raise ValueError("Invalid option for pullup_restriction: {0}".format(option))

        if metric is None:
            return teams
        else:
            least = min(getattr(team, metric) for team in teams)
            return [team for team in teams if getattr(team, metric) == least]

    # Odd bracket resolutions

    ODD_BRACKET_FUNCTIONS = {
        "pullup_top"                 : "_pullup_top",
        "pullup_bottom"              : "_pullup_bottom",
        "pullup_middle"              : "_pullup_middle",
        "pullup_random"              : "_pullup_random",
        "intermediate"               : "_intermediate_brackets",
        "intermediate_bubble_up_down": "_intermediate_brackets_with_bubble_up_down",
    }

    def resolve_odd_brackets(self, brackets):
        """Returns a function taking an OrderedDict as returned by
        _make_raw_brackets(), and adjusting that OrderedDict in-place to
        guarantee that all brackets have an even number of teams."""
        function = self.get_option_function("odd_bracket", self.ODD_BRACKET_FUNCTIONS)
        return function(brackets)

    def _pullup_top(self, brackets):
        self._pullup(brackets, lambda x: 0)

    def _pullup_middle(self, brackets):
        self._pullup(brackets, lambda x: x // 2 - (random.randrange(2) if x % 2 == 0 else 0))

    def _pullup_bottom(self, brackets):
        self._pullup(brackets, lambda x: -1)

    def _pullup_random(self, brackets):
        self._pullup(brackets, lambda x: random.randrange(x))

    def _pullup(self, brackets, pos):
        """'brackets' is what is returned by _make_raw_brackets().
        'pos' is a function taking the number of teams to choose from,
        and returning an index for which team to take as the pullup.
        Operates in-place. Does not remove empty brackets."""
        pullup_needed_for = None

        for points, teams in brackets.items():
            if pullup_needed_for:
                pullup_eligible_teams = self._pullup_filter(teams)
                pullup_team = pullup_eligible_teams[pos(len(pullup_eligible_teams))]
                teams.remove(pullup_team)
                self.add_team_flag(pullup_team, "pullup")
                pullup_needed_for.append(pullup_team)
                pullup_needed_for = None

            if len(teams) % 2 != 0:
                pullup_needed_for = teams

        if pullup_needed_for:
            raise DrawFatalError("Last bracket is still odd!\n" + repr(pullup_needed_for))

    @classmethod
    def _intermediate_brackets(cls, brackets):
        """Operates in-place."""
        new = OrderedDict()
        odd_team = None
        for points, teams in brackets.items():
            if odd_team:
                new[points+0.5] = [odd_team, teams.pop(0)]
                odd_team = None
            if len(teams) % 2 != 0:
                odd_team = teams.pop()
            if len(teams) > 0:
                new[points] = teams
        if odd_team:
            raise DrawFatalError("Last bracket is still odd!\n" + repr(odd_team))
        brackets.clear()
        brackets.update(new)

    def _intermediate_brackets_with_bubble_up_down(self, brackets):
        """Operates in-place.
        Requires Team.institution and Team.seen() to be defined."""
        self._intermediate_brackets(brackets)  # operates in-place
        # Check each of the intermediate brackets for conflicts.
        # If there is one, try swapping the top team with the bottom team
        # of the bracket above. Failing that, try the same with the bottom
        # team and the top team of the bracket below. Failing that, give up.
        # Note: Under no circumstances do we swap both teams.

        def _check_conflict(team1, team2):
            try:
                if team1.institution == team2.institution:
                    return 1  # Institution
                if team1.seen(team2):
                    return 2  # History
            except AttributeError:
                raise DrawFatalError("For conflict avoidance, teams must have attributes 'institution' and 'seen'.")
            return 0  # No conflict

        for points, teams in brackets.items():
            if int(points) == points:
                continue  # Skip non-intermediate brackets
            # a couple of checks
            assert points % 0.5 == 0
            assert teams[0].points > teams[1].points
            conflict = _check_conflict(*teams)
            if not conflict:
                continue # leave alone if no conflict

            # bubble up, if there exists such a bubble
            # swap bottom team from higher bracket with top team from
            # intermediate bracket.
            if points+0.5 in brackets:
                swap_team = brackets[points+0.5][-1] # bottom team
                if not _check_conflict(swap_team, teams[1]):
                    self.add_team_flag(teams[0], (conflict == 1) and "bub_up_inst" or "bub_up_hist")
                    self.add_team_flag(swap_team, "bub_up_accom")
                    teams[0], brackets[points+0.5][-1] = swap_team, teams[0]
                    continue

            # bubble down, if bubble up didn't work
            if points-0.5 in brackets:
                swap_team = brackets[points-0.5][0]  # Bottom team
                if not _check_conflict(swap_team, teams[0]):
                    self.add_team_flag(teams[1], (conflict == 1) and "bub_dn_inst" or "bub_dn_hist")
                    self.add_team_flag(swap_team, "bub_dn_accom")
                    teams[1], brackets[points-0.5][0] = swap_team, teams[1]
                    continue

            # if nothing worked, add a "didn't work" flag
            self.add_team_flag(teams[0], "no_bub_updn")

    # Pairings generation
    PAIRING_FUNCTIONS = {
        "fold"                  : "_pairings_fold",
        "slide"                 : "_pairings_slide",
        "random"                : "_pairings_random",
        "adjacent"              : "_pairings_adjacent",
        "fold_top_adjacent_rest": "_pairings_fold_top_adjacent_rest",
    }

    def generate_pairings(self, brackets):
        """Returns a function taking an OrderedDict as returned by
        resolve_odd_brackets(), and returning a list of Debates."""
        function = self.get_option_function("pairing_method", self.PAIRING_FUNCTIONS)
        return function(brackets)

    @staticmethod
    def _pairings(brackets, subpool_func):
        pairings = OrderedDict()
        i = 1
        for points, teams in brackets.items():
            bracket = list()
            top, bottom = subpool_func(teams)
            for teams in zip(top, bottom):
                pairing = Pairing(teams=teams, bracket=points, room_rank=i)
                bracket.append(pairing)
                i = i + 1
            pairings[points] = bracket
        return pairings

    @staticmethod
    def _pairings_top_special(brackets, top_subpool_func, rest_subpool_func):
        pairings = OrderedDict()
        i = 1
        subpool_funcs = [top_subpool_func] + [rest_subpool_func] * (len(brackets) - 1)
        for (points, teams), subpool_func in zip(brackets.items(), subpool_funcs):
            bracket = list()
            top, bottom = subpool_func(teams)
            for teams in zip(top, bottom):
                pairing = Pairing(teams=teams, bracket=points, room_rank=i)
                bracket.append(pairing)
                i = i + 1
            pairings[points] = bracket
        return pairings

    @staticmethod
    def _subpool_slide(teams):
        num_debates = len(teams) // 2
        top = teams[:num_debates]
        bottom = teams[num_debates:]
        return top, bottom

    @staticmethod
    def _subpool_fold(teams):
        num_debates = len(teams) // 2
        top = teams[:num_debates]
        bottom = teams[num_debates:]
        bottom.reverse()
        return top, bottom

    @staticmethod
    def _subpool_shuffle(teams):
        num_debates = len(teams) // 2
        random.shuffle(teams)
        top = teams[:num_debates]
        bottom = teams[num_debates:]
        return top, bottom

    @staticmethod
    def _subpool_adjacent(teams):
        return teams[0::2], teams[1::2]

    @classmethod
    def _pairings_slide(cls, brackets):
        return cls._pairings(brackets, cls._subpool_slide)

    @classmethod
    def _pairings_fold(cls, brackets):
        return cls._pairings(brackets, cls._subpool_fold)

    @classmethod
    def _pairings_random(cls, brackets):
        return cls._pairings(brackets, cls._subpool_shuffle)

    @classmethod
    def _pairings_adjacent(cls, brackets):
        return cls._pairings(brackets, cls._subpool_adjacent)

    @classmethod
    def _pairings_fold_top_adjacent_rest(cls, brackets):
        return cls._pairings_top_special(brackets, cls._subpool_fold, cls._subpool_adjacent)

    # Conflict avoidance

    AVOID_CONFLICT_FUNCTIONS = {
        "one_up_one_down": "_one_up_one_down",
    }

    def avoid_conflicts(self, pairings):
        """Returns a function taking a list of Pairings returned by
        generate_pairings(), and adjusting it in-place to avoid conflicts."""
        if self.options["avoid_conflicts"] == "off":
            return
        function = self.get_option_function("avoid_conflicts", self.AVOID_CONFLICT_FUNCTIONS)
        return function(pairings)

    def _one_up_one_down(self, pairings):
        """We pass the pairings to one_up_one_down.py, then infer annotations
        based on the result."""

        for bracket in pairings.values():
            pairs = [tuple(p.teams) for p in bracket]
            pairs_orig = list(pairs)  # Keep a copy for comparison
            option_names = ["avoid_history", "avoid_institution", "history_penalty", "institution_penalty"]
            options = dict((key, self.options[key]) for key in option_names)
            swapper = OneUpOneDownSwapper(**options)
            pairs_new = swapper.run(pairs)
            swaps = swapper.swaps

            for i, (pairing, orig, new) in enumerate(zip(bracket, pairs_orig, pairs_new)):
                assert(tuple(pairing.teams) == orig)
                assert((i in swaps or i-1 in swaps) == (orig != new))
                if orig != new:
                    if pairing.conflict_hist:
                        pairing.add_flag("1u1d_hist")
                    if pairing.conflict_inst:
                        pairing.add_flag("1u1d_inst")
                    if not (pairing.conflict_hist or pairing.conflict_inst):
                        pairing.add_flag("1u1d_other")
                    pairing.teams = list(new)


class PowerPairedWithAllocatedSidesDrawGenerator(PowerPairedDrawGenerator):
    """Power-paired draw with allocated sides.
    Overrides functions of PowerPairedDrawGenerator where sides need to be constrained.
    All teams must have an 'allocated_side' attribute which must be either
    'aff' or 'neg' (case-sensitive).
    Options are as for PowerPairedDrawGenerator, except that the allowable values
    for "odd_bracket" are:
        "pullup_top"
        "pullup_bottom"
        "pullup_random"
        "intermediate1" - the excess teams in a bracket begin an intermediate bracket,
            which is filled by teams allocated to the other side from lower brackets,
            starting from the top of the next bracket down and pulling up as many
            teams as necessary. This may involve pulling up teams from multiple
            brackets if there aren't enough in the next bracket down.
        "intermediate2" - the excess teams in a bracket begin an intermediate bracket,
            which is filled by teams allocated to the other side from lower brackets.
            However, if there aren't enough teams in the next bracket down, then only
            those teams are pulled up into this intermediate bracket, and the excess
            teams (of the original excess) form a new, lower, intermediate bracket (but
            still higher than the next bracket down). So there can be multiple
            intermediate brackets between two brackets.
    """

    DEFAULT_OPTIONS = {
        "odd_bracket"           : "intermediate1",
        "pairing_method"        : "fold",
        "avoid_conflicts"       : None,
        "pullup_restriction"    : "none",
    }

    def __init__(self, *args, **kwargs):
        super(PowerPairedWithAllocatedSidesDrawGenerator, self).__init__(*args, **kwargs)
        self.check_teams_for_attribute("allocated_side", choices=["aff", "neg"])

    def _make_raw_brackets(self):
        """Returns an OrderedDict mapping bracket names (normally numbers)
        to (unordered) dicts. Each unordered dict has an 'aff' and a 'neg' key,
        each mapping to a list of teams."""
        brackets = OrderedDict()
        teams = list(self.teams)
        while len(teams) > 0:
            top_team = teams.pop(0)
            points = top_team.points
            pool = {"aff": list(), "neg": list()}
            pool[top_team.allocated_side].append(top_team)
            while len(teams) > 0 and teams[0].points == points:
                team = teams.pop(0)
                side = team.allocated_side
                pool[side].append(team)
            brackets[points] = pool
        return brackets

    ODD_BRACKET_FUNCTIONS = {
        "pullup_top"                  : "_pullup_top",
        "pullup_bottom"               : "_pullup_bottom",
        "pullup_random"               : "_pullup_random",
        "intermediate1"               : "_intermediate_brackets_1",
        "intermediate2"               : "_intermediate_brackets_2",
    }

    def _pullup_top(self, brackets):
        self._pullup(brackets, lambda x, num: range(0, num))

    def _pullup_bottom(self, brackets):
        self._pullup(brackets, lambda x, num: range(-num, 0))

    def _pullup_random(self, brackets):
        self._pullup(brackets, lambda x, num: random.sample(list(range(x)), num))

    # Overriding functions for resolving odd brackets:
    def _pullup(self, brackets, indices):
        """'brackets' is what is returned by _make_raw_brackets().
        'pos' is a function taking the number of teams to choose from
        and number of teams required, and returning a list of indices
        for which teams to take as the pullup.
        Operates in-place. Does not remove empty brackets."""

        # Tuples: (teams_list, side, number_needed)
        # List by highest bracket first.
        pullups_needed_for = list()

        for points, pool in brackets.items():

            # First, try to fulfil any pullups needed from higher brackets.
            # There's no guarantee we will have enough teams in this bracket to
            # fulfil all requirements.
            new_pullups_needed_for = list()
            for pullups_needed_teams, side, number_needed in pullups_needed_for:
                # Figure out which team indices we're pulling up.
                if len(pool[side]) < number_needed:
                    # If there are an unsufficient number of teams, pull up all of them
                    # and add to next pullups needed list.
                    pullup_indices = range(len(pool[side]))
                    new_pullups_needed_for.append((pullups_needed_teams, side, number_needed - len(pool[side])))
                else:
                    # Otherwise, pull up the number required.
                    pullup_indices = indices(len(pool[side]), number_needed)

                pullup_teams = list()
                for i in pullup_indices:
                    # Don't use pop, because that mucks up the indices.
                    pullup_team = pool[side][i]
                    self.add_team_flag(pullup_team, "pullup")
                    pullup_teams.append(pullup_team)

                # Now remove those teams from the bracket.
                # Again, avoiding pop, because it changes the indices.
                for team in pullup_teams:
                    pool[side].remove(team)

                # Finally, add our pullup teams to the destination list.
                pullups_needed_teams.extend(pullup_teams)

            # Then, figure out if we need any pullups in *this* bracket.
            aff_surplus = len(pool["aff"]) - len(pool["neg"])  # Could be negative
            if aff_surplus > 0:
                new_pullups_needed_for.append((pool["neg"], "neg", aff_surplus))
            elif aff_surplus < 0:
                new_pullups_needed_for.append((pool["aff"], "aff", -aff_surplus))

            # Assign the new pullups-needed list, then start again!
            pullups_needed_for = new_pullups_needed_for

        if pullups_needed_for:
            raise DrawFatalError("Last bracket still needed pullups!\n" + repr(pullups_needed_for))

    @classmethod
    def _intermediate_brackets_1(cls, brackets):
        """Operates in-place.
        This implements the first intermediate brackets method, where there is at most
        one intermediate bracket between brackets, but may have pullups from multiple
        brackets.
        """
        new = OrderedDict()
        unfilled = OrderedDict()

        for points, pool in brackets.items():

            to_delete_from_unfilled = []

            # First, check for unfilled intermediate brackets
            for unfilled_points, unfilled_pool in unfilled.items():
                aff_surplus = len(unfilled_pool["aff"]) - len(unfilled_pool["neg"])
                if aff_surplus > 0:
                    # Take the top teams from negative pool as appropriate.
                    # Note that there may not be enough teams; if there aren't,
                    # then this line just takes all of them.
                    unfilled_pool["neg"].extend(pool["neg"][:aff_surplus])
                    del pool["neg"][:aff_surplus]
                elif aff_surplus < 0:
                    # Take the top teams from affirmative pool as appropriate.
                    unfilled_pool["aff"].extend(pool["aff"][:-aff_surplus])
                    del pool["aff"][:-aff_surplus]
                # If the bubble now looks good, move it to the main brackets and
                # mark it for deletion from the unfilled buffer.
                if len(unfilled_pool["aff"]) == len(unfilled_pool["neg"]):
                    new[unfilled_points] = unfilled_pool
                    to_delete_from_unfilled.append(unfilled_points)

            # Delete the unfilled brackets tht were marked for deletion
            for unfilled_points in to_delete_from_unfilled:
                del unfilled[unfilled_points]

            # Find lesser and greater of number of aff and neg teams.
            nums_teams = list(map(len, list(pool.values())))
            n = min(nums_teams)
            m = max(nums_teams)

            # Assign the main bracket
            new[points] = {"aff": pool["aff"][:n], "neg": pool["neg"][:n]}

            # Assign the intermediate bracket, if any
            if m > n:
                unfilled[points-0.5] = {"aff": pool["aff"][n:], "neg": pool["neg"][n:]}

        if unfilled:
            raise DrawFatalError("There are still unfilled intermediate brackets!\n" + repr(unfilled))

        # Currently, the brackets are out of order, since e.g. 3.5 would have been
        # inserted after 3 (or maybe even after 2). Let's change that:
        new_sorted = sorted(list(new.items()), key=lambda x: x[0], reverse=True)

        brackets.clear()
        brackets.update(new_sorted)

    @classmethod
    def _intermediate_brackets_2(cls, brackets):
        """Operates in-place.
        This implements the second intermediate brackets method, where all debates
        in the same intermediate bracket have the same number of wins, but there
        might be multiple intermediate brackets between brackets.
        """

        new = OrderedDict()
        unfilled = OrderedDict()
        intermediates = OrderedDict()  # Values are lists of {"aff", "neg"} dicts
        for points, pool in brackets.items():

            to_delete_from_unfilled = []

            # First, check for unfilled intermediate brackets
            for unfilled_points, unfilled_pool in unfilled.items():
                intermediates.setdefault(unfilled_points, list())
                if unfilled_pool["aff"] and unfilled_pool["neg"]:
                    raise DrawFatalError("An unfilled pool unexpectedly had both affirmative and negative teams.")
                elif unfilled_pool["aff"]:
                    # In a new bracket, take the lesser of how many excess affirmative
                    # teams there are, and how many negative teams in the pool we have.
                    num_teams = min(len(unfilled_pool["aff"]), len(pool["neg"]))
                    intermediates[unfilled_points].append({
                        "aff": unfilled_pool["aff"][:num_teams],
                        "neg": pool["neg"][:num_teams],
                    })
                    del unfilled_pool["aff"][:num_teams]
                    del pool["neg"][:num_teams]
                elif unfilled_pool["neg"]:
                    # Take the top teams from affirmative pool as appropriate.
                    num_teams = min(len(unfilled_pool["neg"]), len(pool["aff"]))
                    intermediates[unfilled_points].append({
                        "aff": pool["aff"][:num_teams],
                        "neg": unfilled_pool["neg"][:num_teams],
                    })
                    del pool["aff"][:num_teams]
                    del unfilled_pool["neg"][:num_teams]
                # If we've exhausted the unfilled pool, add all these
                # intermediate brackets to the main list of brackets and mark
                # them for deletion from the unfilled buffer.
                if not unfilled_pool["aff"] and not unfilled_pool["neg"]:
                    num_brackets = len(intermediates[unfilled_points])
                    for i, intermediate_pool in enumerate(intermediates[unfilled_points], start=1):
                        intermediate_points = unfilled_points - i / (num_brackets + 1)
                        new[intermediate_points] = intermediate_pool
                    to_delete_from_unfilled.append(unfilled_points)

            # Delete the unfilled brackets tht were marked for deletion
            for unfilled_points in to_delete_from_unfilled:
                del unfilled[unfilled_points]

            # Find lesser and greater of number of aff and neg teams.
            nums_teams = list(map(len, list(pool.values())))
            n = min(nums_teams)
            m = max(nums_teams)

            # Assign the main bracket
            new[points] = {"aff": pool["aff"][:n], "neg": pool["neg"][:n]}

            # Take note of the excess teams, if any
            if m > n:
                unfilled[points] = {"aff": pool["aff"][n:], "neg": pool["neg"][n:]}

        if unfilled:
            raise DrawFatalError("There are still unfilled intermediate brackets!\n" + repr(unfilled))

        # Currently, the brackets are out of order, since e.g. 3.5 would have been
        # inserted after 3 (or maybe even after 2). Let's change that:
        new_sorted = sorted(list(new.items()), key=lambda x: x[0], reverse=True)

        brackets.clear()
        brackets.update(new_sorted)

    def _intermediate_brackets_with_up_down():
        """This should never be called - the associated option string is removed
        from the allowable list above."""
        raise NotImplementedError("Intermediate brackets with conflict avoidance isn't supported with allocated sides.")

    @staticmethod
    def _pairings(brackets, presort_func):
        pairings = OrderedDict()
        i = 1
        for points, pool in brackets.items():
            assert len(pool["aff"]) == len(pool["neg"])
            bracket = list()
            presort_func(pool)
            for teams in zip(pool["aff"], pool["neg"]):
                pairing = Pairing(teams=teams, bracket=points, room_rank=i)
                bracket.append(pairing)
                i = i + 1
            pairings[points] = bracket
        return pairings

    @classmethod
    def _pairings_slide(cls, brackets):
        def slide(pool):
            pass  # Do nothing
        return cls._pairings(brackets, slide)

    @classmethod
    def _pairings_fold(cls, brackets):
        def fold(pool):
            pool["neg"].reverse()
        return cls._pairings(brackets, fold)

    @classmethod
    def _pairings_random(cls, brackets):
        def shuffle(pool):
            random.shuffle(pool["aff"])
            random.shuffle(pool["neg"])
        return cls._pairings(brackets, shuffle)
