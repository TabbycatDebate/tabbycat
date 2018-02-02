from django.urls import path

from . import views

urlpatterns = [
    # Viewing
    path('',
        views.AssistantResultsEntryView.as_view(),
        name='results-assistant-round-list'),

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
        views.AssistantEditBallotSetView.as_view(),
        name='results-assistant-ballotset-edit'),
    path('debate/<int:debate_id>/new/',
        views.AssistantNewBallotSetView.as_view(),
        name='results-assistant-ballotset-new'),
]
