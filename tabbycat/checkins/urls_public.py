from django.urls import path

from . import views

urlpatterns = [
    path('status/people/',
        views.PublicCheckInPeopleStatusView.as_view(),
        name='public-checkin-status'),
    path('submit/<slug:url_key>/',
        views.ParticipantCheckinView.as_view(),
        name='public-checkin-submit')
]
