from django.conf.urls import url

from . import views


urlpatterns = [

    url(r'^all_tournaments_all_institutions/$',
        views.AllTournamentsAllInstitutionsView.as_view(),
        name='all-tournaments-all-institutions'),

    url(r'^all_tournaments_all_venues/$',
        views.AllTournamentsAllVenuesView.as_view(),
        name='all_tournaments-all-venues'),

    url(r'^all_tournaments_all_teams/$',
        views.AllDrawsForAllTeamsView.as_view(),
        name='all-tournaments-all-teams'),

    url(r'^all_tournaments_all_institutions/all_draws/(?P<institution_id>\d+)$',
        views.AllDrawsForInstitutionView.as_view(),
        name='all-draws-for-institution'),

    url(r'^all_tournaments_all_venues/all_draws/(?P<venue_id>\d+)$',
        views.AllDrawsForVenueView.as_view(),
        name='all-draws-for-venue'),

]
