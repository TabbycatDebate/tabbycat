from django.conf.urls import url

from . import views

urlpatterns = [
    # Display
    url(r'^$',
        views.breaking_index,
        name='breaking_index'),
    url(r'^teams/(?P<category>\w+)/$',
        views.breaking_teams,
        name='breakqual-teams'),
    url(r'^adjudicators/$',
        views.AdminBreakingAdjudicators.as_view(),
        name='breaking_adjs'),
    # Create/Update
    url(r'^generate_all/(?P<category>\w+)/$',
        views.GenerateAllBreaksView.as_view(),
        name='breakqual-generate-all'),
    url(r'^update_all/(?P<category>\w+)/$',
        views.UpdateAllBreaksView.as_view(),
        name='breakqual-update-all'),
    url(r'^update/(?P<category>\w+)/$',
        views.UpdateBreakView.as_view(),
        name='breakqual-update-one'),
    url(r'^eligibility/$',
        views.edit_eligibility,
        name='edit_eligibility'),
]
