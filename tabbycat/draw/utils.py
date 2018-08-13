import logging

from django.db.models import Count, Q
from django.utils.translation import gettext as _

from adjallocation.allocation import AdjudicatorAllocation
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


def send_mail_to_adjs(subject, message, round):
    from notifications.models import SentMessageRecord
    from notifications.utils import TournamentEmailMessage

    tournament = round.tournament
    draw = round.debate_set_with_prefetches(speakers=False, divisions=False).all()

    messages = []

    adj_position_names = {
        AdjudicatorAllocation.POSITION_CHAIR: _("the chair"),
        AdjudicatorAllocation.POSITION_ONLY: _("the only"),
        AdjudicatorAllocation.POSITION_PANELLIST: _("a panellist"),
        AdjudicatorAllocation.POSITION_TRAINEE: _("a trainee"),
    }

    def _assemble_panel(adjs):
        adj_string = []
        for adj, pos in adjs:
            adj_string.append("%s (%s)" % (adj.name, adj_position_names[pos]))

        return ", ".join(adj_string)

    for debate in draw:
        context = {
            'ROUND': round.name,
            'VENUE': debate.venue.name,
            'PANEL': _assemble_panel(debate.adjudicators.with_positions()),
            'DRAW': debate.matchup
        }

        for adj, pos in debate.adjudicators.with_positions():
            if adj.email is None:
                continue

            context['USER'] = adj.name
            context['POSITION'] = adj_position_names[pos]

            messages.append(TournamentEmailMessage(subject, message, tournament, round, SentMessageRecord.EVENT_TYPE_DRAW, adj, context))

    return messages
