from django.conf.urls import url

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

]
