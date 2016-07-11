from django.db.models.expressions import RawSQL

from tournaments.models import Round

from .models import Region, Team


def regions_ordered(t):
    '''Need to redo the region IDs so the CSS classes will be consistent. This
    assumes there aren't huge amounts of regions, or dramatically different
    regions between tournaments (which holds for big tournaments uses)'''

    regions = Region.objects.all().order_by('name')
    data = [{
        'seq': count + 1,
        'name': r.name,
        'id': r.id
    } for count, r in enumerate(regions)]
    return data


def get_side_counts(teams, position, seq):
    """Returns a dict where keys are the team IDs in `teams`, and values are
    the number of debates the team has had in position `position` in preliminary
    rounds."""

    team_ids = [team.id for team in teams]

    query = """
        SELECT DISTINCT COUNT(draw_debateteam.id)
        FROM draw_debateteam
        JOIN draw_debate ON draw_debateteam.debate_id = draw_debate.id
        JOIN tournaments_round ON draw_debate.round_id = tournaments_round.id
        WHERE participants_team.id = draw_debateteam.team_id
        AND draw_debateteam.position = '{pos:s}'
        AND tournaments_round.stage = '{stage:s}'""".format(
            pos=position, stage=Round.STAGE_PRELIMINARY)
    if seq is not None:
        query += """
        AND tournaments_round.seq <= '{round:d}'""".format(round=seq)

    queryset = Team.objects.filter(id__in=team_ids).annotate(
            side_count=RawSQL(query, ()))

    return {annotated_team.id: annotated_team.side_count for annotated_team in queryset}
