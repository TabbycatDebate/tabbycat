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
        views.public_feedback_submit,
        name='public_feedback_submit'),
    url(r'^add/team/(?P<source_id>\d+)/$',
        views.PublicAddFeedbackByIdUrlView.as_view(model=Team),
        name='public_enter_feedback_team'),
    url(r'^add/adjudicator/(?P<source_id>\d+)/$',
        views.PublicAddFeedbackByIdUrlView.as_view(model=Adjudicator),
        name='public_enter_feedback_adjudicator'),
    # Submission via Private URL
    url(r'^add/adjudicator/(?P<source_id>\d+)/(?P<url_key>\w+)/$',
        views.PublicAddFeedbackByRandomisedUrlView.as_view(model=Team),
        name='public_enter_feedback_adjudicator_key'),
    url(r'^add/team/(?P<source_id>\d+)/(?P<url_key>\w+)/$',
        views.PublicAddFeedbackByRandomisedUrlView.as_view(model=Adjudicator),
        name='public_enter_feedback_team_key'),
    url(r'^add/success/$',
        views.PublicFeedbackSuccessView.as_view(),
        name='adjfeedback-public-success')
]
