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
    url(r'^eligibility/$',
        views.EditEligibilityFormView.as_view(),
        name='breakqual-edit-eligibility'),
]
