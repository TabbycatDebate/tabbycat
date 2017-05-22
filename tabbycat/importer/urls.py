from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [

    url(r'^simple/$',
        views.ImporterSimpleIndexView.as_view(),
        name='importer-simple-index'),
    url(r'^simple/institutions/$',
        views.ImportInstitutionsWizardView.as_view(),
        name='importer-simple-institutions'),
    url(r'^simple/teams/$',
        views.ImportTeamsWizardView.as_view(),
        name='importer-simple-teams'),
    url(r'^simple/adjudicators/$',
        views.ImportAdjudicatorsWizardView.as_view(),
        name='importer-simple-adjudicators'),
    url(r'^simple/venues/$',
        views.ImportVenuesWizardView.as_view(),
        name='importer-simple-venues'),

    # Private URLs
    url(r'^private-urls/$',
        views.RandomisedUrlsView.as_view(),
        name='randomised-urls-view'),
    url(r'^private-urls/generate/$',
        views.GenerateRandomisedUrlsView.as_view(),
        name='randomised-urls-generate'),

    url(r'^private-urls/email/ballot/$',
        views.EmailBallotUrlsView.as_view(),
        name='email-ballot-urls'),
    url(r'^private-urls/emails/ballot/confirm/$',
        views.ConfirmEmailBallotUrlsView.as_view(),
        name='confirm-ballot-urls-send'),

    url(r'^private-urls/email/feedback/$',
        views.EmailFeedbackUrlsView.as_view(),
        name='email-feedback-urls'),
    url(r'^private-urls/emails/confirm/$',
        views.ConfirmEmailFeedbackUrlsView.as_view(),
        name='confirm-feedback-urls-send'),

    # Old URLs for randomised URLs, now permanent redirects
    url(r'^randomised_urls/$',
        RedirectView.as_view(permanent=True, pattern_name='randomised-urls-view')),
    url(r'^randomised_urls/generate/$',
        RedirectView.as_view(permanent=True, pattern_name='randomised-urls-generate')),
    url(r'^randomised_urls/email/ballot/$',
        RedirectView.as_view(permanent=True, pattern_name='email-ballot-urls')),
    url(r'^randomised_urls/emails/ballot/confirm/$',
        RedirectView.as_view(permanent=True, pattern_name='confirm-ballot-urls-send')),
    url(r'^randomised_urls/email/feedback/$',
        RedirectView.as_view(permanent=True, pattern_name='email-feedback-urls')),
    url(r'^randomised_urls/emails/confirm/$',
        RedirectView.as_view(permanent=True, pattern_name='confirm-feedback-urls-send')),

]
