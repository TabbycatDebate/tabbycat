import logging
from smtplib import SMTPException

from django.contrib import messages
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from participants.models import Adjudicator, Speaker
from privateurls.models import PrivateUrlSentMailRecord
from tournaments.mixins import TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import SuperuserRequiredMixin
from utils.tables import TabbycatTableBuilder
from utils.urlkeys import populate_url_keys
from utils.views import PostOnlyRedirectView, VueTableTemplateView

from .utils import send_randomised_url_emails

logger = logging.getLogger(__name__)


class RandomisedUrlsMixin(TournamentMixin):

    def get_context_data(self, **kwargs):
        # These are used to choose the nav display
        tournament = self.get_tournament()
        kwargs['exists'] = tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            tournament.team_set.filter(url_key__isnull=False).exists()
        kwargs['blank_exists'] = tournament.adjudicator_set.filter(url_key__isnull=True).exists() or \
            tournament.team_set.filter(url_key__isnull=True).exists()
        return super().get_context_data(**kwargs)

    def get_adjudicators_to_email(self, url_type, already_sent=False):
        subquery = PrivateUrlSentMailRecord.objects.filter(
            url_key=OuterRef('url_key'), email=OuterRef('email'),
            url_type=url_type, adjudicator_id=OuterRef('pk'),
        )
        adjudicators = Adjudicator.objects.filter(
            tournament=self.get_tournament(),
            url_key__isnull=False, email__isnull=False
        ).exclude(
            email__exact=""
        ).annotate(
            already_sent=Exists(subquery)
        ).filter(already_sent=already_sent)
        return adjudicators

    def get_speakers_to_email(self, already_sent=False):
        subquery = PrivateUrlSentMailRecord.objects.filter(
            url_key=OuterRef('team__url_key'), email=OuterRef('email'),
            url_type=PrivateUrlSentMailRecord.URL_TYPE_FEEDBACK, speaker_id=OuterRef('pk'),
        )
        speakers = Speaker.objects.filter(
            team__tournament=self.get_tournament(),
            team__url_key__isnull=False, email__isnull=False
        ).exclude(
            email__exact=""
        ).annotate(
            already_sent=Exists(subquery)
        ).filter(already_sent=already_sent)
        return speakers


class RandomisedUrlsView(RandomisedUrlsMixin, SuperuserRequiredMixin, VueTableTemplateView):

    template_name = 'private_urls.html'
    tables_orientation = 'columns'

    def get_teams_table(self):
        tournament = self.get_tournament()

        def _build_url(team):
            if team.url_key is None:
                return {'text': _("no URL"), 'class': 'text-warning'}
            path = reverse_tournament('adjfeedback-public-add-from-team-randomised', tournament,
                kwargs={'url_key': team.url_key})
            return {'text': self.request.build_absolute_uri(path), 'class': 'small'}

        teams = tournament.team_set.all()
        table = TabbycatTableBuilder(view=self, title=_("Teams"), sort_key=_("Team"))
        table.add_team_columns(teams)
        table.add_column(_("Feedback URL"), [_build_url(team) for team in teams])

        return table

    def get_adjudicators_table(self):
        tournament = self.get_tournament()

        def _build_url(adjudicator, url_name):
            if adjudicator.url_key is None:
                return {'text': _("no URL"), 'class': 'text-warning'}
            path = reverse_tournament(url_name, tournament, kwargs={'url_key': adjudicator.url_key})
            return {'text': self.request.build_absolute_uri(path), 'class': 'small'}

        adjudicators = Adjudicator.objects.all() if tournament.pref('share_adjs') else tournament.adjudicator_set.all()
        table = TabbycatTableBuilder(view=self, title=_("Adjudicators"), sort_key=_("Name"))
        table.add_adjudicator_columns(adjudicators, hide_institution=True, hide_metadata=True)
        table.add_column(_("Feedback URL"), [_build_url(adj, 'adjfeedback-public-add-from-adjudicator-randomised') for adj in adjudicators])
        table.add_column(_("Ballot URL"), [_build_url(adj, 'results-public-ballotset-new-randomised') for adj in adjudicators])

        return table

    def get_tables(self):
        return [self.get_adjudicators_table(), self.get_teams_table()]


class GenerateRandomisedUrlsView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'privateurls-list'

    def post(self, request, *args, **kwargs):
        tournament = self.get_tournament()

        nexisting_adjs = tournament.adjudicator_set.filter(url_key__isnull=False).count()
        nexisting_teams = tournament.team_set.filter(url_key__isnull=False).count()
        blank_adjs = tournament.adjudicator_set.filter(url_key__isnull=True)
        blank_teams = tournament.team_set.filter(url_key__isnull=True)
        nblank_adjs = blank_adjs.count()
        nblank_teams = blank_teams.count()

        if nblank_adjs == 0 and nblank_teams == 0:
            messages.error(self.request, _("All adjudicators and teams already have private URLs. "
                "If you want to delete them, use the Edit Database area."))

        else:
            populate_url_keys(blank_adjs)
            populate_url_keys(blank_teams)

            if nexisting_adjs == 0 and nexisting_teams == 0:
                # too hard to pluralize, will do it when we hit a language that actually needs it
                messages.success(self.request, _("Private URLs were generated for all %(nblank_adjs)d "
                    "adjudicators and all %(nblank_teams)d teams.") % {
                    'nblank_adjs': nblank_adjs, 'nblank_teams': nblank_teams,
                })
            else:
                # too hard to pluralize, will do it when we hit a language that actually needs it
                messages.success(self.request, _("Private URLs were generated for %(nblank_adjs)d "
                    "adjudicators and %(nblank_teams)d teams. The already-existing private URLs for "
                    "%(nexisting_adjs)d adjudicators and %(nexisting_teams)d teams were left intact.") % {
                    'nblank_adjs': nblank_adjs, 'nblank_teams': nblank_teams,
                    'nexisting_adjs': nexisting_adjs, 'nexisting_teams': nexisting_teams,
                })

        return super().post(request, *args, **kwargs)


class BaseEmailRandomisedUrlsView(RandomisedUrlsMixin, VueTableTemplateView):

    tables_orientation = 'rows'

    def get_context_data(self, **kwargs):
        kwargs['adjudicators_no_email'] = self.get_tournament().adjudicator_set.filter(
            Q(email__isnull=True) | Q(email__exact=""), url_key__isnull=False
        ).values_list('name', flat=True)
        return super().get_context_data(**kwargs)

    def get_adjudicators_table(self, url_type, url_name, url_header):
        tournament = self.get_tournament()

        def _build_url(adjudicator):
            path = reverse_tournament(url_name, tournament, kwargs={'url_key': adjudicator.url_key})
            return self.request.build_absolute_uri(path)

        adjudicators = self.get_adjudicators_to_email(url_type)
        title = _("Adjudicators who will be sent e-mails (%(n)s)") % {'n': adjudicators.count()}
        table = TabbycatTableBuilder(view=self, title=title, sort_key=_("Name"))
        table.add_adjudicator_columns(adjudicators, hide_institution=True, hide_metadata=True)
        table.add_column(_("Email"), [adj.email for adj in adjudicators])
        table.add_column(url_header, [_build_url(adj) for adj in adjudicators])

        return table


class EmailBallotUrlsView(BaseEmailRandomisedUrlsView):

    template_name = 'ballot_urls_email_list.html'

    def get_context_data(self, **kwargs):
        kwargs['nadjudicators_already_sent'] = self.get_adjudicators_to_email(
            PrivateUrlSentMailRecord.URL_TYPE_BALLOT, already_sent=True).count()
        return super().get_context_data(**kwargs)

    def get_table(self):
        return self.get_adjudicators_table(PrivateUrlSentMailRecord.URL_TYPE_BALLOT,
            'results-public-ballotset-new-randomised', _("Ballot URL"))


class EmailFeedbackUrlsView(BaseEmailRandomisedUrlsView):

    template_name = 'feedback_urls_email_list.html'

    def get_context_data(self, **kwargs):
        kwargs['speakers_no_email'] = Speaker.objects.filter(
            Q(email__isnull=True) | Q(email__exact=""),
            team__tournament=self.get_tournament(),
            team__url_key__isnull=False
        ).values_list('name', flat=True)
        kwargs['nadjudicators_already_sent'] = self.get_adjudicators_to_email(
            PrivateUrlSentMailRecord.URL_TYPE_FEEDBACK, already_sent=True).count()
        kwargs['nspeakers_already_sent'] = self.get_speakers_to_email(already_sent=True).count()
        return super().get_context_data(**kwargs)

    def get_speakers_table(self):
        tournament = self.get_tournament()

        def _build_url(speaker):
            path = reverse_tournament('adjfeedback-public-add-from-team-randomised', tournament,
                kwargs={'url_key': speaker.team.url_key})
            return self.request.build_absolute_uri(path)

        speakers = self.get_speakers_to_email()
        title = _("Speakers who will be sent e-mails (%(n)s)") % {'n': speakers.count()}
        table = TabbycatTableBuilder(view=self, title=title, sort_key=_("Team"))
        table.add_speaker_columns(speakers, categories=False)
        table.add_team_columns([speaker.team for speaker in speakers])
        table.add_column(_("Email"), [speaker.email for speaker in speakers])
        table.add_column(_("Feedback URL"), [_build_url(speaker) for speaker in speakers])

        return table

    def get_tables(self):
        speaker_table = self.get_speakers_table()
        adjudicator_table = self.get_adjudicators_table(
                PrivateUrlSentMailRecord.URL_TYPE_FEEDBACK,
                'adjfeedback-public-add-from-adjudicator-randomised', _("Feedback URL"))
        return [speaker_table, adjudicator_table]


class BaseConfirmEmailRandomisedUrlsView(SuperuserRequiredMixin, RandomisedUrlsMixin, PostOnlyRedirectView):

    tournament_redirect_pattern_name = 'privateurls-list'


class ConfirmEmailBallotUrlsView(BaseConfirmEmailRandomisedUrlsView):

    def post(self, request, *args, **kwargs):

        tournament = self.get_tournament()

        subject = _("Your personal ballot submission URL for %(tournament)s")
        message = _(
            "Hi %(name)s,\n\n"
            "At %(tournament)s, we are using an online ballot system. You can submit "
            "your ballots at the following URL. This URL is unique to you — do not share it with "
            "anyone, as anyone who knows it can submit ballots on your behalf. This URL "
            "will not change throughout this tournament, so we suggest bookmarking it.\n\n"
            "Your personal private ballot submission URL is:\n"
            "%(url)s"
        )
        adjudicators = self.get_adjudicators_to_email(PrivateUrlSentMailRecord.URL_TYPE_BALLOT)

        try:
            nadjudicators = send_randomised_url_emails(
                request, tournament, adjudicators,
                'results-public-ballotset-new-randomised',
                lambda adj: adj.url_key, 'adjudicator', PrivateUrlSentMailRecord.URL_TYPE_BALLOT,
                subject, message
            )
        except SMTPException:
            messages.error(request, _("There was a problem sending private ballot URLs to adjudicators."))
        else:
            messages.success(request, ungettext(
                "E-mails with private ballot URLs were sent to %(nadjudicators)d adjudicator.",
                "E-mails with private ballot URLs were sent to %(nadjudicators)d adjudicators.",
                nadjudicators
            ) % {'nadjudicators': nadjudicators})

        return super().post(request, *args, **kwargs)


class ConfirmEmailFeedbackUrlsView(BaseConfirmEmailRandomisedUrlsView):

    def post(self, request, *args, **kwargs):

        tournament = self.get_tournament()
        success = True

        subject = _("Your team's feedback submission URL for %(tournament)s")
        message = _(
            "Hi %(name)s,\n\n"
            "At %(tournament)s, we are using an online adjudicator feedback system. As part of "
            "%(team)s, you can submit your feedback at the following URL. This URL is unique "
            "to you — do not share it with anyone, as anyone who knows it can submit feedback on "
            "your team's behalf. This URL will not change throughout this tournament, so we "
            "suggest bookmarking it.\n\n"
            "Your team's private feedback submission URL is:\n"
            "%(url)s"
        )
        speakers = self.get_speakers_to_email()

        try:
            nspeakers = send_randomised_url_emails(
                request, tournament, speakers,
                'adjfeedback-public-add-from-team-randomised',
                lambda speaker: speaker.team.url_key, 'speaker', PrivateUrlSentMailRecord.URL_TYPE_FEEDBACK,
                subject, message
            )
        except SMTPException:
            messages.error(request, _("There was a problem sending private feedback URLs to speakers."))
            success = False

        subject = _("Your personal feedback submission URL for %(tournament)s")
        message = _(
            "Hi %(name)s,\n\n"
            "At %(tournament)s, we are using an online adjudicator feedback system. You can submit "
            "your feedback at the following URL. This URL is unique to you — do not share it with "
            "anyone, as anyone who knows it can submit feedback on your behalf. This URL "
            "will not change throughout this tournament, so we suggest bookmarking it.\n\n"
            "Your personal private feedback submission URL is:\n"
            "%(url)s"
        )
        adjudicators = self.get_adjudicators_to_email(PrivateUrlSentMailRecord.URL_TYPE_FEEDBACK)

        try:
            nadjudicators = send_randomised_url_emails(
                request, tournament, adjudicators,
                'adjfeedback-public-add-from-adjudicator-randomised',
                lambda adj: adj.url_key, 'adjudicator', PrivateUrlSentMailRecord.URL_TYPE_FEEDBACK,
                subject, message
            )
        except SMTPException:
            messages.error(request, _("There was a problem sending private feedback URLs to adjudicators."))
            success = False

        if success:
            # Translators: This goes in the "speakers_phrase" variable in "E-mails with private feedback URLs were sent..."
            speakers_phrase = ungettext("%(nspeakers)d speaker",
                "%(nspeakers)d speakers", nspeakers) % {'nspeakers': nspeakers}
            # Translators: This goes in the "adjudicators_phrase" variable in "E-mails with private feedback URLs were sent..."
            adjudicators_phrase = ungettext("%(nadjudicators)d adjudicator",
                "%(nadjudicators)d adjudicators", nadjudicators) % {'nadjudicators': nadjudicators}
            messages.success(request, _("E-mails with private feedback URLs were sent to "
                "%(speakers_phrase)s and %(adjudicators_phrase)s.") % {
                'speakers_phrase': speakers_phrase, 'adjudicators_phrase': adjudicators_phrase
            })

        return super().post(request, *args, **kwargs)
