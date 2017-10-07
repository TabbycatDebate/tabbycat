from django.conf.urls import url

from . import views

urlpatterns = [
    # Overview
    url(r'^$',
        views.TournamentConfigIndexView.as_view(),
        name='options-tournament-index'),

    # Presets
    url(r'^presets/(?P<preset_name>\w+)/confirm/$',
        views.ConfirmTournamentPreferencesView.as_view(),
        name="options-presets-confirm"),

    # Per Type
    url(r'^(?P<section>\w+)/$',
        views.TournamentPreferenceFormView.as_view(),
        name="options-tournament-section"),
]
