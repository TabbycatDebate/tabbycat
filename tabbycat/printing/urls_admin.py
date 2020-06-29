from django.urls import path

from . import views

urlpatterns = [

    # Traditional sheets
    path('round/<int:round_seq>/scoresheets/',
        views.AdminPrintScoresheetsView.as_view(),
        name='printing-scoresheets'),
    path('round/<int:round_seq>/feedback/',
        views.AdminPrintFeedbackFormsView.as_view(),
        name='printing-feedback'),

    # Private URL distribution
    path('urls_sheets/teams',
        views.PrintableRandomisedURLsForTeams.as_view(),
        name='printing-urls-teams'),
    path('urls_sheets/adjudicators',
        views.PrintableRandomisedURLsForAdjudicators.as_view(),
        name='printing-urls-adjudicators'),
]
