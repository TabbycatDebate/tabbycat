from django.conf.urls import url

from . import views

urlpatterns = [
    # Viewing
    url(r'^round/(?P<round_seq>\d+)/$',
        views.ResultsEntryForRoundView.as_view(),
        name='results-round-list'),

    # JSON updates
    url(r'^ballots_status/$',
        views.BallotsStatusJsonView.as_view(),
        name='results-ballots-graph-data'),
    url(r'^latest_results/$',
        views.LatestResultsJsonView.as_view(),
        name='results-latest-json'),

    # Inline Actions
    url(r'^round/(?P<round_seq>\d+)/postpone/$',
        views.PostponeDebateView.as_view(),
        name='results-postpone-debate'),
    url(r'^round/(?P<round_seq>\d+)/unpostpone/$',
        views.UnpostponeDebateView.as_view(),
        name='results-unpostpone-debate'),

    # Ballot check-in
    url(r'^round/(?P<round_seq>\d+)/checkin/$',
        views.BallotCheckinView.as_view(),
        name='results-ballot-checkin'),
    url(r'^round/(?P<round_seq>\d+)/checkin/detail/$',
        views.BallotCheckinGetDetailsView.as_view(),
        name='results-ballot-checkin-details'),
    url(r'^round/(?P<round_seq>\d+)/checkin/post/$',
        views.PostBallotCheckinView.as_view(),
        name='results-ballot-checkin-post'),

    # Ballots
    url(r'^ballots/(?P<pk>\d+)/edit/$',
        views.EditBallotSetView.as_view(),
        name='results-ballotset-edit'),
    url(r'^debate/(?P<debate_id>\d+)/new/$',
        views.NewBallotSetView.as_view(),
        name='results-ballotset-new'),
]
