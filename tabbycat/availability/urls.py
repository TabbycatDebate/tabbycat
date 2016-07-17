from django.conf.urls import url

from . import views

urlpatterns = [
    # Overview
    url(r'^$',
        views.AvailabilityIndexView.as_view(),
        name='availability_index'),

    # # Bulk Updates
    url(r'all/update/$', views.AvailabilityActivateAll.as_view(),
        name='update_availability_all'),
    url(r'previous/update/$', views.AvailabilityActivateFromPrevious.as_view(),
        name='update_availability_previous'),

    # Adjs
    url(r'adjudicators/$', views.AvailabilityTypeAdjudicatorView.as_view(),
        name='adjudicator_availability'),
    url(r'adjudicators/update/$', views.AvailabilityUpdateAdjudicators.as_view(),
        name='update_adjudicator_availability'),
    url(r'adjudicators/update/breaking/$', views.AvailabilityActivateBreakingAdjs.as_view(),
        name='update_availability_breaking_adjs'),

    # Teams
    url(r'teams/$', views.AvailabilityTypeTeamView.as_view(),
        name='team_availability'),
    url(r'teams/update/$', views.AvailabilityUpdateTeams.as_view(),
        name='update_team_availability'),

    # Venues
    url(r'venues/$', views.AvailabilityTypeVenueView.as_view(),
        name='venue_availability'),
    url(r'venues/update/$', views.AvailabilityUpdateVenues.as_view(),
        name='update_venue_availability'),

]
