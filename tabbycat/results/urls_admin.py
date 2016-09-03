from django.conf.urls import url

from . import views

urlpatterns = [
    # Viewing
    url(r'^round/(?P<round_seq>\d+)/$',
        views.ResultsEntryForRoundView.as_view(),
        name='results'),

    # JSON updates
    url(r'^ballots_status/$',
        views.ballots_status,
        name='ballots_status'),
    url(r'^latest_results/$',
        views.latest_results,
        name='latest_results'),

    # Inline Actions
    url(r'^round/(?P<round_seq>\d+)/postpone/$',
        views.PostponeDebateView.as_view(),
        name='postpone_debate'),
    url(r'^round/(?P<round_seq>\d+)/unpostpone/$',
        views.UnpostponeDebateView.as_view(),
        name='unpostpone_debate'),
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
    url(r'^ballots/(?P<pk>\d+)/edit/$',
        views.EditBallotSetView.as_view(),
        name='edit_ballotset'),
    url(r'^debate/(?P<debate_id>\d+)/new/$',
        views.NewBallotSetView.as_view(),
        name='new_ballotset'),
]
