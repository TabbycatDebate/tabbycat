from django.urls import path

from participants.models import Adjudicator, Team

from . import views

urlpatterns = [
    # Overviews
    path('',
        views.FeedbackOverview.as_view(),
        name='adjfeedback-overview'),
    path('progress/',
        views.FeedbackProgress.as_view(),
        name='adjfeedback-progress'),

    # Getting/setting values
    path('test/set/',
        views.SetAdjudicatorBaseScoreView.as_view(),
        name='adjfeedback-set-adj-base-score'),
    path('breaking/set/',
        views.SetAdjudicatorBreakingStatusView.as_view(),
        name='adjfeedback-set-adj-breaking-status'),

    # Source
    path('latest/',
        views.LatestFeedbackView.as_view(),
        name='adjfeedback-view-latest'),
    path('important',
        views.ImportantFeedbackView.as_view(),
        name='adjfeedback-view-important'),
    path('comments/',
        views.CommentsFeedbackView.as_view(),
        name='adjfeedback-view-comments'),
    path('source/list/',
        views.FeedbackBySourceView.as_view(),
        name='adjfeedback-view-by-source'),
    path('source/team/<int:pk>/',
        views.FeedbackFromTeamView.as_view(),
        name='adjfeedback-view-from-team'),
    path('source/adjudicator/<int:pk>/',
        views.FeedbackFromAdjudicatorView.as_view(),
        name='adjfeedback-view-from-adjudicator'),
    path('target/list/',
        views.FeedbackByTargetView.as_view(),
        name='adjfeedback-view-by-target'),
    path('target/adjudicator/<int:pk>/',
        views.FeedbackOnAdjudicatorView.as_view(),
        name='adjfeedback-view-on-adjudicator'),

    # Adding
    path('add/',
        views.AdminAddFeedbackIndexView.as_view(),
        name='adjfeedback-add-index'),
    path('add/team/<int:source_id>/',
        views.AdminAddFeedbackView.as_view(model=Team),
        name='adjfeedback-add-from-team'),
    path('add/adjudicator/<int:source_id>/',
        views.AdminAddFeedbackView.as_view(model=Adjudicator),
        name='adjfeedback-add-from-adjudicator'),

    # Updating in bulk
    path('scores/bulk-update/',
        views.UpdateAdjudicatorScoresView.as_view(),
        name='adjfeedback-update-scores-bulk'),

    # Ignoring/Recognizing
    path('ignore/<int:feedback_id>/',
        views.IgnoreFeedbackView.as_view(),
        name='adjfeedback-ignore-feedback'),
    path('confirm/<int:feedback_id>/',
        views.ConfirmFeedbackView.as_view(),
        name='adjfeedback-confirm-feedback'),

    # CSV views
    path('csv/scores.csv',
        views.AdjudicatorScoresCsvView.as_view(),
        name='adjfeedback-csv-scores'),
    path('csv/feedback.csv',
        views.AdjudicatorFeedbackCsvView.as_view(),
        name='adjfeedback-csv-feedback'),
]
