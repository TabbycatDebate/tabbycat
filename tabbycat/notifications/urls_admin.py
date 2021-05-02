from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.CustomEmailCreateView.as_view(),
        name='notifications-email'),

    path('event-webhook/<slug:key>',
        views.EmailEventWebhookView.as_view(),
        name='notifications-webhook'),

    path('status/',
        views.EmailStatusView.as_view(),
        name='notifications-status'),
]
