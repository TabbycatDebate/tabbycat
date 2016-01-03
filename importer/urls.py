from django.conf.urls import *
from django.core.urlresolvers import reverse

from . import views

urlpatterns = [

    url(r'^data/$',                         views.data_index,           name='data_index'),

    url(r'^data/institutions/$',            views.add_institutions,     name='add_institutions'),
    url(r'^data/institutions/edit/$',       views.edit_institutions,    name='edit_institutions'),
    url(r'^data/institutions/confirm/$',    views.confirm_institutions, name='confirm_institutions'),

    url(r'^data/teams/$',                   views.add_teams,            name='add_teams'),
    url(r'^data/teams/edit/$',              views.edit_teams,           name='edit_teams'),
    url(r'^data/teams/confirm/$',           views.confirm_teams,        name='confirm_teams'),

    url(r'^data/adjudicators/$',            views.add_adjudicators,     name='add_adjudicators'),

    url(r'^data/venues/$',                  views.add_venues,           name='add_venues'),
    url(r'^data/venues/edit/$',             views.edit_venues,          name='edit_venues'),
    url(r'^data/venues/confirm$',           views.confirm_venues,       name='confirm_venues'),

]