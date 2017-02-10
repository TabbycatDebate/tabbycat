import logging
from threading import Lock

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import management
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import CreateView, FormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from draw.models import Debate
from importer.management.commands import importtournament
from importer.base import TournamentDataImporterError
from utils.forms import SuperuserCreationForm
from utils.misc import redirect_round, redirect_tournament
from utils.mixins import CacheMixin, PostOnlyRedirectView, SuperuserRequiredMixin

from .forms import TournamentForm
from .mixins import RoundMixin, TournamentMixin
from .models import Tournament

User = get_user_model()
logger = logging.getLogger(__name__)


class PublicSiteIndexView(TemplateView):
    template_name = 'site_index.html'

    def get(self, request, *args, **kwargs):
        tournaments = Tournament.objects.all()
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
    cache_timeout = 10 # Set slower to show new indexes so it will show new pages


class TournamentAdminHomeView(LoginRequiredMixin, TournamentMixin, TemplateView):
    template_name = "tournament_index.html"

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        round = tournament.current_round
        assert(round is not None)
        kwargs["round"] = round
        kwargs["readthedocs_version"] = settings.READTHEDOCS_VERSION
        kwargs["blank"] = not (tournament.team_set.exists() or tournament.adjudicator_set.exists() or tournament.venue_set.exists())
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament.current_round is None:
            if self.request.user.is_superuser:
                tournament.current_round = tournament.round_set.order_by('seq').first()
                if tournament.current_round is None:
                    return HttpResponse('<p>Error: This tournament has no rounds; '
                                        ' you\'ll need to add some in the '
                                        '<a href="' + reverse('admin:tournaments_round_changelist') +
                                        '">Edit Database</a> area.</p>')
                messages.warning(self.request, "The current round wasn't set, "
                                 "so it's been automatically set to the first round.")
                logger.warning("Automatically set current round to {}".format(tournament.current_round))
                tournament.save()
                self.request.tournament = tournament  # Update for context processors
            else:
                raise Http404()
        return super().get(self, request, *args, **kwargs)


class RoundIncrementConfirmView(SuperuserRequiredMixin, RoundMixin, TemplateView):
    template_name = 'round_increment_check.html'

    def get(self, request, *args, **kwargs):
        round = self.get_round()
        current_round = self.get_tournament().current_round
        if round != current_round:
            messages.error(self.request, "You are trying to advance from {this_round} but "
                "the current round is {current_round} — advance to {this_round} first!".format(
                    this_round=round.name, current_round=current_round.name))
            return redirect_round('results-round-list', self.get_tournament().current_round)
        else:
            return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['num_unconfirmed'] = self.get_round().debate_set.filter(
            result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
        kwargs['increment_ok'] = kwargs['num_unconfirmed'] == 0
        return super().get_context_data(**kwargs)


class RoundIncrementView(RoundMixin, SuperuserRequiredMixin, LogActionMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ROUND_ADVANCE
    round_redirect_pattern_name = 'results-round-list' # standard redirect is only on error

    def post(self, request, *args, **kwargs):
        tournament = self.get_tournament()

        # Advance relative to the round of the view, not the current round, so
        # that in times of confusion, going back then clicking again won't advance
        # twice.
        next_round = self.get_round().next
        if next_round:
            tournament.current_round = next_round
            tournament.save()
            messages.success(request, "Advanced the current round. The current round is now %s. "
                "Woohoo! Keep it up!" % next_round.name)
            self.log_action(round=next_round, content_object=next_round)
            return redirect_round('availability-index', next_round)

        else:
            messages.error(request, "Whoops! Could not advance round, because there's no round "
                "after this round!")
            return super().post(request, *args, **kwargs)


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
            logger.error("Tried to get the blank-site-start view when a user account already exists.")
            return redirect('tabbycat-index')

        return super().get(request)

    def post(self, request):
        with self.lock:
            if User.objects.exists():
                logger.error("Tried to post the blank-site-start view when a user account already exists.")
                messages.error(request, "Whoops! It looks like someone's already created the first user account. Please log in.")
                return redirect('login')

            return super().post(request)

    def form_valid(self, form):
        form.save()
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password1'])
        login(self.request, user)
        messages.success(self.request, "Welcome! You've created an account for %s." % user.username)

        return super().form_valid(form)


class CreateTournamentView(SuperuserRequiredMixin, CreateView):
    """This view allows a logged-in superuser to create a new tournament."""

    model = Tournament
    form_class = TournamentForm
    template_name = "create_tournament.html"


class LoadDemoView(SuperuserRequiredMixin, PostOnlyRedirectView):

    def post(self, request, *args, **kwargs):
        source = request.POST.get("source", "")
        if Tournament.objects.filter(slug=source).exists():
            messages.warning(self.request, "This kind of demo tournament "
                "already exists; you should delete it (and its institutions) "
                "in the Edit Database Area before creating another demo.")
        else:
            try:
                management.call_command(importtournament.Command(), source)
            except TournamentDataImporterError as e:
                messages.error(self.request, mark_safe("<p>There were one or more errors creating the demo tournament. "
                    "Before retrying, please delete the existing demo tournament <strong>and</strong> "
                    "the institutions in the Edit Database Area.</p><p><i>Technical information: The errors are as follows:"
                    "<ul>" + "".join("<li>{}</li>".format(message) for message in e.itermessages()) + "</ul></i></p>"))
                logger.critical("Error importing demo tournament: " + str(e))
            else:
                messages.success(self.request, "Created new demo tournament. You "
                    "can access it below.")
        return redirect('tabbycat-index')


class TournamentPermanentRedirectView(RedirectView):
    """Redirect old-style /t/<slug>/... URLs to new-style /<slug>/... URLs."""

    url = "/%(slug)s/%(page)s"
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        slug = kwargs['slug']
        if not Tournament.objects.filter(slug=slug).exists():
            logger.error("Tried to redirect non-existent tournament slug '%s'" % slug)
            raise Http404("There isn't a tournament with slug '%s'." % slug)
        return super().get_redirect_url(*args, **kwargs)


class DonationsView(CacheMixin, TemplateView):
    template_name = 'donations.html'


class TournamentDonationsView(TournamentMixin, TemplateView):
    template_name = 'donations.html'
