from django.urls import path

from . import views

urlpatterns = [

    path('',
        views.RandomisedUrlsView.as_view(),
        name='privateurls-list'),
    path('generate/',
        views.GenerateRandomisedUrlsView.as_view(),
        name='privateurls-generate'),

    path('email/ballot/',
        views.EmailBallotUrlsView.as_view(),
        name='privateurls-email-ballot'),

    path('email/feedback/',
        views.EmailFeedbackUrlsView.as_view(),
        name='privateurls-email-feedback'),

]
