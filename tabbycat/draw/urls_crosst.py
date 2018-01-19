from django.urls import path

from . import views


urlpatterns = [

    path('all_tournaments_all_institutions/',
        views.AllTournamentsAllInstitutionsView.as_view(),
        name='all-tournaments-all-institutions'),

    path('all_tournaments_all_venues/',
        views.AllTournamentsAllVenuesView.as_view(),
        name='all_tournaments-all-venues'),

    path('all_tournaments_all_teams/',
        views.AllDrawsForAllTeamsView.as_view(),
        name='all-tournaments-all-teams'),

    path('all_tournaments_all_institutions/all_draws/<int:institution_id>',
        views.AllDrawsForInstitutionView.as_view(),
        name='all-draws-for-institution'),

    path('all_tournaments_all_venues/all_draws/<int:venue_id>',
        views.AllDrawsForVenueView.as_view(),
        name='all-draws-for-venue'),

]
