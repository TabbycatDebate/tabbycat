from django.conf.urls import url

from . import views

urlpatterns = [
    # Viewing
    url(r'^$',
        views.PublicResultsIndexView.as_view(),
        name='public_results_index'),
    url(r'^round/(?P<round_seq>\d+)/$',
        views.PublicResultsForRoundView.as_view(),
        name='public_results'),
    url(r'^debate/(?P<pk>\d+)/scoresheets/$',
        views.PublicBallotScoresheetsView.as_view(),
        name='public_ballots_view'),

    # Ballots
    url(r'^add/$',
        views.PublicBallotSubmissionIndexView.as_view(),
        name='public_ballot_submit'),
    url(r'^add/adjudicator/(?P<adj_id>\d+)/$',
        views.PublicNewBallotSetByIdUrlView.as_view(),
        name='public_new_ballotset'),
    url(r'^add/a(?P<url_key>\w+)/$',
        views.PublicNewBallotSetByRandomisedUrlView.as_view(),
        name='public_new_ballotset_key'),
]
