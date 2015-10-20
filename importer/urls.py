from django.conf.urls import *
from django.core.urlresolvers import reverse

from . import views

urlpatterns = [

    url(r'^data/$',                 views.data_index,           name='data_index'),
    url(r'^data/institutions/$',    views.add_institutions,     name='add_institutions'),
    url(r'^data/teams/$',           views.add_teams,            name='add_teams'),
    url(r'^data/adjudicators/$',    views.add_adjudicators,     name='add_adjudicators'),

]