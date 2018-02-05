from django.urls import path

from participants.models import Adjudicator, Team

from . import views

urlpatterns = [
    path('add/',
        views.AssistantAddFeedbackIndexView.as_view(),
        name='adjfeedback-assistant-add-index'),
    path('add/team/<int:source_id>/',
        views.AssistantAddFeedbackView.as_view(model=Team),
        name='adjfeedback-assistant-add-from-team'),
    path('add/adjudicator/<int:source_id>/',
        views.AssistantAddFeedbackView.as_view(model=Adjudicator),
        name='adjfeedback-assistant-add-from-adjudicator'),
]
