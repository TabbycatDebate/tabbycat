from django.conf.urls import url

from participants.models import Adjudicator, Institution, Team

from . import views

urlpatterns = [

    url(r'^data/constraints/adjudicators/$',
        views.AddConstraintsView.as_view(type=Adjudicator),
        name='add_adjudicator_constraints'),
    url(r'^data/constraints/adjudicators/edit/$',
        views.EditConstraintsView.as_view(type=Adjudicator),
        name='edit_adjudicators_constraints'),
    url(r'^data/constraints/adjudicators/confirm/$',
        views.ConfirmConstraintsView.as_view(type=Adjudicator),
        name='confirm_adjudicators_constraints'),

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

    # URLS Generation
    url(r'^randomised_urls/$',
        views.RandomisedUrlsView.as_view(),
        name='randomised-urls-view'),
    url(r'^randomised_urls/generate/$',
        views.GenerateRandomisedUrlsView.as_view(),
        name='randomised-urls-generate'),

    url(r'^randomised_urls/email/ballot/$',
        views.EmailBallotUrlsView.as_view(),
        name='email-ballot-urls'),
    url(r'^randomised_urls/emails/ballot/confirm/$',
        views.ConfirmEmailBallotUrlsView.as_view(),
        name='confirm-ballot-urls-send'),

    url(r'^randomised_urls/email/feedback/$',
        views.EmailFeedbackUrlsView.as_view(),
        name='email-feedback-urls'),
    url(r'^randomised_urls/emails/confirm/$',
        views.ConfirmEmailFeedbackUrlsView.as_view(),
        name='confirm-feedback-urls-send'),

    url(r'^old_importer/institutions/$',                        views.add_institutions,         name='add_institutions'),
    url(r'^old_importer/institutions/edit/$',                   views.edit_institutions,        name='edit_institutions'),
    url(r'^old_importer/institutions/confirm/$',                views.confirm_institutions,     name='confirm_institutions'),
    url(r'^old_importer/teams/$',                               views.add_teams,                name='add_teams'),

    url(r'^old_importer/teams/edit/$',                          views.edit_teams,               name='edit_teams'),
    url(r'^old_importer/teams/confirm/$',                       views.confirm_teams,            name='confirm_teams'),
    url(r'^old_importer/adjudicators/$',                        views.add_adjudicators,         name='add_adjudicators'),

    url(r'^old_importer/adjudicators/edit/$',                   views.edit_adjudicators,        name='edit_adjudicators'),
    url(r'^old_importer/adjudicators/confirm/$',                views.confirm_adjudicators,     name='confirm_adjudicators'),
    url(r'^old_importer/venues/$',                              views.add_venues,               name='add_venues'),

    url(r'^old_importer/venues/edit/$',                         views.edit_venues,              name='edit_venues'),
    url(r'^old_importer/venues/confirm/$',                      views.confirm_venues,           name='confirm_venues'),
    url(r'^data/constraints/institutions/$',

        views.AddConstraintsView.as_view(type=Institution),
        name='add_institution_constraints'),
    url(r'^data/constraints/institutions/edit/$',
        views.EditConstraintsView.as_view(type=Institution),
        name='edit_institutions_constraints'),
    url(r'^data/constraints/institutions/confirm/$',
        views.ConfirmConstraintsView.as_view(type=Institution),
        name='confirm_institutions_constraints'),

    url(r'^data/constraints/teams/$',
        views.AddConstraintsView.as_view(type=Team),
        name='add_team_constraints'),
    url(r'^data/constraints/teams/edit/$',
        views.EditConstraintsView.as_view(type=Team),
        name='edit_teams_constraints'),
    url(r'^data/constraints/teams/confirm/$',
        views.ConfirmConstraintsView.as_view(type=Team),
        name='confirm_teams_constraints'),
]
