from django.conf.urls import url
from participants.models import Team, Adjudicator
from . import views

urlpatterns = [
    # Overviews
    url(r'^feedback_progress/$',
        views.public_feedback_progress,
        name='public_feedback_progress'),

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

    url(r'^add/success/$',
        views.PublicFeedbackSuccessView.as_view(),
        name='adjfeedback-public-success')
]
