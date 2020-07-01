from django.urls import path

from participants.models import Adjudicator, Team

from . import views

urlpatterns = [
    # Overviews
    path('progress/',
        views.PublicFeedbackProgress.as_view(),
        name='public_feedback_progress'),

    # Submission via Public Form
    path('add/',
        views.PublicAddFeedbackIndexView.as_view(),
        name='adjfeedback-public-add-index'),
    path('add/team/<int:source_id>/',
        views.PublicAddFeedbackByIdUrlView.as_view(model=Team),
        name='adjfeedback-public-add-from-team-pk'),
    path('add/adjudicator/<int:source_id>/',
        views.PublicAddFeedbackByIdUrlView.as_view(model=Adjudicator),
        name='adjfeedback-public-add-from-adjudicator-pk'),

    # Submission via Private URL
    path('add/t<slug:url_key>/',
        views.SpeakerAddFeedbackByRandomisedUrlView.as_view(),
        name='adjfeedback-public-add-from-team-randomised'),
    path('add/a<slug:url_key>/',
        views.AdjudicatorAddFeedbackByRandomisedUrlView.as_view(),
        name='adjfeedback-public-add-from-adjudicator-randomised'),
]
