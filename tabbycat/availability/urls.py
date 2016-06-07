from django.conf.urls import url

from . import views
from .models import ActiveAdjudicator, ActiveTeam, ActiveVenue

urlpatterns = [

    # Overview
    url(r'^$',
        views.availability_index,
        name='availability_index'),

    # All
    url(r'all/update/$',
        views.update_availability_all,
        name='update_availability_all'),
    url(r'all/update_previous/$',
        views.update_availability_previous,
        name='update_availability_previous'),

    # People
    url(r'people/$',
        views.checkin_results,
        {'model': 'person',
         'context_name': 'people'},
        name='people_availability'),
    url(r'people/update/$',
        views.checkin_update,
        {'active_attr': None,
         'active_model': None,
         'update_method': 'set_available_people'},
        name='update_people_availability'),

    # Teams
    url(r'teams/$',
        views.availability,
        {'model': 'team',
         'context_name': 'teams'},
        name='team_availability'),
    url(r'teams/update/$',
        views.update_availability,
        {'active_attr': 'team',
         'active_model': ActiveTeam,
         'update_method': 'set_available_teams'},
        name='update_team_availability'),
    url(r'teams/update/breaking/$',
        views.update_availability_breaking_teams,
        name='update_availability_breaking_teams'),
    url(r'teams/update/advancing/$',
        views.update_availability_advancing_teams,
        name='update_availability_advancing_teams'),

    # Venues
    url(r'venues/$', views.availability, {'model': 'venue',
                                          'context_name': 'venues'},
        'venue_availability'),
    url(r'venues/update/$',
        views.update_availability,
        {'active_attr': 'venue',
         'active_model': ActiveVenue,
         'update_method': 'set_available_venues'},
        name='update_venue_availability'),

    # Adjs
    url(r'adjudicators/$',
        views.availability,
        {'model': 'adjudicator',
         'context_name': 'adjudicators'},
        name='adjudicator_availability'),
    url(r'adjudicators/update/$',
        views.update_availability,
        {'active_attr': 'adjudicator',
         'active_model': ActiveAdjudicator,
         'update_method': 'set_available_adjudicators'},
        name='update_adjudicator_availability'),
    url(r'adjudicators/update/breaking/$',
        views.update_availability_breaking_adjs,
        name='update_availability_breaking_adjs'),
]
