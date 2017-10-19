from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$',
        views.RandomisedUrlsView.as_view(),
        name='privateurls-list'),
    url(r'^generate/$',
        views.GenerateRandomisedUrlsView.as_view(),
        name='privateurls-generate'),

    url(r'^email/ballot/$',
        views.EmailBallotUrlsView.as_view(),
        name='privateurls-email-ballot'),
    url(r'^email/ballot/confirm/$',
        views.ConfirmEmailBallotUrlsView.as_view(),
        name='privateurls-email-ballot-send'),

    url(r'^email/feedback/$',
        views.EmailFeedbackUrlsView.as_view(),
        name='privateurls-email-feedback'),
    url(r'^email/feedback/confirm/$',
        views.ConfirmEmailFeedbackUrlsView.as_view(),
        name='privateurls-email-feedback-send'),

]
