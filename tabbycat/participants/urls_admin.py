from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/$',
        views.ParticipantsListView.as_view(),
        name='participants-list'),
    url(r'^team/(?P<pk>\d+)/$',
        views.TeamRecordView.as_view(),
        name='participants-team-record'),
    url(r'^adjudicator/(?P<pk>\d+)/$',
        views.AdjudicatorRecordView.as_view(),
        name='participants-adjudicator-record'),
]
