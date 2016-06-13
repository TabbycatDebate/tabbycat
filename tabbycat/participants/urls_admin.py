from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/$',
        views.ParticipantsListView.as_view(),
        name='participants-list'),
    url(r'^team/(?P<pk>\d+)/$',
        views.TeamSummaryView.as_view(),
        name='participants-team-summary'),
    url(r'^adjudicator/(?P<pk>\d+)/$',
        views.AdjudicatorSummaryView.as_view(),
        name='participants-adjudicator-summary'),
]
