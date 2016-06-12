import json
from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from participants.models import Adjudicator
from actionlog.models import ActionLogEntry
from utils.misc import get_ip_address
from utils.views import admin_required, expect_post, public_optional_tournament_view, redirect_tournament, tournament_view
from utils.mixins import HeadlessTemplateView, PublicCacheMixin, VueTableMixin
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin

from .models import BreakCategory, BreakingTeam
from . import forms
from . import breaking


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_results')
def public_break_index(request, t):
    return render(request, "public_break_index.html")


class PublicBreakingTeams(PublicTournamentPageMixin, PublicCacheMixin, VueTableMixin, HeadlessTemplateView):

    template_name = 'base_vue_table.html'

    public_page_preference = 'public_breaking_teams'

    page_emoji = "👑"

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        bc = get_object_or_404(BreakCategory, slug=self.kwargs.get('category'), tournament=t)

        standings = breaking.get_breaking_teams(bc, include_all=True, include_categories=t.pref('public_break_categories'))
        # generated = BreakingTeam.objects.filter(break_category__tournament=t).exists()

        teams_data = []
        for info in standings.standings:
            ddict = []
            ddict.extend(self.ranking_cells(info))
            ddict.extend(self.team_cells(info.team, t))
            ddict.extend(self.metric_cells(info.metrics))
            teams_data.append(ddict)

        self.page_title = bc.name
        kwargs["tableData"] = json.dumps(teams_data)
        return super().get_context_data(**kwargs)


@admin_required
@tournament_view
def breaking_index(request, t):
    return render(request, 'breaking_index.html')


@admin_required
@tournament_view
def breaking_teams(request, t, category):
    bc = get_object_or_404(BreakCategory, slug=category, tournament=t)

    if request.method == "POST":
        form = forms.BreakingTeamsForm(bc, request.POST)
        if form.is_valid():
            form.save()
        ActionLogEntry.objects.log(
            type=ActionLogEntry.ACTION_TYPE_BREAK_EDIT_REMARKS,
            user=request.user, tournament=t, ip_address=get_ip_address(request))
        messages.success(request, "Changes to breaking team remarks saved.")

    else:
        form = forms.BreakingTeamsForm(bc)

    generated = BreakingTeam.objects.filter(break_category__tournament=t).exists()
    return render(request, 'breaking_teams.html', dict(form=form, category=bc, generated=generated))


@expect_post
@tournament_view
def generate_all_breaking_teams(request, t, category):
    """Generates for all break categories; 'category' is used only for the redirect"""
    breaking.generate_all_breaking_teams(t)
    ActionLogEntry.objects.log(
        type=ActionLogEntry.ACTION_TYPE_BREAK_GENERATE_ALL,
        user=request.user, tournament=t, ip_address=get_ip_address(request))
    messages.success(request, "Teams break generated for all break categories.")
    return redirect_tournament('breaking_teams', t, category=category)


@expect_post
@tournament_view
def update_all_breaking_teams(request, t, category):
    """Generates for all break categories; 'category' is used only for the redirect"""
    breaking.update_all_breaking_teams(t)
    ActionLogEntry.objects.log(
        type=ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ALL,
        user=request.user, tournament=t, ip_address=get_ip_address(request))
    messages.success(request, "Teams break updated for all break categories.")
    return redirect_tournament('breaking_teams', t, category=category)


@expect_post
@tournament_view
def update_breaking_teams(request, t, category):
    bc = get_object_or_404(BreakCategory, slug=category, tournament=t)
    breaking.update_breaking_teams(bc)
    ActionLogEntry.objects.log(
        type=ActionLogEntry.ACTION_TYPE_BREAK_UPDATE_ONE, user=request.user,
        tournament=t, ip_address=get_ip_address(request), break_category=bc)
    messages.success(request, "Teams break updated for break category %s." % bc.name)
    return redirect_tournament('breaking_teams', t, category=category)


class BreakingAdjudicators(TournamentMixin, VueTableMixin, HeadlessTemplateView):

    template_name = 'base_vue_table.html'
    page_title = 'Breaking Adjudicators'
    page_emoji = '🎉'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()

        adjs_data = []
        for adj in Adjudicator.objects.filter(breaking=True, tournament=t):
            adjs_data.append(self.adj_cells(adj, t))

        kwargs["tableData"] = json.dumps(adjs_data)
        return super().get_context_data(**kwargs)


class AdminBreakingAdjudicators(LoginRequiredMixin, BreakingAdjudicators):

    def get(self, request, *args, **kwargs):
        messages.info(self.request, "Adjudicators can be marked as breaking in the Feedback section.")
        return super().get(self, request, *args, **kwargs)


class PublicBreakingAdjudicators(PublicTournamentPageMixin, PublicCacheMixin, BreakingAdjudicators):

    public_page_preference = 'public_breaking_adjs'


@admin_required
@tournament_view
def edit_eligibility(request, t):
    context = dict()
    if request.method == "POST":
        form = forms.BreakEligibilityForm(t, request.POST)
        if form.is_valid():
            form.save()
            ActionLogEntry.objects.log(
                type=ActionLogEntry.ACTION_TYPE_BREAK_ELIGIBILITY_EDIT,
                user=request.user, tournament=t, ip_address=get_ip_address(request))
            messages.success(request, "Break eligibility saved.")
            return redirect_tournament('breaking_index', t)
    else:
        form = forms.BreakEligibilityForm(t)

    context['form'] = form
    return render(request, 'edit_eligibility.html', context)
