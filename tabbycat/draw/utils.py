import logging

from django.db.models import Count, Q

from participants.models import Team
from tournaments.models import Round

logger = logging.getLogger(__name__)


def annotate_npullups(teams, until):
    """Adds an `npullup` attribute to every team in `teams` denoting how many
    teams the team has been pulled up (i.e., has a pullup flag in an associated
    DebateTeam object)."""

    team_ids = [team.id for team in teams]

    query = Count('debateteam', distinct=True, filter=Q(
        debateteam__flags__regex=r'(^|,)pullup($|,)',
        debateteam__debate__round__stage=Round.STAGE_PRELIMINARY,
        debateteam__debate__round__seq__lte=until.seq
    ))

    annotated = Team.objects.filter(id__in=team_ids).annotate(npullups=query)
    npullups_by_team_id = {team.id: team.npullups for team in annotated}

    for team in teams:
        team.npullups = npullups_by_team_id.get(team.id, 0)
