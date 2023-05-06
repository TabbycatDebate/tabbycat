import string

from django.db.models import Count, Q

from tournaments.models import Round
from utils.misc import generate_identifier_string

from .models import Person, Region, Team


def regions_ordered(t):
    """Need to redo the region IDs so the CSS classes will be consistent. This
    assumes there aren't huge amounts of regions, or dramatically different
    regions between tournaments (which holds for big tournaments uses)"""

    regions = Region.objects.all().order_by('name')
    data = [{
        'seq': count % 9,  # There are 9 available colours
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
        debateteam__debate__round__stage=Round.Stage.PRELIMINARY,
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


def populate_code_names(people, length=8, num_attempts=10):
    """Populates the code name field for every instance in the given QuerySet."""
    chars = string.digits

    existing_keys = list(Person.objects.exclude(code_name__isnull=True).values_list('code_name', flat=True))
    for person in people:
        for i in range(num_attempts):
            new_key = generate_identifier_string(chars, length)
            if new_key not in existing_keys:
                person.code_name = new_key
                existing_keys.append(new_key)
                break
        Person.objects.bulk_update(people, ['code_name'])
