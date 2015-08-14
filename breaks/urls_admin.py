from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^teams/(?P<category>\w+)/$',          views.breaking_teams,               name='breaking_teams'),
    url(r'^generate_all/(?P<category>\w+)/$',   views.generate_all_breaking_teams,  name='generate_breaking_teams'),
    url(r'^update_all/(?P<category>\w+)/$',     views.update_all_breaking_teams,    name='update_all_breaking_teams'),
    url(r'^update/(?P<category>\w+)/$',         views.update_breaking_teams,        name='update_breaking_teams'),
    url(r'^eligibility/$',                      views.break_eligibility,            name='break_eligibility'),
    url(r'^adjudicators/$',                     views.breaking_adjs,                name='breaking_adjs'),

]