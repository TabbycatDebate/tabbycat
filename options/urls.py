from django.conf.urls import url
from django.core.urlresolvers import reverse
from utils.views import *

from . import views

urlpatterns = [

    url(r'^$',              views.tournament_config_index,                                  name='tournament_config_index'),

    url(r'^scoring/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='scoring')),
        name="scoring"),
    url(r'^draw_rules/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='draw_rules')),
        name="draw_rules"),
    url(r'^feedback/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='feedback')),
        name="feedback"),
    url(r'^debate_rules/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='debate_rules')),
        name="debate_rules"),
    url(r'^standings/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='standings')),
        name="standings"),
    url(r'^tab_release/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='tab_release')),
        name="tab_release"),
    url(r'^ui_options/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='ui_options')),
        name="ui_options"),
    url(r'^league_options/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='league_options')),
        name="league_options"),
    url(r'^data_entry/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='data_entry')),
        name="data_entry"),
    url(r'^public_features/$',
        admin_required(views.TournamentPreferenceFormView.as_view(section='public_features')),
        name="public_features"),


    url(r'^presets/$',
        admin_required(views.TournamentPreferenceConfirmView.as_view(preset='australs')),
        name="preset_confirm"),

]