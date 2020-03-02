from django.urls import path

from . import views

urlpatterns = [

    path('simple/',
        views.ImporterSimpleIndexView.as_view(),
        name='importer-simple-index'),
    path('simple/institutions/',
        views.ImportInstitutionsWizardView.as_view(),
        name='importer-simple-institutions'),
    path('simple/teams/',
        views.ImportTeamsWizardView.as_view(),
        name='importer-simple-teams'),
    path('simple/adjudicators/',
        views.ImportAdjudicatorsWizardView.as_view(),
        name='importer-simple-adjudicators'),
    path('simple/venues/',
        views.ImportVenuesWizardView.as_view(),
        name='importer-simple-venues'),
]
