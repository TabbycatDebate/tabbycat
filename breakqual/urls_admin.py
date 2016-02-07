from django.conf.urls import url

from . import views

urlpatterns = [
    # Display
    url(r'^$',
        views.breaking_index,
        name='breaking_index'),
    url(r'^teams/(?P<category>\w+)/$',
        views.breaking_teams,
        name='breaking_teams'),
    url(r'^adjudicators/$',
        views.breaking_adjs,
        name='breaking_adjs'),
    # Create/Update
    url(r'^generate_all/(?P<category>\w+)/$',
        views.generate_all_breaking_teams,
        name='generate_breaking_teams'),
    url(r'^update_all/(?P<category>\w+)/$',
        views.update_all_breaking_teams,
        name='update_all_breaking_teams'),
    url(r'^update/(?P<category>\w+)/$',
        views.update_breaking_teams,
        name='update_breaking_teams'),
    url(r'^eligibility/$',
        views.edit_eligibility,
        name='edit_eligibility'),
]
