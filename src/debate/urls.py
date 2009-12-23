from django.conf.urls.defaults import *

from django.core.urlresolvers import reverse

urlpatterns = patterns('debate.views',
                       url(r'^$', 'index', name='debate_index'),
                       url(r'^round/(?P<round_id>\d+)/venues/$',
                           'venue_availability', name='venue_availability'),
                       url(r'^round/(?P<round_id>\d+)/venues/update/$',
                           'update_venue_availability', name='update_venue_availability'),
                      )

