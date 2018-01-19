from django.urls import path

from . import views

urlpatterns = [
    path('list/',
        views.ParticipantsListView.as_view(),
        name='participants-list'),
    path('eligibility/',
        views.EditSpeakerCategoryEligibilityView.as_view(),
        name='participants-speaker-eligibility'),
    path('eligibility/update/',
        views.UpdateEligibilityEditView.as_view(),
        name='participants-speaker-update-eligibility'),
    path('categories/',
        views.EditSpeakerCategoriesView.as_view(),
        name='participants-speaker-categories-edit'),
    path('team/<int:pk>/',
        views.TeamRecordView.as_view(),
        name='participants-team-record'),
    path('adjudicator/<int:pk>/',
        views.AdjudicatorRecordView.as_view(),
        name='participants-adjudicator-record'),
]
