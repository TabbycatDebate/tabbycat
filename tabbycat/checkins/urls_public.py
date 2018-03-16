from django.urls import path

from . import views

urlpatterns = [
    path('status/',
        views.PublicCheckInPeopleStatusView.as_view(),
        name='public-checkin-status'),
]
