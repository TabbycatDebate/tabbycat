import math
import logging

from django.db.models import Sum

from standings.teams import TeamStandingsGenerator

from .models import BreakCategory

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


def categories_ordered(t):
    categories = BreakCategory.objects.filter(
        tournament=t).order_by('-is_general', 'name')
    data = [{
        'seq': count + 1,
        'open': bc.is_general,
        'name': bc.name,
        'id': bc.id,
        'size': bc.break_size,
        'teams': bc.team_set.count(),
        'scores': get_scores(bc) if not bc.is_general else None
    } for count, bc in enumerate(categories)]

    return data


def determine_liveness(thresholds, wins):
    """thresholds should be calculated using calculate_live_thresholds."""
    safe, dead = thresholds
    if wins >= safe:
        return True
    elif wins <= dead:
        return False
    else:
        return None


def calculate_live_thresholds(break_category, tournament, round):
    """ Create array of binomial coefficients, then create arrays of raw decimal
    data, upper bounds, and lower bounds. Contributed by Thevesh Theva and
    his work on the debatebreaker.blogspot.com.au blog and app"""

    def factorial(n):
        if n == 0:
            return 1
        else:
            return n * factorial(n-1)

    current_round = round.seq
    break_spots = break_category['size']
    total_teams = break_category['teams']
    total_rounds = tournament.prelim_rounds(until=round).count()
    break_cat_scores = break_category['scores']

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
    if break_category['open']:
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
