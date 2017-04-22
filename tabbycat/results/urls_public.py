from django.conf.urls import url

from . import views

urlpatterns = [
    # Viewing
    url(r'^$',
        views.PublicResultsIndexView.as_view(),
        name='results-public-index'),
    url(r'^round/(?P<round_seq>\d+)/$',
        views.PublicResultsForRoundView.as_view(),
        name='results-public-round'),
    url(r'^debate/(?P<pk>\d+)/scoresheets/$',
        views.PublicBallotScoresheetsView.as_view(),
        name='results-public-scoresheet-view'),

    # Public Ballots
    url(r'^add/$',
        views.PublicBallotSubmissionIndexView.as_view(),
        name='results-public-ballot-submission-index'),
    url(r'^add/adjudicator/(?P<adj_id>\d+)/$',
        views.PublicNewBallotSetByIdUrlView.as_view(),
        name='results-public-ballotset-new-pk'),

    # Private Ballots
    url(r'^add/a(?P<url_key>\w+)/$',
        views.PublicNewBallotSetByRandomisedUrlView.as_view(),
        name='results-public-ballotset-new-randomised'),

    url(r'^added/$',
        views.PostPublicBallotSetSubmissionURLView.as_view(),
        name='post-results-public-ballotset-new'),
]
