from django.urls import path

from . import views

urlpatterns = [
    path('list/',
        views.AssistantParticipantsListView.as_view(),
        name='participants-assistant-list'),
    path('institutions/',
        views.AssistantInstitutionsListView.as_view(),
        name='participants-assistant-institutions-list'),
    path('code-names/',
        views.AssistantCodeNamesListView.as_view(),
        name='participants-assistant-code-names-list'),
]
