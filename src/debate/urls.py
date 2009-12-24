from django.conf.urls.defaults import *

from django.core.urlresolvers import reverse

urlpatterns = patterns('debate.views',
    url(r'^$', 'index', name='debate_index'),
    url(r'^round/(?P<round_id>\d+)/venues/$',
        'venue_availability', name='venue_availability'),
    url(r'^round/(?P<round_id>\d+)/venues/update/$',
        'update_venue_availability', name='update_venue_availability'),
    url(r'^round/(?P<round_id>\d+)/adjudicators/$',
        'adjudicator_availability', name='adjudicator_availability'),
    url(r'^round/(?P<round_id>\d+)/adjudicators/update/$',
        'update_adjudicator_availability', name='update_adjudicator_availability'),
    url(r'^round/(?P<round_id>\d+)/teams/$',
        'team_availability', name='team_availability'),
    url(r'^round/(?P<round_id>\d+)/teams/update/$',
        'update_team_availability', name='update_team_availability'),
    url(r'^round/(?P<round_id>\d+)/draw/$', 'draw',
        name='draw'),
    url(r'^round/(?P<round_id>\d+)/draw/create/$', 'create_draw',
        name='create_draw'),
    url(r'^round/(?P<round_id>\d+)/draw/confirm/$', 'confirm_draw',
        name='confirm_draw'),
    )

