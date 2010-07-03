from django.conf.urls.defaults import *

from django.core.urlresolvers import reverse

from debate import models as m

urlpatterns = patterns('debate.views',
    url(r'^$', 'tournament_home', name='tournament_home'),
    url(r'^config/$', 'tournament_config', name='tournament_config'),
    url(r'^draw/$', 'draw_index', name='draw_index'),
    url(r'^round/(?P<round_seq>\d+)/$',
        'round_index', name='round_index'),

    url(r'^round/(?P<round_seq>\d+)/venues/$',
        'availability', { 'model': 'venue', 'context_name': 'venues' }, 'venue_availability'),
    url(r'^round/(?P<round_seq>\d+)/venues/update/$',
        'update_availability', { 'active_attr': 'venue', 'active_model': m.ActiveVenue, 'update_method': 'set_available_venues' }, 'update_venue_availability'),

    url(r'^round/(?P<round_seq>\d+)/adjudicators/$',
        'availability', { 'model': 'adjudicator', 'context_name': 'adjudicators' }, 'adjudicator_availability'),
    url(r'^round/(?P<round_seq>\d+)/adjudicators/update/$',
        'update_availability', { 'active_attr': 'adjudicator', 'active_model': m.ActiveAdjudicator, 'update_method': 'set_available_adjudicators' }, 'update_adjudicator_availability'),

    url(r'^round/(?P<round_seq>\d+)/people/$',
        'availability', { 'model': 'person', 'context_name': 'people' }, 'people_availability'),
    url(r'^round/(?P<round_seq>\d+)/people/update/$',
        'update_availability', { 'active_attr': None, 'active_model': None, 'update_method': 'set_available_people' }, 'update_people_availability'),

    url(r'^round/(?P<round_seq>\d+)/teams/$',
        'availability', { 'model': 'team', 'context_name': 'teams' }, 'team_availability'),
    url(r'^round/(?P<round_seq>\d+)/teams/update/$',
        'update_availability', { 'active_attr': 'team', 'active_model': m.ActiveTeam, 'update_method': 'set_available_teams' }, 'update_team_availability'),

    url(r'^round/(?P<round_seq>\d+)/checkin/$', 'checkin', name='checkin'),
    url(r'^round/(?P<round_seq>\d+)/checkin/post/$', 'post_checkin', name='post_checkin'),

    url(r'^round/(?P<round_seq>\d+)/draw/$', 'draw',
        name='draw'),
    url(r'^round/(?P<round_seq>\d+)/wordpress_post_draw/$', 'wordpress_post_draw',
        name='wordpress_post_draw'),
    url(r'^round/(?P<round_seq>\d+)/wordpress_post_standings/$', 'wordpress_post_standings',
        name='wordpress_post_standings'),
    url(r'^round/(?P<round_seq>\d+)/draw_display/$', 'draw_display',
        name='draw_display'),
    url(r'^round/(?P<round_seq>\d+)/draw/create/$', 'create_draw',
        name='create_draw'),
    url(r'^round/(?P<round_seq>\d+)/draw/confirm/$', 'confirm_draw',
        name='confirm_draw'),

    url(r'^round/(?P<round_seq>\d+)/draw/venues/$', 'draw_venues_edit',
        name='draw_venues_edit'),
    url(r'^round/(?P<round_seq>\d+)/draw/venues/save/$', 'save_venues',
        name='save_venues'),

    url(r'^round/(?P<round_seq>\d+)/draw/adjudicators/$', 'draw_adjudicators_edit',
        name='draw_adjudicators_edit'),
    url(r'^round/(?P<round_seq>\d+)/draw/adjudicators/_get/$',
        'draw_adjudicators_get',
        name='draw_adjudicators_get'),
    url(r'^round/(?P<round_seq>\d+)/draw/adjudicators/save/$', 'save_adjudicators',
        name='save_adjudicators'),
    url(r'^round/(?P<round_seq>\d+)/_update_importance/$',
        'update_debate_importance',
        name='update_debate_importance'),

    url(r'^round/(?P<round_seq>\d+)/adj_allocation/create/$',
        'create_adj_allocation',
        name='create_adj_allocation'),
    url(r'^round/(?P<round_seq>\d+)/results/$', 'results',
        name='results'),
    url(r'^round/(?P<round_seq>\d+)/team_standings/$', 'team_standings',
        name='team_standings'),
    url(r'^round/(?P<round_seq>\d+)/speaker_standings/$', 'speaker_standings',
        name='speaker_standings'),
    url(r'^debate/(?P<debate_id>\d+)/results/$', 'enter_result',
        name='enter_result'),

    url(r'^round/(?P<round_seq>\d+)/adjudicators/conflicts/$', 'adj_conflicts', name='adj_conflicts'),
    url(r'^adjudicators/scores/$', 'adj_scores', name='adj_scores'),
    url(r'^adjudicators/feedback/$', 'adj_feedback', name='adj_feedback'),
    url(r'^adjudicators/feedback/get/$', 'get_adj_feedback', name='get_adj_feedback'),
    url(r'^adjudicators/feedback/(?P<adjudicator_id>\d+)/$', 
        'enter_feedback', name='enter_feedback'),
    )


