from django.urls import path

from . import views

urlpatterns = [
    # Viewing
    path('round/<int:round_seq>/',
        views.AdminResultsEntryForRoundView.as_view(),
        name='results-round-list'),

    # Ballot check-in
    path('round/<int:round_seq>/checkin/',
        views.AdminBallotCheckinView.as_view(),
        name='results-ballot-checkin'),

    # Inline Actions
    path('round/<int:round_seq>/postpone/',
        views.PostponeDebateView.as_view(),
        name='results-postpone-debate'),
    path('round/<int:round_seq>/unpostpone/',
        views.UnpostponeDebateView.as_view(),
        name='results-unpostpone-debate'),

    # Ballots
    path('ballots/<int:pk>/edit/',
        views.AdminEditBallotSetView.as_view(),
        name='results-ballotset-edit'),
    path('debate/<int:debate_id>/new/',
        views.AdminNewBallotSetView.as_view(),
        name='results-ballotset-new'),
]
