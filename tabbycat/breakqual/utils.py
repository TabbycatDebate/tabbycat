import math

from .models import BreakCategory


def categories_ordered(t):
    categories = BreakCategory.objects.filter(tournament=t).order_by('-is_general', 'name')
    data = [{
        'seq': count + 1,
        'name': bc.name,
        'id': bc.id,
        'size': bc.break_size,
        'teams': bc.team_set.count()
    } for count, bc in enumerate(categories)]
    return data


def determine_liveness(break_category, tournament, round, wins):

    thresholds = calculate_live_thresholds(break_category, tournament, round)
    if wins >= thresholds[0]:
        return True
    elif wins <= thresholds[1]:
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

    coefficients = []
    for i in range(0, total_rounds):
        coefficients.append((factorial(total_rounds)/(factorial(i)*factorial(total_rounds - i))))

    originals = []
    for i in range(0, total_rounds):
        originals.append((total_teams / (2.0**total_rounds) * coefficients[i]))

    ceilings = []
    floors = []

    for i in range(0, total_rounds):
        ceilings.append(math.ceil(originals[i]))
        floors.append(math.floor(originals[i]))

    # Now, we create the arrays of sum totals for each number of wins. This is the data we'll work with.
    sum_o = []
    sum_u = []
    sum_d = []

    sum_o.insert(0, originals[0])
    sum_u.insert(0, ceilings[0])
    sum_d.insert(0, floors[0])

    for i in range(1, total_rounds):
        sum_o.append(originals[i] + sum_o[i-1])
        sum_u.append(ceilings[i] + sum_u[i-1])
        sum_d.append(floors[i] + sum_d[i-1])

    # We now have complete data sets, and can compute the safe score and dead score.
    high_bound = 0
    for i in range(0, total_rounds):
        if sum_u[i] <= break_spots:
            high_bound = total_rounds-i

    low_bound = 0
    for i in range(0, total_rounds):
        if sum_d[i] <= break_spots:
            low_bound = total_rounds-i-1

    # If a team is on this score, breaking is guaranteed.
    safe = high_bound
    # If a team is on this score, breaking is impossible.
    dead = low_bound - (total_rounds - (current_round - 1)) - 1

    return safe, dead
