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
    path('identifiers/generate/<kind>/',
        views.AdminCheckInGenerateView.as_view(),
        name='admin-checkin-generate'),
    path('identifiers/print/<kind>/',
        views.AdminCheckInPrintablesView.as_view(),
        name='admin-checkin-print'),
]
