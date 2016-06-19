from breakqual.models import BreakingTeam
from standings.teams import TeamStandingsGenerator


def get_draw_with_standings(round):
    draw = round.get_draw()

    if round.prev is None:
        return None, draw

    teams = round.tournament.team_set.select_related('institution')
    metrics = round.tournament.pref('team_standings_precedence')
    generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'))
    standings = generator.generate(teams, round=round.prev)

    for debate in draw:
        aff_standing = standings.get_standing(debate.aff_team)
        neg_standing = standings.get_standing(debate.neg_team)
        debate.metrics = [(a, n) for a, n in zip(aff_standing.itermetrics(), neg_standing.itermetrics())]
        if round.is_break_round:
            debate.aff_breakrank = BreakingTeam.objects.get(
                break_category=round.break_category,
                team=debate.aff_team.id).break_rank
            debate.neg_breakrank = BreakingTeam.objects.get(
                break_category=round.break_category,
                team=debate.neg_team.id).break_rank
        else:
            if "points" in standings.metric_keys:
                debate.aff_is_pullup = abs(aff_standing.metrics["points"] - debate.bracket) >= 1
                debate.neg_is_pullup = abs(neg_standing.metrics["points"] - debate.bracket) >= 1
            debate.aff_subrank = aff_standing.rankings["subrank"]
            debate.neg_subrank = neg_standing.rankings["subrank"]

    return standings, draw
