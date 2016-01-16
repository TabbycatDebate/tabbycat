from django.conf.urls import url

from . import views
from .models import ActiveTeam, ActiveVenue, ActiveAdjudicator

urlpatterns = [

    url(r'^$',                       views.availability_index,   name='availability_index'),

    url(r'people/$',                views.checkin_results,
        { 'model': 'person', 'context_name': 'people' }, 'people_availability'),
    url(r'people/update/$',         views.checkin_update,
        { 'active_attr': None, 'active_model': None, 'update_method': 'set_available_people' },
        'update_people_availability'),

    url(r'teams/$',                 views.availability,
        { 'model': 'team', 'context_name': 'teams' }, 'team_availability'),
    url(r'teams/update/$',          views.update_availability,
        { 'active_attr': 'team', 'active_model': ActiveTeam, 'update_method': 'set_available_teams' },
        'update_team_availability'),

    url(r'venues/$',                views.availability,
        { 'model': 'venue', 'context_name': 'venues' }, 'venue_availability'),
    url(r'venues/update/$',         views.update_availability,
        { 'active_attr': 'venue', 'active_model': ActiveVenue, 'update_method': 'set_available_venues' },
        'update_venue_availability'),

    url(r'adjudicators/$',          views.availability,
        { 'model': 'adjudicator', 'context_name': 'adjudicators' }, 'adjudicator_availability'),
    url(r'adjudicators/update/$',   views.update_availability,
        { 'active_attr': 'adjudicator', 'active_model': ActiveAdjudicator, 'update_method': 'set_available_adjudicators' },
        'update_adjudicator_availability'),

]