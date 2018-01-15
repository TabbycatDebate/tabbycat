from django.conf.urls import url

from . import views

urlpatterns = [
    # Viewing
    url(r'^round/(?P<round_seq>\d+)/$',
        views.AdminResultsEntryForRoundView.as_view(),
        name='results-round-list'),

    # Inline Actions
    url(r'^round/(?P<round_seq>\d+)/postpone/$',
        views.PostponeDebateView.as_view(),
        name='results-postpone-debate'),
    url(r'^round/(?P<round_seq>\d+)/unpostpone/$',
        views.UnpostponeDebateView.as_view(),
        name='results-unpostpone-debate'),

    # Ballots
    url(r'^ballots/(?P<pk>\d+)/edit/$',
        views.AdminEditBallotSetView.as_view(),
        name='results-ballotset-edit'),
    url(r'^debate/(?P<debate_id>\d+)/new/$',
        views.AdminNewBallotSetView.as_view(),
        name='results-ballotset-new'),
]
