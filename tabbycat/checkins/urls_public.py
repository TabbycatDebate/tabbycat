from django.urls import path

from . import views

urlpatterns = [
    path('status/people/',
        views.PublicCheckInPeopleStatusView.as_view(),
        name='checkins-public-status'),
    path('submit/<slug:url_key>/',
        views.ParticipantCheckinView.as_view(),
        name='checkins-public-submit'),
]
