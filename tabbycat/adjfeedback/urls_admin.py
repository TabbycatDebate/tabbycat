from django.conf.urls import url

from participants.models import Adjudicator, Team

from . import views

urlpatterns = [
    # Overviews
    url(r'^$',
        views.FeedbackOverview.as_view(),
        name='adjfeedback-overview'),
    url(r'^progress/$',
        views.FeedbackProgress.as_view(),
        name='feedback_progress'),

    # Getting/setting values
    url(r'^test/set/$',
        views.SetAdjudicatorTestScoreView.as_view(),
        name='adjfeedback-set-adj-test-score'),
    url(r'^breaking/set/$',
        views.SetAdjudicatorBreakingStatusView.as_view(),
        name='adjfeedback-set-adj-breaking-status'),
    url(r'^notes/test/set/$',
        views.SetAdjudicatorNoteView.as_view(),
        name='adjfeedback-set-adj-note'),
    # Only used in old allocation screen; TODO: deprecate
    url(r'^scores/all/$',
        views.GetAdjScores.as_view(),
        name='adj_scores'),
    url(r'^feedback/get/$',
        views.GetAdjFeedback.as_view(),
        name='get_adj_feedback'),

    # Source
    url(r'^latest/$',
        views.LatestFeedbackView.as_view(),
        name='adjfeedback-view-latest'),
    url(r'^source/list/$',
        views.FeedbackBySourceView.as_view(),
        name='adjfeedback-view-by-source'),
    url(r'^source/team/(?P<pk>\d+)/$',
        views.FeedbackFromTeamView.as_view(),
        name='adjfeedback-view-from-team'),
    url(r'^source/adjudicator/(?P<pk>\d+)/$',
        views.FeedbackFromAdjudicatorView.as_view(),
        name='adjfeedback-view-from-adjudicator'),
    url(r'^target/list/$',
        views.FeedbackByTargetView.as_view(),
        name='adjfeedback-view-by-target'),
    url(r'^target/adjudicator/(?P<pk>\d+)/$',
        views.FeedbackOnAdjudicatorView.as_view(),
        name='adjfeedback-view-on-adjudicator'),
    url(r'^target/adjudicator/json/(?P<pk>\d+)/$',
        views.GetAdjFeedbackJSON.as_view(),
        name='get_adj_feedback_json'),

    # Adding
    url(r'^add/$',
        views.TabroomAddFeedbackIndexView.as_view(),
        name='adjfeedback-add-index'),
    url(r'^add/team/(?P<source_id>\d+)/$',
        views.TabroomAddFeedbackView.as_view(model=Team),
        name='adjfeedback-add-from-team'),
    url(r'^add/adjudicator/(?P<source_id>\d+)/$',
        views.TabroomAddFeedbackView.as_view(model=Adjudicator),
        name='adjfeedback-add-from-adjudicator'),

]
