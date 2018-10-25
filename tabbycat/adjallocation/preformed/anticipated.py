"""Functions for computing an anticipated draw."""

import itertools

from breakqual.utils import calculate_live_thresholds, determine_liveness
from participants.models import Team
from standings.teams import TeamStandingsGenerator


def calculate_anticipated_draw(round):
    """Calculates an anticipated draw for the next round, based on the draw for
    the last round. Returns a list of tuples
        `(bracket_min, bracket_max, liveness)`,
    being the minimum and maximum brackets possible for that room, and the
    maximum number of teams that might be live in it. If the previous round's
    draw doesn't exist, it will just return an empty list.

    Procedure:
      1. Take the (actual) draw of the last round, with team point standings.
      2. For each room, compute a (min, max) of outcomes for each team.
      3. Take the min, divide into rooms to make the `bracket_min` for each room.
      4. Take the max, divide into rooms to make the `bracket_max` for each room.

    `round` should be the round for which you want an anticipated draw (the
    "next round").
    """

    nteamsindebate = 4 if round.tournament.pref('teams_in_debate') == 'bp' else 2

    if round.prev is None:
        # Special case: If this is the first round, everyone will be on zero.
        # Just take all teams, rounded down -- if this is done, it'll typically
        # be done before availability is locked down.
        npanels = round.tournament.team_set.count() // nteamsindebate
        return [(0, 0) for i in range(npanels)]

    # 1. Take the (actual) draw of the last round, with team point standings.
    debates = round.debate_set_with_prefetches(ordering=('room_rank',),
        teams=True, adjudicators=False, speakers=False, divisions=False, venues=False)
    teams = Team.objects.filter(debateteam__debate__round=round)
    generator = TeamStandingsGenerator(('points',), ())
    standings = generator.generate(teams, round=round.prev)

    # 2. Compute a (min, max) of outcomes for each team
    team_points_after = []
    for debate in debates:
        points_now = [info.metrics['points'] for info in standings.get_standings(debate.teams)]
        highest = max(points_now)
        lowest = min(points_now)

        # Most cases will be single-point rooms or rooms with pull-ups from only
        # one bracket; in these cases it's easy to prove this closed-form
        # guarantee for what the teams in that room will look like afterwards.
        if highest - lowest <= 1:
            points_after = [(lowest+i, highest+i) for i in range(nteamsindebate)]

        # For more complicated rooms (e.g. [9, 8, 8, 7]), it gets harder; just
        # use brute force. For few enough rooms this won't be too bad a hit.
        else:
            possible_outcomes = []
            for result in itertools.permutations(range(nteamsindebate)):
                outcome = [n + r for n, r in zip(points_now, result)]
                outcome.sort(reverse=True)
                possible_outcomes.append(outcome)
            points_after = [(min(team_after), max(team_after)) for team_after in zip(*possible_outcomes)]

        team_points_after.extend(points_after)

    # 3. Take the min, divide into rooms to make the `bracket_min` for each room.
    # 4. Take the max, divide into rooms to make the `bracket_max` for each room.
    lowers, uppers = [sorted(x, reverse=True) for x in zip(*team_points_after)]
    brackets_min = [max(r) for r in zip(*([iter(lowers)] * nteamsindebate))]
    brackets_max = [max(r) for r in zip(*([iter(uppers)] * nteamsindebate))]

    open_category = round.tournament.breakcategory_set.filter(is_general=True).first()
    if open_category:
        live_thresholds = calculate_live_thresholds(open_category, round.tournament, round)
        liveness_by_lower = [determine_liveness(live_thresholds, x) for x in lowers]
        liveness_by_upper = [determine_liveness(live_thresholds, x) for x in uppers]
        liveness_by_team = [x == 'live' or y == 'live' for x, y in zip(liveness_by_lower, liveness_by_upper)]
        liveness = [x.count(True) for x in zip(*([iter(liveness_by_team)] * nteamsindebate))]

    return zip(brackets_min, brackets_max, liveness)
