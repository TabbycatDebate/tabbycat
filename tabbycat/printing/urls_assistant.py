from django.urls import path

from . import views

urlpatterns = [

    # Traditional sheets
    path('scoresheets/',
        views.AssistantPrintScoresheetsView.as_view(),
        name='printing-assistant-scoresheets'),
    path('feedback/',
        views.AssistantPrintFeedbackFormsView.as_view(),
        name='printing-assistant-feedback'),
]
