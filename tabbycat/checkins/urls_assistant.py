from django.urls import path

from . import views

urlpatterns = [
    path('prescan/',
        views.AssistantCheckInPreScanView.as_view(),
        name='assistant-checkin-prescan'),
    path('scan/',
        views.AssistantCheckInScanView.as_view(),
        name='assistant-checkin-scan'),

    path('status/',
        views.AssistantCheckInStatusView.as_view(),
        name='assistant-checkin-statuses'),
    path('identifiers/',
        views.AssistantCheckInIdentifiersView.as_view(),
        name='assistant-checkin-identifiers'),
    path('identifiers/print/<kind>/',
        views.AssistantCheckInPrintablesView.as_view(),
        name='assistant-checkin-print'),
]
