from django.urls import path

from . import views

urlpatterns = [
    # Display
    path('',
        views.AdminBreakIndexView.as_view(),
        name='breakqual-index'),
    path('teams/<slug:category>/',
        views.BreakingTeamsFormView.as_view(),
        name='breakqual-teams'),
    path('adjudicators/',
        views.AdminBreakingAdjudicatorsView.as_view(),
        name='breakqual-adjudicators'),
    # Create/Update
    path('generate_all/<slug:category>/',
        views.GenerateAllBreaksView.as_view(),
        name='breakqual-generate-all'),
    path('eligibility/',
        views.EditTeamEligibilityView.as_view(),
        name='breakqual-edit-eligibility'),
    path('eligibility/update',
        views.UpdateEligibilityEditView.as_view(),
        name='breakqual-update-eligibility'),
    path('categories/',
        views.EditBreakCategoriesView.as_view(),
        name='break-categories-edit'),
]
