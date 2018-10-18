from django.urls import path

from . import views

urlpatterns = [
    path('',
        views.CustomEmailCreateView.as_view(),
        name='notifications-email'),
]
