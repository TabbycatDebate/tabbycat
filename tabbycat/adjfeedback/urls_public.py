from django.urls import path
from django.views.generic.base import RedirectView

from participants.models import Adjudicator, Team

from . import views

urlpatterns = [
    # Overviews
    path('progress/',
        views.PublicFeedbackProgress.as_view(),
        name='public_feedback_progress'),

    # Transitional provision added 7/10/2017, remove after 7/11/2017
    path('feedback_progress/',
        RedirectView.as_view(url='/%(tournament_slug)s/feedback/progress/', permanent=True)),

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
        views.PublicAddFeedbackByRandomisedUrlView.as_view(model=Team),
        name='adjfeedback-public-add-from-team-randomised'),
    path('add/a<slug:url_key>/',
        views.PublicAddFeedbackByRandomisedUrlView.as_view(model=Adjudicator),
        name='adjfeedback-public-add-from-adjudicator-randomised'),
]
