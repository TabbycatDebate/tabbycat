# Liveness calculation functions.
# Contributed by Thevesh Theva and his work on the debatebreaker.blogspot.com.au
# blog and app.

from itertools import accumulate
from math import ceil, factorial, floor


def ncr(n, r):
    try:
        binom = factorial(n) // factorial(r) // factorial(n - r)
    except ValueError:
        binom = 0
    return binom


def get_bp_coefficients(nrounds):
    """Get row of the number of rounds from the quadrinomial coefficients
    triangle (similar to Pascal's triangle).

    See: https://oeis.org/A008287"""

    def get_coefficient(m, k):
        coeff = 0
        for i in range(0, floor(k / 2) + 1):
            coeff += ncr(m, i) * ncr(m, k - 2 * i)
        return coeff

    half_row = [get_coefficient(nrounds, k) for k in range(0, ceil((3 * nrounds + 1) / 2))]

    if nrounds == 0:
        return half_row

    if nrounds % 2 == 1:
        return half_row + half_row[::-1]

    return half_row + half_row[-2::-1]


def liveness_twoteam(is_general, current_round, break_size, total_teams, total_rounds, team_scores=None):

    if total_teams < break_size or (not is_general and len(team_scores) <= break_size):
        return 0, -1  # special case, everyone is safe

    coefficients = [ncr(total_rounds, i) for i in range(total_rounds+1)]
    originals = [total_teams / (2**total_rounds) * coeff for coeff in coefficients]
    ceilings = [ceil(x) for x in originals]
    floors = [floor(x) for x in originals]
    sum_u = list(accumulate(ceilings))  # most teams that can be on i wins
    sum_d = list(accumulate(floors))    # fewest teams that can be on i wins

    rounds_to_go = total_rounds - current_round + 1

    # Last index for which sum_u[i] <= break_size, i.e. lowest guaranteed break.
    # This is the answer for general break categories, and a starting point for
    # limited-eligibility ones.
    index = next((i for i, x in enumerate(sum_u) if x > break_size), total_rounds+1) - 1
    safe = total_rounds - index

    if is_general:
        # First index for which sum_d[i] > break_size, i.e. highest impossible-to-break.
        index = next((i for i, x in enumerate(sum_d) if x > break_size), total_rounds+1)
        highest_nonbreaking = total_rounds - index  # after total_rounds rounds
        dead = highest_nonbreaking - rounds_to_go - 1

    else:
        team_scores.sort(reverse=True)

        # Check if teams in breaking range can still be 'caught' by the team
        # just outside breaking range, and lower the safe score if so.
        safe = min(safe, team_scores[break_size] + rounds_to_go + 1)

        # The dead score is the highest score from which a team can no longer
        # 'catch' a team in the last breaking spot.
        dead = team_scores[break_size-1] - rounds_to_go - 1

    return safe, dead


def liveness_bp(is_general, current_round, break_size, total_teams, total_rounds, team_scores=None):

    if total_teams < break_size or (not is_general and len(team_scores) <= break_size):
        return -1, -1  # special case, everyone is safe

    originals = [total_teams / (4**total_rounds) * coeff for coeff in get_bp_coefficients(total_rounds)]
    ceilings = [ceil(x) for x in originals]
    floors = [floor(x) for x in originals]
    sum_u = list(accumulate(ceilings))  # most teams that can be on i wins
    sum_d = list(accumulate(floors))    # fewest teams that can be on i wins

    max_points = total_rounds * 3
    points_to_go = (total_rounds - current_round + 1) * 3

    # Last index for which sum_u[i] <= break_size, i.e. lowest guaranteed break.
    # This is the answer for general break categories, and a starting point for
    # limited-eligibility ones. Note that the safe score for limited-eligibility
    # categories can be (and usually is) higher than the open safe score. The
    # reason for this is that teams are allowed to opt for the category they
    # wish. Hypothetically, it means that an ESL team on 27 could choose to
    # break in ESL. Since the ESL break is smaller, the safe score is usually
    # higher, ex-ante.
    index = next((i for i, x in enumerate(sum_u) if x > break_size), max_points+1) - 1
    safe = max_points - index

    if is_general:

        # First index for which sum_d[i] > break_size, i.e. highest impossible-to-break.
        index = next((i for i, x in enumerate(sum_d) if x > break_size), max_points+1)
        highest_nonbreaking = max_points - index  # after total_rounds rounds
        dead = highest_nonbreaking - points_to_go - 1

    else:
        team_scores.sort(reverse=True)

        # Check if teams in breaking range can still be 'caught' by the team
        # just outside breaking range, and lower the safe score if so.
        safe = min(safe, team_scores[break_size] + points_to_go + 1)

        # The dead score is the highest score from which a team can no longer
        # 'catch' a team in the last breaking spot.
        if len(team_scores) >= break_size - 1:
            dead = team_scores[break_size-1] - points_to_go - 1
        else:
            dead = -1 # All are live if no team scores exist (i.e. Round 1)

    return safe, dead
