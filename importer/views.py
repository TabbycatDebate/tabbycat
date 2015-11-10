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
    print("adding insts")
    #form = forms.AddInstitutionsForm
    return r2r(request, 'add_institutions.html')

@admin_required
@expect_post
@tournament_view
def confirm_institutions(request, t):
    institutions = []
    institution_lines = request.POST['institutions_raw'].split('\n')
    for line in institution_lines:
        try:
            full_name = line.split(',')[0].strip()
            short_name = line.split(',')[1].strip()
            institution = Institution(name=full_name, code=short_name)
            institutions.append(institution)
        except:
            pass # TODO

    return r2r(request, 'confirm_institutions.html', dict(institutions=institutions))

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