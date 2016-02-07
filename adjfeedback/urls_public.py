from django.conf.urls import url
from participants.models import Team, Adjudicator
from . import views

urlpatterns = [
    # Overviews
    url(r'^feedback_progress/$',
        views.public_feedback_progress,
        name='public_feedback_progress'),
    # Submission
    url(r'^add/$',
        views.public_feedback_submit,
        name='public_feedback_submit'),
    url(r'^add/team/(?P<source_id>\d+)/$',
        views.public_enter_feedback_id,
        {'source_type': Team},
        name='public_enter_feedback_team'),
    url(r'^add/team/h/(?P<url_key>\w+)/$',
        views.public_enter_feedback_key,
        {'source_type': Team},
        name='public_enter_feedback_team_key'),
    url(r'^add/adjudicator/(?P<source_id>\d+)/$',
        views.public_enter_feedback_id,
        {'source_type': Adjudicator},
        name='public_enter_feedback_adjudicator'),
    url(r'^add/adjudicator/h/(?P<url_key>\w+)/$',
        views.public_enter_feedback_key,
        {'source_type': Adjudicator},
        name='public_enter_feedback_adjudicator_key'),
]
