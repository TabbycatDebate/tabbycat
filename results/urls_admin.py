from django.conf.urls import *

from . import views

urlpatterns = [
    # Viewing
    url(r'^round/(?P<round_seq>\d+)/$',
        views.results,
        name='results'),

    # JSON updates
    url(r'^ballots_status/$',
        views.ballots_status,
        name='ballots_status'),
    url(r'^latest_results/$',
        views.latest_results,
        name='latest_results'),

    # Inline Actions
    url(r'^toggle_postponed/$',
        views.toggle_postponed,
        name='toggle_postponed'),
    url(r'^round/(?P<round_seq>\d+)/checkin/$',
        views.ballot_checkin,
        name='ballot_checkin'),
    url(r'^round/(?P<round_seq>\d+)/checkin/detail/$',
        views.ballot_checkin_get_details,
        name='ballot_checkin_get_details'),
    url(r'^round/(?P<round_seq>\d+)/checkin/post/$',
        views.post_ballot_checkin,
        name='post_ballot_checkin'),

    # Ballots
    url(r'^ballots/(?P<ballotsub_id>\d+)/edit/$',
        views.edit_ballotset,
        name='edit_ballotset'),
    url(r'^debate/(?P<debate_id>\d+)/new/$',
        views.new_ballotset,
        name='new_ballotset'),
]
