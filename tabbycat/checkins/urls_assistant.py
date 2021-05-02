from django.urls import path

from . import views

urlpatterns = [
    path('prescan/',
        views.AssistantCheckInPreScanView.as_view(),
        name='assistant-checkin-prescan'),

    path('status/people/',
        views.AssistantCheckInPeopleStatusView.as_view(),
        name='assistant-people-statuses'),
    path('status/venues/',
        views.AssistantCheckInVenuesStatusView.as_view(),
        name='assistant-venues-statuses'),

    path('identifiers/',
        views.AssistantCheckInIdentifiersView.as_view(),
        name='assistant-checkin-identifiers'),
    path('identifiers/print/<kind>/',
        views.AssistantCheckInPrintablesView.as_view(),
        name='assistant-checkin-print'),
]
