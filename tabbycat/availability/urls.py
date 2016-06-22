from django.conf.urls import url

from . import views
from .models import ActiveAdjudicator, ActiveTeam, ActiveVenue

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
    url(r'adjudicators/update/$', views.update_availability,
        {'active_attr': 'adjudicator',
         'active_model': ActiveAdjudicator,
         'update_method': 'set_available_adjudicators'},
        name='update_adjudicator_availability'),
    url(r'adjudicators/update/breaking/$', views.AvailabilityActivateBreakingAdjs.as_view(),
        name='update_availability_breaking_adjs'),

    # Teams
    url(r'teams/$', views.AvailabilityTypeTeamView.as_view(),
        name='team_availability'),
    url(r'teams/update/$', views.update_availability,
        {'active_attr': 'team',
         'active_model': ActiveTeam,
         'update_method': 'set_available_teams'},
        name='update_team_availability'),
    url(r'teams/update/breaking/$', views.AvailabilityActivateBreakingTeams.as_view(),
        name='update_availability_breaking_teams'),
    url(r'teams/update/advancing/$',
        views.AvailabilityActivateAdvancingTeams.as_view(),
        name='update_availability_advancing_teams'),

    # Venues
    url(r'venues/$', views.AvailabilityTypeVenueView.as_view(),
        name='venue_availability'),
    url(r'venues/update/$', views.update_availability,
        {'active_attr': 'venue',
         'active_model': ActiveVenue,
         'update_method': 'set_available_venues'},
        name='update_venue_availability'),

    # People
    url(r'people/$', views.AvailabilityTypePersonView.as_view(),
        name='people_availability'),
    url(r'people/update/$', views.checkin_update,
        {'active_attr': None,
         'active_model': None,
         'update_method': 'set_available_people'},
        name='update_people_availability'),

]
