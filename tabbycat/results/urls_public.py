from django.urls import include, path

from . import views

urlpatterns = [
    # Viewing
    path('',
        views.PublicResultsIndexView.as_view(),
        name='results-public-index'),
    path('round/<int:round_seq>/',
        views.PublicResultsForRoundView.as_view(),
        name='results-public-round'),
    path('debate/<int:pk>/scoresheets/',
        views.PublicBallotScoresheetsView.as_view(),
        name='results-public-scoresheet-view'),

    # Public Ballots
    path('add/',
        views.PublicBallotSubmissionIndexView.as_view(),
        name='results-public-ballot-submission-index'),
    path('add/adjudicator/<int:adj_id>/',
        views.OldPublicNewBallotSetByIdUrlView.as_view(),
        name='old-results-public-ballotset-new-pk'),

    # Private Ballots
    path('adjudicator/<slug:url_key>/', include([
        path('add/',
            views.OldPublicNewBallotSetByRandomisedUrlView.as_view(),
            name='results-public-ballotset-new-randomised'),
        path('round/<int:round_seq>/view/',
            views.PrivateUrlBallotScoresheetView.as_view(),
            name='results-privateurl-scoresheet-view'),
    ])),

    path('added/',
        views.PostPublicBallotSetSubmissionURLView.as_view(),
        name='post-results-public-ballotset-new'),
]
