from utils.views import *

@admin_required
@tournament_view
def data_index(request, t):
    return r2r(request, 'data/data_index.html')

@admin_required
@tournament_view
def add_institutions(request, t):
    return r2r(request, 'data/add_institutions.html')

@admin_required
@tournament_view
def add_teams(request, t):
    return r2r(request, 'data/add_teams.html')

@admin_required
@tournament_view
def add_adjudicators(request, t):
    return r2r(request, 'data/add_adjudicators.html')