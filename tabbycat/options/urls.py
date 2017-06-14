from django.conf.urls import url

from . import views

urlpatterns = [
    # Overview
    url(r'^$',
        views.TournamentConfigIndexView.as_view(),
        name='options-tournament-index'),

    # Per Type
    url(r'^scoring/$',
        views.TournamentPreferenceFormView.as_view(section_slug='scoring'),
        name="options-tournament-scoring"),
    url(r'^draw_rules/$',
        views.TournamentPreferenceFormView.as_view(section_slug='draw_rules'),
        name="options-tournament-draw-rules"),
    url(r'^feedback/$',
        views.TournamentPreferenceFormView.as_view(section_slug='feedback'),
        name="options-tournament-feedback"),
    url(r'^debate_rules/$',
        views.TournamentPreferenceFormView.as_view(section_slug='debate_rules'),
        name="options-tournament-debate-rules"),
    url(r'^standings/$',
        views.TournamentPreferenceFormView.as_view(section_slug='standings'),
        name="options-tournament-standings"),
    url(r'^tab_release/$',
        views.TournamentPreferenceFormView.as_view(section_slug='tab_release'),
        name="options-tournament-tab-release"),
    url(r'^ui_options/$',
        views.TournamentPreferenceFormView.as_view(section_slug='ui_options'),
        name="options-tournament-ui"),
    url(r'^league_options/$',
        views.TournamentPreferenceFormView.as_view(section_slug='league_options'),
        name="options-tournament-league"),
    url(r'^data_entry/$',
        views.TournamentPreferenceFormView.as_view(section_slug='data_entry'),
        name="options-tournament-data-entry"),
    url(r'^public_features/$',
        views.TournamentPreferenceFormView.as_view(section_slug='public_features'),
        name="options-tournament-public-features"),

    # Presets
    url(r'^presets/confirm/(?P<preset_name>\w+)/$',
        views.ConfirmTournamentPreferencesView.as_view(),
        name="tournament_preference_confirm"),
    url(r'^presets/apply/(?P<preset_name>\w+)/$',
        views.ApplyTournamentPreferencesView.as_view(),
        name="tournament_preference_apply"),
]
