from django.conf.urls import url
from django.views.generic.base import RedirectView

from participants.models import Adjudicator, Team

from . import views

urlpatterns = [
    # Overviews
    url(r'^progress/$',
        views.PublicFeedbackProgress.as_view(),
        name='public_feedback_progress'),

    # Transitional provision added 7/10/2017, remove after 7/11/2017
    url(r'^feedback_progress/$',
        RedirectView.as_view(url='/%(tournament_slug)s/feedback/progress/', permanent=True)),

    # Submission via Public Form
    url(r'^add/$',
        views.PublicAddFeedbackIndexView.as_view(),
        name='adjfeedback-public-add-index'),
    url(r'^add/team/(?P<source_id>\d+)/$',
        views.PublicAddFeedbackByIdUrlView.as_view(model=Team),
        name='adjfeedback-public-add-from-team-pk'),
    url(r'^add/adjudicator/(?P<source_id>\d+)/$',
        views.PublicAddFeedbackByIdUrlView.as_view(model=Adjudicator),
        name='adjfeedback-public-add-from-adjudicator-pk'),

    # Submission via Private URL
    url(r'^add/t(?P<url_key>\w+)/$',
        views.PublicAddFeedbackByRandomisedUrlView.as_view(model=Team),
        name='adjfeedback-public-add-from-team-randomised'),
    url(r'^add/a(?P<url_key>\w+)/$',
        views.PublicAddFeedbackByRandomisedUrlView.as_view(model=Adjudicator),
        name='adjfeedback-public-add-from-adjudicator-randomised'),
]
