import json
import logging
from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url
from django.utils.html import format_html_join
from django.utils.timezone import get_current_timezone_name
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from formtools.wizard.views import SessionWizardView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from breakqual.models import BreakCategory
from breakqual.utils import auto_make_break_rounds
from draw.models import Debate
from notifications.models import BulkNotification
from results.models import BallotSubmission
from results.prefetch import populate_confirmed_ballots
from tournaments.models import Round
from users.permissions import has_permission, Permission
from utils.misc import redirect_round, redirect_tournament, reverse_round, reverse_tournament
from utils.mixins import (AdministratorMixin, AssistantMixin, CacheMixin, TabbycatPageTitlesMixin,
                          WarnAboutDatabaseUseMixin, WarnAboutLegacySendgridConfigVarsMixin)
from utils.tables import TabbycatTableBuilder
from utils.views import ModelFormSetView, PostOnlyRedirectView, VueTableTemplateView

from .forms import (clear_all_round_caches, RoundRobinPrelimSetupForm, RoundWeightForm, ScheduleEventForm,
                    SetCurrentRoundMultipleBreakCategoriesForm, SetCurrentRoundSingleBreakCategoryForm,
                    TournamentConfigureForm, TournamentStartForm)
from .mixins import PublicTournamentPageMixin, RoundMixin, TournamentMixin
from .models import ScheduleEvent, Tournament
from .utils import auto_make_rounds_rr, DRAW_FORMAT_ROUND_ROBIN, get_side_name

User = get_user_model()
logger = logging.getLogger(__name__)


def _create_tournament_wizard_show_rr_setup(wizard):
    cfg = wizard.get_cleaned_data_for_step('configure')
    return bool(cfg and cfg.get('draw_format') == DRAW_FORMAT_ROUND_ROBIN)


class PublicSiteIndexView(WarnAboutDatabaseUseMixin, WarnAboutLegacySendgridConfigVarsMixin, TemplateView):
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
        kwargs['tournaments'] = Tournament.objects.filter(active=True)
        kwargs['inactive'] = Tournament.objects.filter(active=False)
        return super().get_context_data(**kwargs)


class TournamentPublicHomeView(CacheMixin, TournamentMixin, TemplateView):
    template_name = 'public_tournament_index.html'

    def get_context_data(self, **kwargs):
        kwargs['public_index'] = True
        return super().get_context_data(**kwargs)


class BaseTournamentDashboardHomeView(TournamentMixin, WarnAboutDatabaseUseMixin, WarnAboutLegacySendgridConfigVarsMixin, TemplateView):

    def get_context_data(self, **kwargs):
        t = self.tournament
        updates = 10 # Number of items to fetch

        kwargs["round"] = t.current_round
        kwargs["tournament_slug"] = t.slug
        kwargs["readthedocs_version"] = settings.READTHEDOCS_VERSION
        kwargs["blank"] = not (t.team_set.exists() or t.adjudicator_set.exists() or t.venue_set.exists())

        action_perm = has_permission(self.request.user, 'view.actionlogentry', self.tournament)
        if action_perm:
            actions = ActionLogEntry.objects.filter(tournament=t).prefetch_related(
                        'content_object', 'user').order_by('-timestamp')[:updates]
            kwargs["initialActions"] = json.dumps([a.serialize for a in actions])
        else:
            kwargs["initialActions"] = json.dumps([])

        results_perm = has_permission(self.request.user, 'view.ballotsubmission', self.tournament)
        if results_perm:
            debates = t.current_round.debate_set.filter(
                ballotsubmission__confirmed=True,
            ).order_by('-ballotsubmission__timestamp')[:updates]
            populate_confirmed_ballots(debates, results=True)
            subs = [d._confirmed_ballot.serialize_like_actionlog for d in debates]
            kwargs["initialBallots"] = json.dumps(subs)
        else:
            kwargs["initialBallots"] = json.dumps([])

        status = t.current_round.draw_status
        kwargs["total_debates"] = t.current_round.debate_set.count()
        graph_perm = has_permission(self.request.user, 'view.ballotsubmission.graph', self.tournament)
        if (status == Round.Status.CONFIRMED or status == Round.Status.RELEASED) and graph_perm:
            ballots = BallotSubmission.objects.filter(
                debate__round=t.current_round, discarded=False).select_related(
                'submitter', 'debate')
            stats = [{'ballot': bs.serialize(t)} for bs in ballots]
            kwargs["initial_graph_data"] = json.dumps(stats)
        else:
            kwargs["initial_graph_data"] = json.dumps([])

        kwargs["overview_permissions"] = json.dumps({
            "graph": graph_perm,
            "actionlog": action_perm,
            "results": results_perm,
        })

        return super().get_context_data(**kwargs)


class TournamentAssistantHomeView(AssistantMixin, BaseTournamentDashboardHomeView):
    template_name = 'assistant_tournament_index.html'


class TournamentAdminHomeView(AdministratorMixin, BaseTournamentDashboardHomeView):
    template_name = 'tournament_index.html'
    view_permission = True


class CompleteRoundCheckView(AdministratorMixin, RoundMixin, TemplateView):
    template_name = 'round_complete_check.html'
    view_permission = True

    def get_context_data(self, **kwargs):
        prior_rounds_not_completed = self.tournament.round_set.filter(
            Q(break_category=self.round.break_category) | Q(break_category__isnull=True),
            completed=False, seq__lt=self.round.seq,
        )
        kwargs['number_of_prior_rounds_not_completed'] = prior_rounds_not_completed.count()
        kwargs['prior_rounds_not_completed'] = format_html_join(
            ", ",
            "<a href=\"{}\" class=\"alert-link\">{}</a>",
            ((reverse_round('tournament-complete-round-check', r), r.name)
                for r in prior_rounds_not_completed),
        )

        kwargs['num_unconfirmed'] = self.round.debate_set.filter(
            result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
        kwargs['increment_ok'] = kwargs['num_unconfirmed'] == 0
        kwargs['emails_sent'] = BulkNotification.objects.filter(
            tournament=self.tournament, round=self.round, event=BulkNotification.EventType.POINTS).exists()
        return super().get_context_data(**kwargs)


class CompleteRoundToggleSilentView(AdministratorMixin, RoundMixin, PostOnlyRedirectView):
    round_redirect_pattern_name = 'tournament-complete-round-check'
    edit_permission = Permission.SILENCE_ROUND

    def post(self, request, *args, **kwargs):
        self.round.silent = request.POST["state"] != "True"
        self.round.save()

        if self.round.silent:
            messages.success(request, _("%(round)s has been marked as silent.") % {'round': self.round.name})
        else:
            messages.success(request, _("%(round)s has been unmarked as silent.") % {'round': self.round.name})

        return super().post(request, *args, **kwargs)


class CompleteRoundView(RoundMixin, AdministratorMixin, LogActionMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ActionType.ROUND_COMPLETE
    edit_permission = Permission.CONFIRM_ROUND

    def post(self, request, *args, **kwargs):
        self.round.completed = True
        self.round.save()
        self.log_action(round=self.round, content_object=self.round)

        incomplete_rounds = self.tournament.round_set.filter(completed=False)

        if not incomplete_rounds.exists():
            messages.success(request, _("%(round)s has been marked as completed. "
                "All rounds are now completed, so you're done with the tournament! "
                "Congratulations!") % {'round': self.round.name})
            return redirect_tournament('tournament-admin-home', self.tournament)

        elif not self.round.next:
            messages.success(request, _("%(round)s has been marked as completed. "
                "That's the last round in that sequence! Going back to the first "
                "round that hasn't been marked as completed.") % {'round': self.round.name})
            # guaranteed to exist, otherwise the first 'if' statement would have been false
            round_for_redirect = incomplete_rounds.order_by('seq').first()
            return redirect_round('availability-index', round_for_redirect)

        if (self.round.stage == Round.Stage.PRELIMINARY and
                self.round.next.stage == Round.Stage.ELIMINATION):

            incomplete_prelim_rounds = incomplete_rounds.filter(stage=Round.Stage.PRELIMINARY)

            if not incomplete_prelim_rounds.exists():
                messages.success(request, _("%(round)s has been marked as completed. "
                    "You've made it to the end of the preliminary rounds! Congratulations! "
                    "The next step is to generate the break.") % {'round': self.round.name})
                return redirect_tournament('breakqual-index', self.tournament)

            else:
                messages.success(request, _("%(round)s has been marked as completed. "
                    "That was the last preliminary round, but one or more preliminary "
                    "rounds are still not completed. Going back to the first incomplete "
                    "preliminary round.") % {'round': self.round.name})
                round_for_redirect = incomplete_prelim_rounds.order_by('seq').first()
                return redirect_round('availability-index', round_for_redirect)

        else:
            messages.success(request, _("%(this_round)s has been marked as completed. "
                "Moving on to %(next_round)s! Woohoo! Keep it up!") % {
                'this_round': self.round.name, 'next_round': self.round.next.name,
            })
            return redirect_round('availability-index', self.round.next)


class CreateTournamentWizardView(AdministratorMixin, WarnAboutDatabaseUseMixin, SessionWizardView):
    """Create a tournament and apply initial configuration in one wizard (session-backed)."""

    form_list = [
        ('basics', TournamentStartForm),
        ('configure', TournamentConfigureForm),
        ('rr_setup', RoundRobinPrelimSetupForm),
    ]
    condition_dict = {
        'rr_setup': _create_tournament_wizard_show_rr_setup,
    }
    template_name = "create_tournament.html"
    db_warning_severity = messages.ERROR

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        demo_datasets = [
            ('minimal8team', _("8-team generic dataset")),
            ('australs24team', _("24-team Australs dataset")),
            ('bp88team', _("88-team BP dataset")),
        ]
        context['demo_datasets'] = demo_datasets
        demo_slugs = [slug for slug, _ in demo_datasets]
        context['preexisting'] = Tournament.objects.filter(slug__in=demo_slugs).values_list('slug', flat=True)
        return context

    def get_form_kwargs(self, step=None, **kwargs):
        kwargs = super().get_form_kwargs(step=step, **kwargs)
        if step == 'configure':
            kwargs.setdefault('instance', Tournament())
        return kwargs

    def done(self, form_list, form_dict, **kwargs):
        configure = form_dict['configure']
        draw_rr = configure.cleaned_data.get('draw_format') == DRAW_FORMAT_ROUND_ROBIN
        rr_form = form_dict.get('rr_setup') if draw_rr else None
        panels = max(1, int(rr_form.cleaned_data['prelim_panels'])) if rr_form else 1
        skip_rounds = draw_rr and panels > 1

        t = form_dict['basics'].save(skip_rounds=skip_rounds)
        configure.instance = t
        configure.save(skip_rounds=skip_rounds)

        if draw_rr and rr_form:
            num_rr = form_dict['basics'].cleaned_data['num_prelim_rounds']
            t.preferences['draw_rules__prelim_panels'] = panels
            if skip_rounds:
                auto_make_rounds_rr(t, num_rr, panels=panels)
                open_break = BreakCategory.objects.filter(tournament=t, is_general=True).first()
                if open_break:
                    auto_make_break_rounds(open_break, t, False)
            else:
                t.round_set.filter(stage=Round.Stage.PRELIMINARY).update(draw_type=Round.DrawType.ROUNDROBIN)
            clear_all_round_caches(t)

        messages.success(self.request, _("Tournament %(name)s is ready.") % {'name': t.short_name or t.name})
        return HttpResponseRedirect(reverse_tournament('tournament-admin-home', tournament=t))


class ConfigureTournamentView(AdministratorMixin, TournamentMixin, UpdateView):
    model = Tournament
    form_class = TournamentConfigureForm
    template_name = "configure_tournament.html"
    slug_url_kwarg = 'tournament_slug'

    def get_success_url(self):
        t = self.tournament
        return reverse_tournament('tournament-admin-home', tournament=t)


class SetCurrentRoundView(AdministratorMixin, TournamentMixin, FormView):
    template_name = 'set_current_round.html'
    slug_url_kwarg = 'tournament_slug'
    redirect_field_name = 'next'
    page_title = _('Set Current Round')
    page_emoji = '🙏'

    view_permission = True
    edit_permission = Permission.CONFIRM_ROUND

    def get_form_class(self):
        if self.tournament.breakcategory_set.count() <= 1:
            return SetCurrentRoundSingleBreakCategoryForm
        else:
            return SetCurrentRoundMultipleBreakCategoriesForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs

    def get_redirect_to(self, use_default=True):
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, ''),
        )
        if not redirect_to and use_default:
            return reverse_tournament('tournament-admin-home', tournament=self.tournament)
        else:
            return redirect_to

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        from django.utils.http import url_has_allowed_host_and_scheme
        # Copied from django.contrib.auth.views.LoginView.get_success_url
        redirect_to = self.get_redirect_to(use_default=True)
        url_is_safe = url_has_allowed_host_and_scheme(
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


class SetRoundWeightingsView(AdministratorMixin, TournamentMixin, FormView):
    template_name = 'set_round_weights.html'
    form_class = RoundWeightForm
    view_permission = True
    edit_permission = Permission.EDIT_ROUND

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Successfully set round weights for tapered scoring."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_tournament('options-tournament-index', self.tournament)


class FixDebateTeamsView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = "fix_debate_teams.html"

    def get_incomplete_debates(self):
        annotations = {  # annotates with the number of DebateTeams on each side in the debate
            side: Count('debateteam', filter=Q(debateteam__side=side), distinct=True)
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


class StyleGuideView(TemplateView, TabbycatPageTitlesMixin):
    template_name = 'admin/style_guide.html'
    page_subtitle = 'Contextual sub title'


class SetTournamentScheduleView(AdministratorMixin, TournamentMixin, ModelFormSetView):
    template_name = 'tournament_schedule_edit.html'
    formset_model = ScheduleEvent
    form_class = ScheduleEventForm

    edit_permission = Permission.EDIT_EVENTS
    view_permission = Permission.VIEW_EVENTS

    same_view = 'tournament-set-schedule'

    def get_formset_factory_kwargs(self):
        can_edit = has_permission(self.request.user, self.get_edit_permission(), self.tournament)
        kwargs = super().get_formset_factory_kwargs()
        kwargs.update({
            'form': self.form_class,
            'extra': 3 * int(can_edit),
            'can_delete': can_edit,
        })
        return kwargs

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs.update({
            'form_kwargs': {'tournament': self.tournament},
        })
        return kwargs

    def get_formset(self):
        formset = super().get_formset()
        if not has_permission(self.request.user, self.get_edit_permission(), self.tournament):
            for form in formset:
                for field in form.fields.values():
                    field.disabled = True
        return formset

    def get_formset_queryset(self):
        return self.tournament.scheduleevent_set.all()

    def formset_valid(self, formset):
        instances = formset.save(commit=False)
        for ev in instances:
            ev.tournament = self.tournament
            ev.save()

        deleted = formset.deleted_objects
        for ev in deleted:
            ev.delete()

        nsaved = len(instances)
        ndeleted = len(deleted)
        messages.success(
            self.request,
            f"Saved {nsaved} event(s), deleted {ndeleted}.",
        )

        if "add_more" in self.request.POST:
            return redirect_tournament(self.same_view, self.tournament)

        return super().formset_valid(formset)

    def get_success_url(self):
        return reverse_tournament('tournament-set-schedule', self.tournament)


class PublicScheduleView(PublicTournamentPageMixin, VueTableTemplateView):
    template_name = 'public_tournament_schedule.html'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT
    public_page_preference = 'public_schedule'
    page_title = _("Tournament Schedule")
    page_emoji = '⏳'
    cache_timeout = settings.PUBLIC_SLOW_CACHE_TIMEOUT

    def get_table(self):
        events = self.tournament.scheduleevent_set.all()
        table = TabbycatTableBuilder(view=self, sort_key='start_time')
        table.add_schedule_event_columns(events)
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_timezone_label'] = get_current_timezone_name()
        return context
