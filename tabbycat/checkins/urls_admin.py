from django.urls import path

from . import views

urlpatterns = [
    path('scan/',
        views.AdminCheckInScanView.as_view(),
        name='admin-checkin-scan'),
    path('statuses/',
        views.AdminCheckInStatusView.as_view(),
        name='admin-checkin-statuses'),
    path('identifiers/',
        views.AdminCheckInIdentifiersView.as_view(),
        name='admin-checkin-identifiers'),
]
