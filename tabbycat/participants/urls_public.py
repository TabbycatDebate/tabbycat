from django.urls import path

from . import views

urlpatterns = [
    path('list/',
        views.PublicParticipantsListView.as_view(),
        name='participants-public-list'),
    path('institutions/',
        views.PublicInstitutionsListView.as_view(),
        name='participants-public-institutions-list'),

    path('team/<int:pk>/',
        views.PublicTeamRecordView.as_view(),
        name='participants-public-team-record'),
    path('adjudicator/<int:pk>/',
        views.PublicAdjudicatorRecordView.as_view(),
        name='participants-public-adjudicator-record'),
]
