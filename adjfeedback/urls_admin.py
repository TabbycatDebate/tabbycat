from django.conf.urls import url

from . import views
from participants.models import Team, Adjudicator

urlpatterns = [
    # Overviews
    url(r'^$',
        views.feedback_overview,
        name='feedback_overview'),
    url(r'^progress/$',
        views.feedback_progress,
        name='feedback_progress'),

    # Getting/setting values
    url(r'^scores/all/$',
        views.adj_scores,
        name='adj_scores'),
    url(r'^scores/get/$',
        views.get_adj_feedback,
        name='get_adj_feedback'),
    url(r'^scores/add/$',
        views.add_feedback,
        name='add_feedback'),
    url(r'^test/set/$',
        views.set_adj_test_score,
        name='set_adj_test_score'),
    url(r'^breaking/set/$',
        views.set_adj_breaking_status,
        name='set_adj_breaking_status'),
    url(r'^notes/test/set/$',
        views.set_adj_note,
        name='set_adj_note'),

    # Source
    url(r'^source/latest/$',
        views.adj_latest_feedback,
        name='adj_latest_feedback'),
    url(r'^source/list/$',
        views.adj_source_feedback,
        name='adj_source_feedback'),
    url(r'^source/team/(?P<team_id>\d+)/$',
        views.team_feedback_list,
        name='team_feedback_list'),
    url(r'^source/adjudicator(?P<adj_id>\d+)/$',
        views.adj_feedback_list,
        name='adj_feedback_list'),

    # Adding
    url(r'^add/team/(?P<source_id>\d+)/$',
        views.TabroomAddFeedbackView.as_view(model=Team),
        name='enter_feedback_team'),
    url(r'^add/adjudicator/(?P<source_id>\d+)/$',
        views.TabroomAddFeedbackView.as_view(model=Adjudicator),
        name='enter_feedback_adjudicator'),

    # URLS
    url(r'^randomised_urls/$',
        views.randomised_urls,
        name='randomised_urls'),
    url(r'^randomised_urls/generate/$',
        views.generate_randomised_urls,
        name='generate_randomised_urls'),
]
