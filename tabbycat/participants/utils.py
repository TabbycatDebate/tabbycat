from django.db.models import Count, Q

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
        'id': r.id,
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

    return {'%s_count' % side: Count('debateteam', filter=Q(
        debateteam__side=side,
        debateteam__debate__round__stage=Round.STAGE_PRELIMINARY,
        debateteam__debate__round__seq__lte=seq), distinct=True,
    ) for side in sides}


def get_side_history(teams, sides, seq):
    """Returns a dict where keys are the team IDs in `teams`, and values are
    lists of integers of the same length as `sides`, being the number of debates
    that team has had on the corresponding side in `sides`, up to and including
    the given `seq` (of a round)."""
    team_ids = [team.id for team in teams]
    queryset = Team.objects.filter(id__in=team_ids).prefetch_related(
        'debateteam_set__debate__round',
    ).annotate(
        **annotate_side_count_kwargs(sides, seq))
    return {team.id: [getattr(team, '%s_count' % side) for side in sides] for team in queryset}
