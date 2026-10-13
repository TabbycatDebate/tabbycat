from django.urls import include, path

from . import csv_views, views

urlpatterns = [

    path('csv/', include([
        path('', csv_views.CSVUploadView.as_view(), name='importer-csv-upload'),
        path('templates/<slug:template_key>/', csv_views.CSVTemplateView.as_view(), name='importer-csv-template'),
        path('<uuid:import_id>/', include([
            path('', csv_views.CSVWizardView.as_view(), name='importer-csv-wizard'),
            path('results/', csv_views.CSVResultsView.as_view(), name='importer-csv-results'),
            path('errors/', csv_views.CSVErrorsView.as_view(), name='importer-csv-errors'),
        ])),
    ])),

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

    path('export/',
        views.ExportArchiveIndexView.as_view(),
        name='exporter-xml-index'),
    path('export/all/',
        views.ExportArchiveAllView.as_view(),
        name='exporter-archive-all'),

]
