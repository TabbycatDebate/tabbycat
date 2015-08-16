from django.db.models import Sum
from results.models import TeamScore
import random

def _add_ranks(standings, key):
    """Adds the 'rank' attribute to each team in 'standings'. Teams in
    'standings' are assumed to be correctly ordered. 'key' must be a function
    taking a team and returning some metric. Teams are on the same rank if their
    keys are the same."""
    prev_key = None
    current_rank = 0
    for i, team in enumerate(standings, start=1):
        this_key = key(team)
        if this_key != prev_key:
            current_rank = i
            prev_key = this_key
        team.rank = current_rank

def _add_subranks(standings, key):
    """Adds the 'subrank' attribute to each team in 'standings'. Works as for
    _add_ranks, but ranks reset within each points bracket."""
    prev_key = None
    prev_points = None
    current_rank = 0
    counter = 0
    for team in standings:
        if team.points != prev_points:
            counter = 1
            prev_points = team.points
        this_key = key(team)
        if this_key != prev_key:
            current_rank = counter
            prev_key = this_key
        team.subrank = current_rank
        counter += 1
    return standings

def ranked_team_standings(teams, *args, **kwargs):
    standings = annotate_team_standings(teams, *args, **kwargs)
    _add_ranks(standings, lambda t: (t.points, t.speaker_score))
    return standings

def division_ranked_team_standings(teams, *args, **kwargs):
    standings = annotate_team_standings(teams, *args, **kwargs)
    _add_ranks(standings, lambda t: (t.points, t.margins, t.speaker_score))
    return standings

def subranked_team_standings(teams, *args, **kwargs):
    standings = annotate_team_standings(teams, *args, **kwargs)
    _add_subranks(standings, lambda t: t.speaker_score)
    return standings

def annotate_team_standings(teams, round=None, tournament=None, shuffle=False):
    """Accepts a QuerySet, returns a list.
    If 'shuffle' is True, it shuffles the list before sorting so that teams that
    are equal are in random order. This should be turned on for draw generation,
    and turned off for display."""
    # This is what might be more concisely expressed, if it were permissible
    # in Django, as:
    # teams = teams.annotate_if(
    #     dict(points = models.Count('debateteam__teamscore__points'),
    #     speaker_score = models.Count('debateteam__teamscore__score')),
    #     dict(debateteam__teamscore__ballot_submission__confirmed = True)
    # )
    # That is, it adds up all the wins and points of each team on CONFIRMED
    # ballots and adds them as columns to the table it returns.
    # The standings include only preliminary rounds.

    from tournaments.models import Round

    EXTRA_QUERY = """
        SELECT DISTINCT SUM({field:s})
        FROM "results_teamscore"
        JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        JOIN "draws_debateteam" ON "results_teamscore"."debate_team_id" = "draws_debateteam"."id"
        JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
        JOIN "tournaments_round" ON "draws_debate"."round_id" = "tournaments_round"."id"
        WHERE "results_ballotsubmission"."confirmed" = True
        AND "draws_debateteam"."team_id" = "debate_team"."id"
        AND "tournaments_round"."stage" = '""" + str(Round.STAGE_PRELIMINARY) + "\'"

    if round is not None:
        EXTRA_QUERY += """AND "tournaments_round"."seq" <= {round:d}""".format(round=round.seq)

    teams = teams.extra({
        "points": EXTRA_QUERY.format(field="points"),
        "speaker_score": EXTRA_QUERY.format(field="score"),
        "margins": EXTRA_QUERY.format(field="margin"),
    }).distinct()

    # Extract which rule to use from the tournament config
    if round is not None and tournament is None:
        tournament = round.tournament
    if tournament is None:
        raise TypeError("A tournament or a round must be specified.")
    rule = tournament.config.get('team_standings_rule')

    if rule == "australs":

        if shuffle:
            sorted_teams = list(teams)
            random.shuffle(sorted_teams) # shuffle first, so that if teams are truly equal, they'll be in random order
            sorted_teams.sort(key=lambda x: (x.points, x.speaker_score), reverse=True)
            return sorted_teams
        else:
            teams = teams.order_by("-points", "-speaker_score")
            return list(teams)

    elif rule == "nz":

        # Add draw strength annotation.
        for team in teams:
            draw_strength = 0
            # Find all teams that they've faced.
            debateteam_set = team.debateteam_set.all()
            if round is not None:
                debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
            for dt in debateteam_set:
                # Can't just use dt.opposition.team.points, as dt.opposition.team isn't annotated.
                draw_strength += teams.get(id=dt.opposition.team.id).points
            team.draw_strength = draw_strength

        def who_beat_whom(team1, team2):
            """Returns a positive value if team1 won more debates, a negative value
            if team2 won more, 0 if the teams won the same number against each other
            or haven't faced each other."""
            # Find all debates between these two teams
            def get_wins(team, other):
                ts = TeamScore.objects.filter(
                    ballot_submission__confirmed=True,
                    debate_team__team=team,
                    debate_team__debate__debateteam__team=other).aggregate(Sum('points'))
                return ts["points__sum"]
            wins1 = get_wins(team1, team2)
            wins2 = get_wins(team2, team1)
            # Print this to the logs, just so we know it happened
            print "who beat whom, {0} vs {1}: {2} wins against {3}".format(team1, team2, wins1, wins2)
            return cmp(wins1, wins2)

        def cmp_teams(team1, team2):
            """Returns 1 if team1 ranks ahead of team2, -1 if team2 ranks ahead of team1,
            and 0 if they rank the same. Requires access to teams, so that it knows whether
            it can apply who-beat-whom."""
            # If there are only two teams on this number of points, or points/speakers,
            # or points/speaks/draw-strength, then use who-beat-whom.
            def two_teams_left(key):
                return key(team1) == key(team2) and len(filter(lambda x: key(x) == key(team1), teams)) == 2
            if two_teams_left(lambda x: x.points) or two_teams_left(lambda x: (x.points, x.speaker_score)) \
                    or two_teams_left(lambda x: (x.points, x.speaker_score, x.draw_strength)):
                winner = who_beat_whom(team1, team2)
                if winner != 0: # if this doesn't help, keep going
                    return winner
            key = lambda x: (x.points, x.speaker_score, x.draw_strength)
            return cmp(key(team1), key(team2))

        sorted_teams = list(teams)
        if shuffle:
            random.shuffle(sorted_teams) # shuffle first, so that if teams are truly equal, they'll be in random order
        sorted_teams.sort(cmp=cmp_teams, reverse=True)
        return sorted_teams

    elif rule == "wadl":
        # Sort by points
        teams = teams.order_by("-points", "-margins", "-speaker_score")
        print "%s total teams" % len(teams)
        teams = [t for t in teams if (t.margins != 0 and t.points > 0)]

        print "%s culled teams" % len(teams)

        # Sort by division rank
        divisions = tournament.division_set.all()
        for division in divisions:
            rank_count = 1
            for team in teams:
                if team.division == division:
                    team.division_rank = rank_count # Assign their in-division rank
                    rank_count = rank_count + 1

        # Sort division winners
        #final_teams = sorted(teams, key = lambda x: (-x.points, -x.margins, -x.speaker_score))
        return teams

    else:
        raise ValueError("Invalid team_standings_rule option: {0}".format(rule))

