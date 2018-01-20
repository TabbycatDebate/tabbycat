from django.urls import path

from . import views

urlpatterns = [
    # Viewing
    path('round/<int:round_seq>/',
        views.ResultsEntryForRoundView.as_view(),
        name='results-round-list'),

    # JSON updates
    path('json/status/',
        views.BallotsStatusJsonView.as_view(),
        name='results-ballots-graph-data'),

    # Inline Actions
    path('round/<int:round_seq>/postpone/',
        views.PostponeDebateView.as_view(),
        name='results-postpone-debate'),
    path('round/<int:round_seq>/unpostpone/',
        views.UnpostponeDebateView.as_view(),
        name='results-unpostpone-debate'),

    # Ballot check-in
    path('round/<int:round_seq>/checkin/',
        views.BallotCheckinView.as_view(),
        name='results-ballot-checkin'),
    path('round/<int:round_seq>/checkin/detail/',
        views.BallotCheckinGetDetailsView.as_view(),
        name='results-ballot-checkin-details'),
    path('round/<int:round_seq>/checkin/post/',
        views.PostBallotCheckinView.as_view(),
        name='results-ballot-checkin-post'),

    # Ballots
    path('ballots/<int:pk>/edit/',
        views.EditBallotSetView.as_view(),
        name='results-ballotset-edit'),
    path('debate/<int:debate_id>/new/',
        views.NewBallotSetView.as_view(),
        name='results-ballotset-new'),
]
