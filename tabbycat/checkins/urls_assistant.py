from django.urls import path

from . import views

urlpatterns = [
    path('scan/',
        views.AssistantCheckInScanView.as_view(),
        name='assistant-checkin-scan'),
    path('status/',
        views.AssistantCheckInStatusView.as_view(),
        name='assistant-checkin-status'),
]
