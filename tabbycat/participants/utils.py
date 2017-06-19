from django.db.models.expressions import RawSQL

from tournaments.models import Round

from .models import Region, Team


def regions_ordered(t):
    """Need to redo the region IDs so the CSS classes will be consistent. This
    assumes there aren't huge amounts of regions, or dramatically different
    regions between tournaments (which holds for big tournaments uses)"""

    regions = Region.objects.all().order_by('name')
    data = [{
        'seq': count + 1,
        'name': r.name,
        'id': r.id
    } for count, r in enumerate(regions)]
    return data


def annotate_side_count_kwargs(sides, seq):
    """Returns keyword arguments that can be passed into an annotate() call on a
    Team queryset, that will provide side counts for each side given in `sides`.

    Example usage:
        kwargs = annotate_side_count_kwargs(tournament.sides, round.seq)
        teams = tournament.team_set.annotate(**kwargs)
        for team in teams:
            print(team.aff_count, team.neg_count)
    """

    query = """
        SELECT DISTINCT COUNT(draw_debateteam.id)
        FROM draw_debateteam
        JOIN draw_debate ON draw_debateteam.debate_id = draw_debate.id
        JOIN tournaments_round ON draw_debate.round_id = tournaments_round.id
        WHERE participants_team.id = draw_debateteam.team_id
        AND draw_debateteam.side = %s
        AND tournaments_round.stage = %s
        AND tournaments_round.seq <= %s"""

    return {'%s_count' % side: RawSQL(query, (side, Round.STAGE_PRELIMINARY, seq)) for side in sides}


def get_side_counts(teams, sides, seq):
    """Returns a dict where keys are the team IDs in `teams`, and values are
    dicts mapping a side to the number of debates the team has had on that side
    in preliminary rounds, for each side in `sides`, up to and including the
    given seq (of a round)."""

    team_ids = [team.id for team in teams]
    queryset = Team.objects.filter(id__in=team_ids).annotate(
        **annotate_side_count_kwargs(sides, seq))
    return {team.id: {side: getattr(team, '%s_count' % side) for side in sides} for team in queryset}
