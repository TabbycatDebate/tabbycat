from django.urls import path

from . import views

urlpatterns = [
    path('scan/',
        views.AdminCheckInScanView.as_view(),
        name='admin-checkin-scan'),
    path('status/',
        views.AdminCheckInStatusView.as_view(),
        name='admin-checkin-status'),
]
