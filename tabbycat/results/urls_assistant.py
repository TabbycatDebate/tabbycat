from django.urls import path

from . import views

urlpatterns = [
    # Viewing
    path('',
        views.AssistantResultsEntryView.as_view(),
        name='results-assistant-round-list'),

    # Ballots
    path('ballots/<int:pk>/edit/',
        views.AssistantEditBallotSetView.as_view(),
        name='results-assistant-ballotset-edit'),
    path('debate/<int:debate_id>/new/',
        views.AssistantNewBallotSetView.as_view(),
        name='results-assistant-ballotset-new'),

    # Ballots Old
    path('ballots/old/<int:pk>/edit/',
        views.OldAssistantEditBallotSetView.as_view(),
        name='old-results-assistant-ballotset-edit'),
    path('debate/old/<int:debate_id>/new/',
        views.OldAssistantNewBallotSetView.as_view(),
        name='old-results-assistant-ballotset-new'),
]
