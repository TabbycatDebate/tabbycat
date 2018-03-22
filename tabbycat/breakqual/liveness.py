# Liveness calculation functions.
# Contributed by Thevesh Theva and his work on the debatebreaker.blogspot.com.au
# blog and app.

from math import ceil, factorial, floor
from itertools import accumulate


COEFFICIENTS_BP = [
    [1],
    [1,1,1,1],
    [1,2,3,4,3,2,1],
    [1,3,6,10,12,12,10,6,3,1],
    [1,4,10,20,31,40,44,40,31,20,10,4,1],
    [1,5,15,35,65,101,135,155,155,135,101,65,35,15,5,1],
    [1,6,21,56,120,216,336,456,546,580,546,456,336,216,120,56,21,6,1],
    [1,7,28,84,203,413,728,1128,1554,1918,2128,2128,1918,1554,1128,728,413,203,84,28,7,1],
    [1,8,36,120,322,728,1428,2472,3823,5328,6728,7728,8092,7728,6728,5328,3823,2472,1428,728,322,120,36,8,1],
    [1,9,45,165,486,1206,2598,4950,8451,13051,18351,23607,27876,30276,30276,27876,23607,18351,13051,8451,4950,2598,1206,486,165,45,9,1]
]


def liveness_twoteam(is_general, current_round, break_size, total_teams, total_rounds, team_scores):

    coefficients = [factorial(total_rounds) / factorial(i) / factorial(total_rounds - i)
                    for i in range(total_rounds+1)]
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
        for score in team_scores[0:break_size]:
            if score - team_scores[break_size] > rounds_to_go and score < safe:
                safe = score

        # The dead score is the highest score from which a team can no longer
        # 'catch' a team in the last breaking spot.
        dead = team_scores[break_size-1] - rounds_to_go - 1

    return safe, dead


def liveness_bp(is_general, current_round, break_size, total_teams, total_rounds, team_scores):

    originals = [total_teams / (4**total_rounds) * coeff for coeff in COEFFICIENTS_BP[total_rounds]]
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
        for score in team_scores[0:break_size]:
            if score - team_scores[break_size] > points_to_go and score < safe:
                safe = score

        # The dead score is the highest score from which a team can no longer
        # 'catch' a team in the last breaking spot.
        dead = team_scores[break_size-1] - points_to_go - 1

    return safe, dead
