import logging
from smtplib import SMTPException

from django.conf import settings
from django.core import mail
from django.db.models import Exists, OuterRef
from django.template import Context, Template
from django.utils.translation import gettext as _

from adjallocation.allocation import AdjudicatorAllocation
from draw.models import Debate
from results.result import DebateResult
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
        self.subject = Template(subject).render(self.context)
        self.body = Template(body).render(self.context)

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


class EmailMessageGenerator:
    emails = []

    subject = None
    message = None

    def __init__(self, tournament=None):
        self.tournament = tournament

    def get_subject(self):
        return self.tournament.pref(self.subject)

    def get_message(self):
        return self.tournament.pref(self.message)

    def run(self, *args, **kwargs):
        try:
            mail.get_connection().send_messages(self.emails)
        except SMTPException:
            logger.exception("Failed to send e-mails.")
            raise
        except ConnectionError:
            logger.exception("Connection error sending e-mails.")
            raise
        else:
            SentMessageRecord.objects.bulk_create([message.as_sent_record() for message in self.emails])

        return len(self.emails)


class AdjudicatorAssignmentEmailGenerator(EmailMessageGenerator):
    subject = 'adj_email_subject_line'
    message = 'adj_email_message'

    def run(self, round_id):
        round = Round.objects.get(id=round_id) # Serialize -> Expand
        tournament = round.tournament
        draw = round.debate_set_with_prefetches(speakers=False, divisions=False).all()

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

                self.emails.append(TournamentEmailMessage(
                    self.get_subject(), self.get_message(),
                    tournament, round,
                    SentMessageRecord.EVENT_TYPE_DRAW, adj, context))

        super().run(self)


class RandomizedURLEmailGenerator(EmailMessageGenerator):
    subject = 'url_email_subject'
    message = 'url_email_message'

    def run(self, url, tournament_id):
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

            self.emails.append(TournamentEmailMessage(
                self.get_subject(), self.get_message(), tournament, None, SentMessageRecord.EVENT_TYPE_URL, instance, variables))

        super().run(self)


class BallotEmailGenerator(EmailMessageGenerator):
    subject = 'ballot_email_subject'
    message = 'ballot_email_message'

    def run(self, debate_id):
        debate = Debate.objects.get(id=debate_id)
        ballots = DebateResult(debate.confirmed_ballot).as_dicts()
        round_name = _("%(tournament)s %(round)s @ %(room)s") % {'tournament': str(debate.round.tournament),
                                                                 'round': debate.round.name, 'room': debate.venue.name}

        context = {'DEBATE': round_name}

        for ballot in ballots:
            if 'adjudicator' in ballot:
                judge = ballot['adjudicator']
            else:
                judge = debate.debateadjudicator_set.get(type="C").adjudicator

            if judge.email is None:
                continue

            scores = ''
            for team in ballot['teams']:
                scores += _("(%(side)s) %(team)s\n") % {'side': team['side'], 'team': team['team'].short_name}

                for speaker in team['speakers']:
                    scores += _("- %(debater)s: %(score)s\n") % {'debater': speaker['speaker'], 'score': speaker['score']}

            context['USER'] = judge.name
            context['SCORES'] = scores

            self.emails.append(TournamentEmailMessage(
                self.get_subject(), self.get_message(),
                debate.round.tournament, debate.round,
                SentMessageRecord.EVENT_TYPE_BALLOT_CONFIRMED, judge, context))

        super().run(self)


class StandingsEmailGenerator(EmailMessageGenerator):
    subject = 'team_points_email_subject'
    message = 'team_points_email_message'

    def run(self, url, round_id):
        round = Round.objects.get(id=round_id)
        teams = round.active_teams.prefetch_related('speaker_set')
        populate_win_counts(teams)

        context = {'TOURN': str(round.tournament)}

        if round.tournament.pref('public_team_standings'):
            context['url'] = url

        for team in teams:
            context['POINTS'] = str(team.points_count)
            context['TEAM'] = team.short_name

            for speaker in team.speaker_set.all():
                if speaker.email is None:
                    continue

                context['USER'] = speaker.name

                self.emails.append(TournamentEmailMessage(
                    self.get_subject(), self.get_message(),
                    round.tournament, round,
                    SentMessageRecord.EVENT_TYPE_POINTS, speaker, context))

        super().run(self)
