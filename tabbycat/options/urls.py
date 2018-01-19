from django.urls import path

from . import views

urlpatterns = [
    # Overview
    path('',
        views.TournamentConfigIndexView.as_view(),
        name='options-tournament-index'),

    # Presets
    path('presets/<slug:preset_name>/confirm/',
        views.ConfirmTournamentPreferencesView.as_view(),
        name="options-presets-confirm"),

    # Per Type
    path('<slug:section>/',
        views.TournamentPreferenceFormView.as_view(),
        name="options-tournament-section"),
]
