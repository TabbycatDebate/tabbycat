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
        category.nonbreaking = category.eligible - category.breaking - category.excluded
    return categories


def liveness(self, team, teams_count, prelims, current_round):
    live_info = {'text': team.wins_count, 'tooltip': ''}

    # The actual calculation should be shifed to be a cached method on
    # the relevant break category

    highest_liveness = 3
    for bc in team.break_categories.all():
        # print(bc.name, bc.break_size)
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


def calculate_live_thresholds(bc, tournament, round):
    """ Create array of binomial coefficients, then create arrays of raw decimal
    data, upper bounds, and lower bounds. Contributed by Thevesh Theva and
    his work on the debatebreaker.blogspot.com.au blog and app"""

    def factorial(n):
        if n == 0:
            return 1
        else:
            return n * factorial(n-1)

    current_round = round.seq
    break_spots = bc.break_size
    total_teams = bc.team_set.count()
    total_rounds = tournament.prelim_rounds(until=round).count()
    break_cat_scores = get_scores(bc) if not bc.is_general else None

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
