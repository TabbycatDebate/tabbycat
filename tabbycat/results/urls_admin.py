from django.urls import path

from . import views

urlpatterns = [
    # Viewing
    path('round/<int:round_seq>/',
        views.AdminResultsEntryForRoundView.as_view(),
        name='results-round-list'),

    # Inline Actions
    path('round/<int:round_seq>/postpone/<int:debate_id>/',
        views.PostponeDebateView.as_view(),
        name='results-postpone-debate'),

    # Ballots
    path('ballots/<int:pk>/edit/',
        views.AdminEditBallotSetView.as_view(),
        name='results-ballotset-edit'),
    path('debate/<int:debate_id>/new/',
        views.AdminNewBallotSetView.as_view(),
        name='results-ballotset-new'),

    # Ballots Old
    path('ballots/old/<int:pk>/edit/',
        views.OldAdminEditBallotSetView.as_view(),
        name='old-results-ballotset-edit'),
    path('debate/old/<int:debate_id>/new/',
        views.OldAdminNewBallotSetView.as_view(),
        name='old-results-ballotset-new'),
]
