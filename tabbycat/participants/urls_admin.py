from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^records/$',
        views.ParticipantRecordsListView.as_view(),
        name='participants-records-list'),
    url(r'^team/(?P<pk>\d+)/$',
        views.TeamRecordView.as_view(),
        name='participants-team-record'),
    url(r'^adjudicator/(?P<pk>\d+)/$',
        views.AdjudicatorRecordView.as_view(),
        name='participants-adjudicator-record'),
]
