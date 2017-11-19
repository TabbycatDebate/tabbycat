import math
import logging

from django.db.models import Count, Sum
from django.db.models.expressions import RawSQL

from standings.teams import TeamStandingsGenerator

logger = logging.getLogger(__name__)


def get_breaking_teams(category, prefetch=(), rankings=('rank',)):
    """Returns a list of StandingInfo objects, one for each team, with one
    additional attribute populated: for each StandingInfo `tsi`,
    `tsi.break_rank` is the rank of the team out of those that are in the break.

    `prefetch` is passed to `prefetch_related()` in the Team query.
    `rankings` is passed to `rankings` in the TeamStandingsGenerator.
    """
    teams = category.breaking_teams.all().prefetch_related(*prefetch)
    metrics = category.tournament.pref('team_standings_precedence')
    generator = TeamStandingsGenerator(metrics, rankings)
    standings = generator.generate(teams)

    breakingteams_by_team_id = {bt.team_id: bt for bt in category.breakingteam_set.all()}

    for tsi in standings:

        bt = breakingteams_by_team_id[tsi.team.id]
        if bt.break_rank is None:
            if bt.remark:
                tsi.break_rank = "(" + bt.get_remark_display().lower() + ")"
            else:
                tsi.break_rank = "<no rank, no remark>"
        else:
            tsi.break_rank = bt.break_rank

    return standings


def get_scores(bc):
    teams = bc.team_set.filter(
        debateteam__teamscore__ballot_submission__confirmed=True
    ).annotate(score=Sum('debateteam__teamscore__points'))
    scores = sorted([team.score for team in teams], reverse=True)
    return scores


def breakcategories_with_counts(tournament):
    breaking = RawSQL("""
        SELECT DISTINCT COUNT(breakqual_breakingteam.id) FROM breakqual_breakingteam
        WHERE breakqual_breakcategory.id = breakqual_breakingteam.break_category_id
        AND breakqual_breakingteam.break_rank IS NOT NULL
    """, ())
    excluded = RawSQL("""
        SELECT DISTINCT COUNT(breakqual_breakingteam.id) FROM breakqual_breakingteam
        WHERE breakqual_breakcategory.id = breakqual_breakingteam.break_category_id
        AND breakqual_breakingteam.break_rank IS NULL
    """, ())
    categories = tournament.breakcategory_set.annotate(
        eligible=Count('team', distinct=True),
        breaking=breaking,
        excluded=excluded
    )
    for category in categories:
        category.nonbreaking = category.eligible - category.breaking
    return categories


def liveness(self, team, teams_count, prelims, current_round):
    live_info = {'text': team.wins_count, 'tooltip': ''}

    # The actual calculation should be shifed to be a cached method on
    # the relevant break category
    highest_liveness = 3
    for bc in team.break_categories.all():
        import random
        status = random.choice([1,2,3])
        highest_liveness = 3
        if status is 1:
            live_info['tooltip'] += 'Definitely in for the %s break<br>test' % bc.name
            if highest_liveness != 2:
                highest_liveness = 1  # Live not ins are the most important highlight
        elif status is 2:
            live_info['tooltip'] += 'Still live for the %s break<br>test' % bc.name
            highest_liveness = 2
        elif status is 3:
            live_info['tooltip'] += 'Cannot break in %s break<br>test' % bc.name

    if highest_liveness is 1:
        live_info['class'] = 'bg-success'
    elif highest_liveness is 2:
        live_info['class'] = 'bg-warning'

    return live_info


def determine_liveness(thresholds, wins):
    """ Thresholds should be calculated using calculate_live_thresholds."""
    safe, dead = thresholds
    if wins >= safe:
        return 'safe'
    elif wins <= dead:
        return 'dead'
    else:
        return 'live'


def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)


def calculate_live_thresholds(bc, tournament, round):
    """ Create array of binomial coefficients, then create arrays of raw decimal
    data, upper bounds, and lower bounds. Contributed by Thevesh Theva and
    his work on the debatebreaker.blogspot.com.au blog and app"""

    total_teams = bc.team_set.count()
    total_rounds = tournament.prelim_rounds(until=round).count()
    break_cat_scores = get_scores(bc) if not bc.is_general else None
    if tournament.pref('teams_in_debate') == 'bp':
        return calculate_bp(bc, round.seq, bc.break_size,
            total_teams, total_rounds, break_cat_scores)
    else:
        return calculate_2vs2(bc, round.seq, bc.break_size,
            total_teams, total_rounds, break_cat_scores)


def calculate_2vs2(bc, current_round, break_spots, total_teams,
                   total_rounds, break_cat_scores):
    # Create array of binomial coefficients, then create arrays of raw
    # decimal data, upper bounds, and lower bounds
    coefficients = []
    for i in range(0, total_rounds + 1):
        coeff = (factorial(total_rounds) / (factorial(i) * factorial(total_rounds - i)))
        coefficients.append(coeff)

    originals = []
    for i in range(0,total_rounds + 1):
        originals.append((total_teams / (2.0**total_rounds) * coefficients[i]))

    ceilings = []
    floors = []
    for i in range(0, total_rounds + 1):
        ceilings.append(math.ceil(originals[i]))
        floors.append(math.floor(originals[i]))

    # Now, we create the cumulative totals for each number of wins.
    # This is the data we'll work with.
    sum_o = []
    sum_u = []
    sum_d = []
    sum_o.insert(0, originals[0])
    sum_u.insert(0, ceilings[0])
    sum_d.insert(0, floors[0])

    for i in range(1, total_rounds + 1):
        sum_o.append(originals[i] + sum_o[i-1])
        sum_u.append(ceilings[i] + sum_u[i-1])
        sum_d.append(floors[i] + sum_d[i-1])

    # We now have complete data sets, and can compute the safe score and dead
    # scores for any category we want.
    if bc.is_general:
        high_bound = 0
        for i in range(0, total_rounds + 1):
            if sum_u[i] <= break_spots:
                high_bound = total_rounds-i

        low_bound = 0
        for i in range(0, total_rounds + 1):
            if sum_d[i] <= break_spots:
                low_bound = total_rounds-i-1

        safe = high_bound
        dead = low_bound - (total_rounds - (current_round - 1)) - 1
        return safe, dead
    else:
        # The safe score for the ESL/EFL category is trick. First, we get a best
        # possible apriori safe score using the  earlier binomial distribution.
        safe = 0
        for i in range(0, total_rounds + 1):
            if sum_u[i] <= break_spots:
                safe = total_rounds-i

        if len(break_cat_scores) <= break_spots:
            return 0, 0

        # Now, we improve upon our safe score using the actual data.
        # Check if teams in breaking range can still be 'caught'by the team just
        # outside breaking range. This gives us the best possible safe score.
        for i in range(0, break_spots + 1):
            if break_cat_scores[i] - break_cat_scores[break_spots] > total_rounds - current_round + 1:
                safe = break_cat_scores[i]

        # The dead score for the ESL category is easy to calculate.
        # This function just defines the score such that a team can no longer
        # 'catch' a team in the last breaking spot.
        dead = break_cat_scores[break_spots-1] - (total_rounds - current_round + 1) - 1
        return safe, dead


def calculate_bp(bc, current_round, break_spots, total_teams,
                 total_rounds, break_cat_scores):

    a = []
    i = 0
    j = 0

    while(i < total_teams):
        a[i] = 0
        i += 1

    for i in range(0, total_rounds):
        for j in range(0, total_teams, 4):
            a[j + 1] += 1
            a[j + 2] = a[j + 2] + 2
            a[j + 3] = a[j + 3] + 3

        # TODO a.sort(function(a, b) { return a-b }
        sorted(a)

    prev_val = total_teams - 1
    cur_val = total_teams - 1
    cur_count = 1
    total_count = 1
    not_found = 1
    i = total_teams - 2

    if break_spots == 1:
        pass
        # document.getElementById("result1").innerHTML = "All teams greater than "+a[cur_val]+" break";
    elif break_spots == 0:
        pass
        # document.getElementById("result1").innerHTML = "No teams break";
    elif break_spots == total_teams:
        pass
        # document.getElementById("result1").innerHTML = "All teams break";
    else:
        while i >= 0 and not_found:
            cur_val = i
            if a[prev_val] == a[cur_val]:
                cur_count += 1
            else:
                cur_count = 1
            total_count += 1
            if total_count == break_spots:
                not_found = 0
            prev_val = cur_val
            i -= 1
        # document.getElementById("result1").innerHTML = "Case 1 : All teams on "+a[prev_val+cur_count]+" points and higher break and "+cur_count+" teams on "+a[cur_val]+" points will break";

    i = 0
    j = 0
    while i < total_teams:
        a[i] = 0
        i += 1

    for i in range(0, total_rounds):
        for i in range(0, total_rounds, 4):
            a[j] = a[j] + 3
            a[j+1] = a[j+1] + 2
            a[j+2] = a[j+2] + 1

        # TODO a.sort(function(a, b){ return a-b });
        sorted(a)

    prev_val = total_teams - 1
    cur_val = total_teams - 1
    cur_count = 1
    total_count = 1
    not_found = 1
    i = total_teams-2

    if break_spots == 1:
        pass
        # document.getElementById("result2").innerHTML = "All teams greater than "+a[cur_val]+" break";
    elif break_spots == 0:
        pass
        # document.getElementById("result2").innerHTML = "No teams break";
    elif break_spots == total_teams:
        pass
        # document.getElementById("result2").innerHTML = "All teams break";
    else:
        while i >= 0 and not_found:
            cur_val = i
            if a[prev_val] == a[cur_val]:
                cur_count += 1
            else:
                cur_count = 1
            total_count += 1
            if total_count == break_spots:
                not_found = 0
            prev_val = cur_val
            i -= 1
        # document.getElementById("result2").innerHTML = "Case 2 : All teams on "+a[prev_val+cur_count]+" points and higher break and "+cur_count+" teams on "+a[cur_val]+" points will break";

    return None
