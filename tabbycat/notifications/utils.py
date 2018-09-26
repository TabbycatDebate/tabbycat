import logging
from smtplib import SMTPException

from django.conf import settings
from django.core import mail
from django.db.models import Exists, OuterRef
from django.template import Context, Template
from django.utils.translation import gettext as _

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from results.result import DebateResult
from options.utils import use_team_code_names
from participants.prefetch import populate_win_counts
from tournaments.models import Round, Tournament

from .models import SentMessageRecord

logger = logging.getLogger(__name__)


class TournamentEmailMessage(mail.EmailMessage):
    def __init__(self, subject, body, tournament=None, round=None, event=None, person=None, fields=None,
                 connection=None, headers={}, cc=None, bcc=None, attachments=None):

        self.person = person
        self.emails = [self.person.email]

        self.tournament = tournament
        self.round = round

        self.event = event
        self.headers = headers

        self.fields = fields
        self.context = Context(fields)
        self.subject = Template(self.tournament.pref(subject)).render(self.context)
        self.body = Template(self.tournament.pref(body)).render(self.context)

        self.from_email = "%s <%s>" % (self.tournament.short_name, settings.DEFAULT_FROM_EMAIL)
        self.reply_to = None
        if self.tournament.pref('reply_to_address') != "":
            self.reply_to = ["%s <%s>" % (self.tournament.pref('reply_to_name'), self.tournament.pref('reply_to_address'))]

        super().__init__(self.subject, self.body, self.from_email, self.emails, bcc, connection, attachments,
            self.headers, cc, self.reply_to)

    def as_sent_record(self):
        return SentMessageRecord(recipient=self.person, email=self.person.email,
                                 event=self.event, method=SentMessageRecord.METHOD_TYPE_EMAIL,
                                 round=self.round, tournament=self.tournament,
                                 context=self.fields, message=self.message().as_string())


def send_mail(emails):
    try:
        mail.get_connection().send_messages(emails)
    except SMTPException:
        logger.exception("Failed to send e-mails.")
        raise
    except ConnectionError:
        logger.exception("Connection error sending e-mails.")
        raise
    else:
        SentMessageRecord.objects.bulk_create([message.as_sent_record() for message in emails])

    return len(emails)


def adjudicator_assignment_email_generator(round_id):
    emails = []
    round = Round.objects.get(id=round_id)
    tournament = round.tournament
    draw = round.debate_set_with_prefetches(speakers=False, divisions=False).all()
    use_codes = use_team_code_names(tournament, False)

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
            'VENUE': debate.venue.name,
            'PANEL': _assemble_panel(debate.adjudicators.with_positions()),
            'DRAW': matchup
        }

        for adj, pos in debate.adjudicators.with_positions():
            if adj.email is None:
                continue

            context['USER'] = adj.name
            context['POSITION'] = adj_position_names[pos]

            emails.append(TournamentEmailMessage(
                'adj_email_subject_line', 'adj_email_message',
                tournament, round,
                SentMessageRecord.EVENT_TYPE_DRAW, adj, context))

    return send_mail(emails)


def randomized_url_email_generator(url, tournament_id):
    emails = []
    tournament = Tournament.objects.get(id=tournament_id)

    subquery = SentMessageRecord.objects.filter(
        event=SentMessageRecord.EVENT_TYPE_URL,
        tournament=tournament, email=OuterRef('email')
    )
    participants = tournament.participants.filter(
        url_key__isnull=False, email__isnull=False
    ).exclude(email__exact="").annotate(already_sent=Exists(subquery)).filter(already_sent=False)

    for instance in participants:
        url_ind = url + instance.url_key + '/'

        variables = {'NAME': instance.name, 'URL': url_ind, 'KEY': instance.url_key, 'TOURN': str(tournament)}

        emails.append(TournamentEmailMessage(
            'url_email_subject', 'url_email_message',
            tournament, None,
            SentMessageRecord.EVENT_TYPE_URL, instance, variables))

    return send_mail(emails)


def ballots_email_generator(debate_id):
    emails = []
    debate = Debate.objects.get(id=debate_id)
    tournament = debate.round.tournament
    ballots = DebateResult(debate.confirmed_ballot).as_dicts()
    round_name = _("%(tournament)s %(round)s @ %(room)s") % {'tournament': str(tournament),
                                                             'round': debate.round.name, 'room': debate.venue.name}

    context = {'DEBATE': round_name}
    use_codes = use_team_code_names(debate.round.tournament, False)

    for ballot in ballots:
        if 'adjudicator' in ballot:
            judge = ballot['adjudicator']
        else:
            judge = debate.debateadjudicator_set.get(type=DebateAdjudicator.TYPE_CHAIR).adjudicator

        if judge.email is None:
            continue

        scores = ""
        for team in ballot['teams']:

            team_name = team['team'].code_name if use_codes else team['team'].short_name
            scores += _("(%(side)s) %(team)s\n") % {'side': team['side'], 'team': team_name}

            for speaker in team['speakers']:
                scores += _("- %(debater)s: %(score)s\n") % {'debater': speaker['speaker'], 'score': speaker['score']}

        context['USER'] = judge.name
        context['SCORES'] = scores

        emails.append(TournamentEmailMessage(
            'ballot_email_subject', 'ballot_email_message',
            tournament, debate.round,
            SentMessageRecord.EVENT_TYPE_BALLOT_CONFIRMED, judge, context))

    return send_mail(emails)


def standings_email_generator(url, round_id):
    emails = []
    round = Round.objects.get(id=round_id)
    tournament = round.tournament

    teams = round.active_teams.prefetch_related('speaker_set')
    populate_win_counts(teams)

    context = {'TOURN': str(tournament)}

    if tournament.pref('public_team_standings'):
        context['url'] = url

    for team in teams:
        context['POINTS'] = str(team.points_count)
        context['TEAM'] = team.short_name

        for speaker in team.speaker_set.all():
            if speaker.email is None:
                continue

            context['USER'] = speaker.name

            emails.append(TournamentEmailMessage(
                'team_points_email_subject', 'team_points_email_message',
                tournament, round,
                SentMessageRecord.EVENT_TYPE_POINTS, speaker, context))

    return send_mail(emails)


def motion_release_email_generator(round_id):
    emails = []
    round = Round.objects.get(id=round_id)

    def _create_motion_list():
        motion_list = ""
        for motion in round.motion_set.all():
            motion_list += _(" - %s (%s)\n") % (motion.text, motion.reference)

            if motion.info_slide:
                motion_list += "   %s\n" % (motion.info_slide)

        return motion_list

    context = {
        'TOURN': str(round.tournament),
        'ROUND': round.name,
        'MOTIONS': _create_motion_list()
    }

    teams = round.tournament.team_set.filter(round_availabilities__round=round).prefetch_related('speaker_set')
    for team in teams:
        for speaker in team.speaker_set.all():
            if speaker.email is None:
                continue

            context['USER'] = speaker.name

            emails.append(TournamentEmailMessage(
                'motion_email_subject', 'motion_email_message',
                round.tournament, round,
                SentMessageRecord.EVENT_TYPE_MOTIONS, speaker, context))

    return send_mail(emails)
