from django.conf.urls import url

from . import views

urlpatterns = [
    # Display
    url(r'^$',
        views.AdminBreakIndexView.as_view(),
        name='breakqual-index'),
    url(r'^teams/(?P<category>\w+)/$',
        views.BreakingTeamsFormView.as_view(),
        name='breakqual-teams'),
    url(r'^adjudicators/$',
        views.AdminBreakingAdjudicatorsView.as_view(),
        name='breakqual-adjudicators'),
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
        views.EditEligibilityFormView.as_view(),
        name='breakqual-edit-eligibility'),
]
