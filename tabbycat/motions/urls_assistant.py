from django.urls import path

from . import views

urlpatterns = [
    path('display/',
        views.AssistantDisplayMotionsView.as_view(),
        name='motions-assistant-display'),
]
