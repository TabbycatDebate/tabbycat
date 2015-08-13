from django.conf.urls import *

from . import views

urlpatterns = [

    url(r'^round/(?P<round_seq>\d+)/$',                             views.results,                      name='results'),
    url(r'^status/$',                                               views.results_status_update,        name='results_status_update'),

    url(r'^toggle_postponed/$',                                     views.toggle_postponed,             name='toggle_postponed'),

    url(r'^round/(?P<round_seq>\d+)/ballot_checkin/$',              views.ballot_checkin,               name='ballot_checkin'),
    url(r'^round/(?P<round_seq>\d+)/ballot_checkin/get_details/$',  views.ballot_checkin_get_details,   name='ballot_checkin_get_details'),
    url(r'^round/(?P<round_seq>\d+)/ballot_checkin/post/$',         views.post_ballot_checkin,          name='post_ballot_checkin'),

    url(r'^ballots/(?P<ballotsub_id>\d+)/edit/$',                   views.edit_ballotset,               name='edit_ballotset'),
    url(r'^debate/(?P<debate_id>\d+)/new_ballotset/$',              views.new_ballotset,                name='new_ballotset'),

]