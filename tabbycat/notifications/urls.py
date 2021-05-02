from django.urls import path

from . import views

urlpatterns = [
    path('send-test-email/',
        views.TestEmailView.as_view(),
        name='notifications-test-email'),
]
