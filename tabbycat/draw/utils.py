from django.db.models.expressions import RawSQL

from participants.models import Team
from tournaments.models import Round


def annotate_npullups(teams, until):
    """Adds an `npullup` attribute to every team in `teams` denoting how many
    teams the team has been pulled up (i.e., has a pullup flag in an associated
    DebateTeam object)."""

    team_ids = [team.id for team in teams]

    query = RawSQL("""
        SELECT DISTINCT COUNT(draw_debateteam.id)
        FROM draw_debateteam
        JOIN draw_debate ON draw_debateteam.debate_id = draw_debate.id
        JOIN tournaments_round ON draw_debate.round_id = tournaments_round.id
        WHERE participants_team.id = draw_debateteam.team_id
        AND draw_debateteam.flags::text ~ '(^|,)pullup($|,)'
        AND tournaments_round.stage = %s
        AND tournaments_round.seq <= %s""",
        (Round.STAGE_PRELIMINARY, until.seq)
    )
    annotated = Team.objects.filter(id__in=team_ids).annotate(npullups=query)
    npullups_by_team_id = {team.id: team.npullups for team in annotated}

    for team in teams:
        team.npullups = npullups_by_team_id.get(team.id, 0)
