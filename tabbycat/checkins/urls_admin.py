from django.urls import path

from . import views

urlpatterns = [
    path('prescan/',
        views.AdminCheckInPreScanView.as_view(),
        name='admin-checkin-prescan'),

    path('status/people/',
        views.AdminCheckInPeopleStatusView.as_view(),
        name='admin-people-statuses'),
    path('status/venues/',
        views.AdminCheckInVenuesStatusView.as_view(),
        name='admin-venues-statuses'),

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
