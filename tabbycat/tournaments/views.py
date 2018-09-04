import json
import logging
from collections import OrderedDict
from smtplib import SMTPException
from threading import Lock

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.urls import reverse_lazy
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.shortcuts import redirect, resolve_url
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from draw.models import Debate
from notifications.models import SentMessageRecord
from participants.models import Team
from participants.prefetch import populate_win_counts
from results.models import BallotSubmission
from tournaments.models import Round
from utils.forms import SuperuserCreationForm
from utils.misc import redirect_round, redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin, AssistantMixin, CacheMixin, TabbycatPageTitlesMixin, WarnAboutDatabaseUseMixin
from utils.views import BadJsonRequestError, JsonDataResponsePostView, PostOnlyRedirectView

from .forms import SetCurrentRoundForm, TournamentConfigureForm, TournamentStartForm
from .mixins import RoundMixin, TournamentMixin
from .models import Tournament
from .utils import get_side_name, send_standings_emails

User = get_user_model()
logger = logging.getLogger(__name__)


class PublicSiteIndexView(WarnAboutDatabaseUseMixin, TemplateView):
    template_name = 'site_index.html'

    def get(self, request, *args, **kwargs):
        tournaments = Tournament.objects.all()
        if request.GET.get('redirect', '') == 'false':
            return super().get(request, *args, **kwargs)
        if tournaments.count() == 1 and not request.user.is_authenticated:
            logger.debug('One tournament only, user is: %s, redirecting to tournament-public-index', request.user)
            return redirect_tournament('tournament-public-index', tournaments.first())
        elif not tournaments.exists() and not User.objects.exists():
            logger.debug('No users and no tournaments, redirecting to blank-site-start')
            return redirect('blank-site-start')
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['tournaments'] = Tournament.objects.all()
        return super().get_context_data(**kwargs)


class TournamentPublicHomeView(CacheMixin, TournamentMixin, TemplateView):
    template_name = 'public_tournament_index.html'


class TournamentDashboardHomeView(TournamentMixin, WarnAboutDatabaseUseMixin, TemplateView):

    def get_context_data(self, **kwargs):
        t = self.tournament
        updates = 15 # Number of items to fetch

        kwargs["round"] = t.current_round
        kwargs["tournament_slug"] = t.slug
        kwargs["readthedocs_version"] = settings.READTHEDOCS_VERSION
        kwargs["blank"] = not (t.team_set.exists() or t.adjudicator_set.exists() or t.venue_set.exists())

        actions = ActionLogEntry.objects.filter(tournament=t).prefetch_related(
                    'content_object', 'user').order_by('-timestamp')[:updates]
        kwargs["initialActions"] = json.dumps([a.serialize for a in actions])

        subs = BallotSubmission.objects.filter(
            debate__round__tournament=t, confirmed=True).prefetch_related(
            'teamscore_set__debate_team',
            'teamscore_set__debate_team__team').select_related(
            'debate__round__tournament').order_by('-timestamp')[:updates]
        subs = [bs.serialize_like_actionlog for bs in subs]
        kwargs["initialBallots"] = json.dumps(subs)

        status = t.current_round.draw_status
        kwargs["total_debates"] = t.current_round.debate_set.count()
        if status == Round.STATUS_CONFIRMED or status == Round.STATUS_RELEASED:
            ballots = BallotSubmission.objects.filter(
                debate__round=t.current_round, discarded=False).select_related(
                'submitter', 'debate')
            stats = [{'ballot': bs.serialize(t)} for bs in ballots]
            kwargs["initial_graph_data"] = json.dumps(stats)
        else:
            kwargs["initial_graph_data"] = json.dumps([])

        return super().get_context_data(**kwargs)


class TournamentAssistantHomeView(AssistantMixin, TournamentDashboardHomeView):
    template_name = 'assistant_tournament_index.html'


class TournamentAdminHomeView(AdministratorMixin, TournamentDashboardHomeView):
    template_name = 'tournament_index.html'


class RoundAdvanceConfirmView(AdministratorMixin, RoundMixin, TemplateView):
    template_name = 'round_advance_check.html'

    def get(self, request, *args, **kwargs):
        current_round = self.tournament.current_round
        if self.round != current_round:
            messages.error(self.request, "You are trying to advance from {this_round} but "
                "the current round is {current_round} — advance to {this_round} first!".format(
                    this_round=self.round.name, current_round=current_round.name))
            return redirect_round('results-round-list', current_round)
        else:
            return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['num_unconfirmed'] = self.round.debate_set.filter(
            result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
        kwargs['increment_ok'] = kwargs['num_unconfirmed'] == 0
        kwargs['emails_sent'] = SentMessageRecord.objects.filter(
            tournament=self.tournament, round=self.round, event=SentMessageRecord.EVENT_TYPE_POINTS).exists()
        return super().get_context_data(**kwargs)


class RoundAdvanceView(RoundMixin, AdministratorMixin, LogActionMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ROUND_ADVANCE
    round_redirect_pattern_name = 'results-round-list' # standard redirect is only on error

    def post(self, request, *args, **kwargs):
        # Advance relative to the round of the view, not the current round, so
        # that in times of confusion, going back then clicking again won't advance
        # twice.
        next_round = self.tournament.round_set.filter(seq__gt=self.round.seq).order_by('seq').first()

        if next_round:
            self.tournament.current_round = next_round
            self.tournament.save()
            self.log_action(round=next_round, content_object=next_round)

            if (next_round.stage == Round.STAGE_ELIMINATION and
                    self.round.stage == Round.STAGE_PRELIMINARY):
                messages.success(request, _("The current round has been advanced to %(round)s. "
                        "You've made it to the end of the preliminary rounds! Congratulations! "
                        "The next step is to generate the break.") % {'round': next_round.name})
                return redirect_tournament('breakqual-index', self.tournament)
            else:
                messages.success(request, _("The current round has been advanced to %(round)s. "
                    "Woohoo! Keep it up!") % {'round': next_round.name})
                return redirect_round('availability-index', next_round)

        else:
            messages.error(request, _("Whoops! Could not advance round, because there's no round "
                "after this round!"))
            return super().post(request, *args, **kwargs)


class SendStandingsEmailsView(RoundMixin, AdministratorMixin, PostOnlyRedirectView):

    def post(self, request, *args, **kwargs):
        active_teams = Team.objects.filter(debateteam__debate__round=self.round).prefetch_related('speaker_set')
        populate_win_counts(active_teams)

        try:
            send_standings_emails(self.tournament, active_teams, request, self.round)
        except (ConnectionError, SMTPException):
            messages.error(request, _("Team point emails could not be sent."))
        else:
            messages.success(request, _("Team point emails have been sent to the speakers."))

        return redirect_round('tournament-advance-round-check', self.round)


class BlankSiteStartView(FormView):
    """This view is presented to the user when there are no tournaments and no
    user accounts. It prompts the user to create a first superuser. It rejects
    all requests, GET or POST, if there exists any user account in the
    system."""

    form_class = SuperuserCreationForm
    template_name = "blank_site_start.html"
    lock = Lock()
    success_url = reverse_lazy('tabbycat-index')

    def get(self, request):
        if User.objects.exists():
            logger.warning("Tried to get the blank-site-start view when a user account already exists.")
            return redirect('tabbycat-index')

        return super().get(request)

    def post(self, request):
        with self.lock:
            if User.objects.exists():
                logger.warning("Tried to post the blank-site-start view when a user account already exists.")
                messages.error(request, "Whoops! It looks like someone's already created the first user account. Please log in.")
                return redirect('login')

            return super().post(request)

    def form_valid(self, form):
        form.save()
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password1'])
        login(self.request, user)
        messages.info(self.request, "Welcome! You've created an account for %s." % user.username)

        return super().form_valid(form)


class CreateTournamentView(AdministratorMixin, WarnAboutDatabaseUseMixin, CreateView):
    """This view allows a logged-in superuser to create a new tournament."""

    model = Tournament
    form_class = TournamentStartForm
    template_name = "create_tournament.html"
    db_warning_severity = messages.ERROR

    def get_context_data(self, **kwargs):
        demo_datasets = [
            ('minimal8team', _("8-team generic dataset")),
            ('australs24team', _("24-team Australs dataset")),
            ('bp88team', _("88-team BP dataset")),
        ]
        kwargs['demo_datasets'] = demo_datasets
        demo_slugs = [slug for slug, _ in demo_datasets]
        kwargs['preexisting'] = Tournament.objects.filter(slug__in=demo_slugs).values_list('slug', flat=True)
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        t = Tournament.objects.order_by('id').last()
        return reverse_tournament('tournament-configure', tournament=t)


class ConfigureTournamentView(AdministratorMixin, UpdateView, TournamentMixin):
    model = Tournament
    form_class = TournamentConfigureForm
    template_name = "configure_tournament.html"
    slug_url_kwarg = 'tournament_slug'

    def get_success_url(self):
        t = self.tournament
        return reverse_tournament('tournament-admin-home', tournament=t)


class SetCurrentRoundView(AdministratorMixin, UpdateView):
    model = Tournament
    form_class = SetCurrentRoundForm
    template_name = 'set_current_round.html'
    slug_url_kwarg = 'tournament_slug'
    redirect_field_name = 'next'

    def get_redirect_to(self, use_default=True):
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        if not redirect_to and use_default:
            return reverse_tournament('tournament-admin-home', tournament=self.object)
        else:
            return redirect_to

    def get_success_url(self):
        # Copied from django.contrib.auth.views.LoginView.get_success_url
        redirect_to = self.get_redirect_to(use_default=True)
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        if not url_is_safe:
            return resolve_url(settings.LOGIN_REDIRECT_URL)
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            self.redirect_field_name: self.get_redirect_to(use_default=False),
        })
        return context


class FixDebateTeamsView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = "fix_debate_teams.html"

    def get_incomplete_debates(self):
        annotations = {  # annotates with the number of DebateTeams on each side in the debate
            side: RawSQL("""
                SELECT DISTINCT COUNT('a')
                FROM draw_debateteam
                WHERE draw_debate.id = draw_debateteam.debate_id
                AND draw_debateteam.side = %s""", (side,))
            for side in self.tournament.sides
        }
        debates = Debate.objects.filter(round__tournament=self.tournament)
        debates = debates.prefetch_related('debateteam_set__team').annotate(**annotations)

        # A debate is incomplete if there isn't exactly one team on each side
        incomplete_debates = debates.filter(~Q(**{side: 1 for side in self.tournament.sides}))

        # Finally, go through and populate lists of teams on each side
        for debate in incomplete_debates:
            debate.teams_on_each_side = OrderedDict((side, []) for side in self.tournament.sides)
            for dt in debate.debateteam_set.all():
                try:
                    debate.teams_on_each_side[dt.side].append(dt.team)
                except KeyError:
                    pass

        return incomplete_debates

    def get_context_data(self, **kwargs):
        kwargs['side_names'] = [get_side_name(self.tournament, side, 'full') for side in self.tournament.sides]
        kwargs['incomplete_debates'] = self.get_incomplete_debates()
        return super().get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        # bypass the TournamentMixin checks, to avoid potential redirect loops
        return TemplateView.dispatch(self, request, *args, **kwargs)


class DonationsView(CacheMixin, TemplateView):
    template_name = 'donations.html'


class TournamentDonationsView(TournamentMixin, TemplateView):
    template_name = 'donations.html'


class StyleGuideView(TemplateView, TabbycatPageTitlesMixin):
    template_name = 'admin/style_guide.html'
    page_subtitle = 'Contextual sub title'


# ==============================================================================
# Base classes for other apps
# ==============================================================================

class BaseSaveDragAndDropDebateJsonView(AdministratorMixin, RoundMixin, LogActionMixin, JsonDataResponsePostView):
    """For AJAX issued updates which post a Debate dictionary; which is then
    modified and return back via a JSON response"""
    allows_creation = False
    required_json_fields = []

    def modify_debate(self, debate, posted_debate):
        """Modifies the Debate object `debate` using the information in the dict
        `posted_debate`, and returns the modified debate.
        Must be implemented by subclasses."""
        raise NotImplementedError

    def get_debate(self, id):
        """Returns the debate with ID `id`. If the debate doesn't exist and
        `self.allows_creation` is True, it creates a new debate (and saves it)
        and returns it. If the debate doesn't exist and `self.allows_creation`
        is False, it raises a BadJsonRequestError.
        """
        r = self.round
        try:
            return Debate.objects.get(round=r, pk=id)
        except Debate.DoesNotExist:
            if not self.allows_creation:
                logger.exception("Debate with ID %d in round %s doesn't exist, and allows_creation was False", id, r)
                raise BadJsonRequestError("Debate ID %d doesn't exist" % (id,))
            logger.info("Debate with ID %d in round %s doesn't exist, creating new debate", id, r.name)
            return Debate.objects.create(round=r)

    def post_data(self):
        try:
            posted_debate = json.loads(self.body)
        except ValueError:
            logger.exception("Bad JSON provided for drag-and-drop edit")
            raise BadJsonRequestError("Malformed JSON provided")

        debate = self.get_debate(posted_debate['id'])
        debate = self.modify_debate(debate, posted_debate)
        self.log_action(content_object=debate)
        return json.dumps(debate.serialize())
