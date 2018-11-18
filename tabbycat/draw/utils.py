import logging
from smtplib import SMTPException

from django.core.mail import get_connection
from django.db.models import Count, Q
from django.template import Template
from django.utils.translation import gettext as _

from adjallocation.allocation import AdjudicatorAllocation
from notifications.models import SentMessageRecord
from notifications.utils import TournamentEmailMessage
from options.utils import use_team_code_names
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


def send_mail_to_adjs(round):
    tournament = round.tournament
    draw = round.debate_set_with_prefetches(speakers=False, divisions=False).all()
    use_codes = use_team_code_names(tournament, False)

    subject = Template(tournament.pref('adj_email_subject_line'))
    body = Template(tournament.pref('adj_email_message'))
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
        matchup = debate.matchup_codes if use_codes else debate.matchup
        context = {
            'ROUND': round.name,
            'VENUE': debate.venue.display_name if debate.venue is not None else _("TBA"),
            'PANEL': _assemble_panel(debate.adjudicators.with_positions()),
            'DRAW': matchup
        }

        for adj, pos in debate.adjudicators.with_positions():
            if adj.email is None:
                continue

            context_user = context.copy()
            context_user['USER'] = adj.name
            context_user['POSITION'] = adj_position_names[pos]

            messages.append(TournamentEmailMessage(subject, body, tournament, round, SentMessageRecord.EVENT_TYPE_DRAW, adj, context_user))

    try:
        get_connection().send_messages(messages)
    except SMTPException:
        logger.exception("Failed to send adjudicator e-mails")
        raise
    except ConnectionError:
        logger.exception("Connection error sending adjudicator e-mails")
        raise
    else:
        SentMessageRecord.objects.bulk_create([message.as_sent_record() for message in messages])
