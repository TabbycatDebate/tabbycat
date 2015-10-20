from utils.views import *

from . import forms

from participants.models import Institution

@admin_required
@tournament_view
def data_index(request, t):
    return r2r(request, 'data_index.html')

@admin_required
@tournament_view
def add_institutions(request, t):
    form = forms.AddInstitutionsForm
    return r2r(request, 'add_institutions.html')


@admin_required
@tournament_view
def add_venues(request, t):
    form = forms.AddVenuesForm
    return r2r(request, 'add_venues.html')

@admin_required
@tournament_view
def add_teams(request, t):
    institutions = Institution.objects.all()
    form = forms.AddTeamsForm
    return r2r(request, 'add_teams.html', dict(institutions=institutions))

@admin_required
@tournament_view
def add_adjudicators(request, t):
    institutions = Institution.objects.all()
    form = forms.AddAdjudicatorsForm
    return r2r(request, 'add_adjudicators.html', dict(institutions=institutions))