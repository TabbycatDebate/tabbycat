from django.views.decorators.cache import cache_page
from django.conf import settings

from participants.models import Adjudicator
from actionlog.models import ActionLogEntry
from utils.misc import get_ip_address

from .models import BreakCategory, BreakingTeam
from . import forms
from . import breaking

from utils.views import *


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_results')
def public_break_index(request, t):
    return render(request, "public_break_index.html")


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_breaking_teams')
def public_breaking_teams(request, t, category):
    bc = get_object_or_404(BreakCategory, slug=category, tournament=t)
    standings = breaking.get_breaking_teams(
        bc, include_all=True, include_categories=t.pref('public_break_categories'))
    generated = BreakingTeam.objects.filter(
        break_category__tournament=t).exists()
    return render(request, 'public_breaking_teams.html', dict(
        category=bc, generated=generated, standings=standings))


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


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_breaking_adjs')
def public_breaking_adjs(request, t):
    adjs = Adjudicator.objects.filter(breaking=True, tournament=t)
    return render(request, 'public_breaking_adjs.html', dict(adjs=adjs))


@admin_required
@tournament_view
def breaking_adjs(request, t):
    adjs = Adjudicator.objects.filter(breaking=True, tournament=t)
    return render(request, 'breaking_adjs.html', dict(adjs=adjs))


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
