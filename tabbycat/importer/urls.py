from django.conf.urls import url

from participants.models import Adjudicator, Institution, Team

from . import views

urlpatterns = [

    url(r'^data/$',                                     views.data_index,               name='data_index'),

    url(r'^data/institutions/$',                        views.add_institutions,         name='add_institutions'),
    url(r'^data/institutions/edit/$',                   views.edit_institutions,        name='edit_institutions'),
    url(r'^data/institutions/confirm/$',                views.confirm_institutions,     name='confirm_institutions'),

    url(r'^data/teams/$',                               views.add_teams,                name='add_teams'),
    url(r'^data/teams/edit/$',                          views.edit_teams,               name='edit_teams'),
    url(r'^data/teams/confirm/$',                       views.confirm_teams,            name='confirm_teams'),

    url(r'^data/adjudicators/$',                        views.add_adjudicators,         name='add_adjudicators'),
    url(r'^data/adjudicators/edit/$',                   views.edit_adjudicators,        name='edit_adjudicators'),
    url(r'^data/adjudicators/confirm/$',                views.confirm_adjudicators,     name='confirm_adjudicators'),

    url(r'^data/venues/$',                              views.add_venues,               name='add_venues'),
    url(r'^data/venues/edit/$',                         views.edit_venues,              name='edit_venues'),
    url(r'^data/venues/confirm/$',                      views.confirm_venues,           name='confirm_venues'),

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

    url(r'^data/constraints/adjudicators/$',
        views.AddConstraintsView.as_view(type=Adjudicator),
        name='add_adjudicator_constraints'),
    url(r'^data/constraints/adjudicators/edit/$',
        views.EditConstraintsView.as_view(type=Adjudicator),
        name='edit_adjudicators_constraints'),
    url(r'^data/constraints/adjudicators/confirm/$',
        views.ConfirmConstraintsView.as_view(type=Adjudicator),
        name='confirm_adjudicators_constraints'),
        

    url(r'^visual/$',
        views.ImporterVisualIndexView.as_view(),
        name='importer-visual-index'),
    url(r'^visual/institutions/$',
        views.ImportInstitutionsWizardView.as_view(),
        name='importer-visual-institutions'),
    url(r'^visual/teams/$',
        views.ImportTeamsWizardView.as_view(),
        name='importer-visual-teams'),
    url(r'^visual/adjudicators/$',
        views.ImportAdjudicatorsWizardView.as_view(),
        name='importer-visual-adjudicators'),
]
