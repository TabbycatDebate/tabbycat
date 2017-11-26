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
    if safe is None and dead is None:
        return '?'
    elif wins >= safe:
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
    total_teams = bc.team_set.count()
    total_rounds = tournament.prelim_rounds().count()
    break_cat_scores = get_scores(bc) if not bc.is_general else None

    logger.info("LIVENESS: Calculating for tournament %s round %s / %s with %s spots and %s teams" % (tournament.short_name, round.seq, total_rounds, bc.break_size, total_teams))

    if bc.break_size <= 1:
        return None, None # Bad input
    elif bc.break_size == total_teams:
        return 0, 0 # All teams break
    elif total_teams == 0:
        return None, None
    elif tournament.pref('teams_in_debate') == 'bp':
        return calculate_bp(bc.is_general, round.seq, bc.break_size,
                            total_teams, total_rounds, break_cat_scores)
    else:
        return calculate_2vs2(bc.is_general, round.seq, bc.break_size,
                              total_teams, total_rounds, break_cat_scores)


def calculate_2vs2(is_general, current_round, break_spots, total_teams,
                   total_rounds, break_cat_scores):
    """ Create array of binomial coefficients, then create arrays of raw decimal
    data, upper bounds, and lower bounds. Contributed by Thevesh Theva and
    his work on the debatebreaker.blogspot.com.au blog and app"""
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
    if is_general:
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
        logger.info("\t(general): Safe is %s and dead is %s" % (safe, dead))
        return safe, dead
    else:
        # The safe score for the ESL/EFL category is tricky. First we get a best
        # possible apriori safe score using the  earlier binomial distribution.
        safe = 0
        for i in range(0, total_rounds + 1):
            if sum_u[i] <= break_spots:
                safe = total_rounds-i

        if len(break_cat_scores) <= break_spots:
            return 0, 0

        # Now, we improve upon our safe score using the actual data.
        # Check if teams in breaking range can still be 'caught' by the team just
        # outside breaking range. This gives us the best possible safe score.
        for i in range(0, break_spots + 1):
            if break_cat_scores[i] - break_cat_scores[break_spots] > total_rounds - current_round + 1:
                safe = break_cat_scores[i]

        # The dead score for the ESL category is easy to calculate.
        # This function just defines the score such that a team can no longer
        # 'catch' a team in the last breaking spot.
        dead = break_cat_scores[break_spots - 1] - (total_rounds - current_round + 1) - 1
        logger.info("\t(non-general): Safe is %s and dead is %s" % (safe, dead))
        return safe, dead


def calculate_bp(is_general, current_round, break_spots, total_teams,
                 total_rounds, break_cat_scores):
    """Based on Tushar Kanakagiri's algorithm in
    https://github.com/tusharkanakagiri/BreakCalculator """

    # TODO: integrate below sanity checking into the 2vs2 method also
    if is_general is False:
        return None, None # No ESL/EFL support yet

    def get_high_ranges(scores, total_rounds, total_teams):
        for i in range(0, total_rounds):
            for j in range(0, total_teams, 4):
                scores[j + 1] += 1
                scores[j + 2] += 2
                scores[j + 3] += 3
            scores.sort()
        return scores

    def get_low_ranges(scores, total_rounds, total_teams):
        for i in range(0, total_rounds):
            for j in range(0, total_teams, 4):
                scores[j] += 3
                scores[j + 1] += 2
                scores[j + 2] += 1
            scores.sort()
        return scores

    def get_thresholds(total_teams, break_spots, scores):
        cur_val = total_teams - 1
        prev_val = total_teams - 1
        cur_count = 1
        total_count = 1
        i = total_teams - 2
        not_found = True

        while i >= 0 and not_found:
            cur_val = i

            if scores[prev_val] == scores[cur_val]:
                cur_count += 1
            else:
                cur_count = 1

            total_count += 1
            if total_count == break_spots:
                not_found = False

            prev_val = cur_val
            i -= 1

        safe_at_break = scores[prev_val + cur_count]
        marginal_at_break = scores[cur_val]
        return safe_at_break, marginal_at_break

    # Round up teams to nearest multiple of four
    floored_teams = int(math.ceil(total_teams / 4.0)) * 4
    high_scores = get_high_ranges([0] * floored_teams, total_rounds, total_teams)
    low_scores = get_low_ranges([0] * floored_teams, total_rounds, total_teams)

    high_safe, high_marginal = get_thresholds(total_teams, break_spots, high_scores)
    low_safe, low_marginal = get_thresholds(total_teams, break_spots, low_scores)

    logger.info("\tBest case calculated as safe %s marginal %s" % (high_safe, high_marginal))
    logger.info("\tWorst case calculated as safe %s marginal %s" % (low_safe, low_marginal))

    safe = max(high_safe, low_safe) # Choose worst case
    final_dead = min(high_marginal, low_marginal) # Choose best case
    possible_points_gain = (total_rounds - current_round + 1) * 3
    dead = final_dead - possible_points_gain - 1

    logger.info("\tSafe is %s and dead is %s" % (safe, dead))

    return safe, dead
