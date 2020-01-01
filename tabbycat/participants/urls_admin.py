from django.urls import path

from . import views

urlpatterns = [
    path('list/',
        views.AdminParticipantsListView.as_view(),
        name='participants-list'),
    path('institutions/',
        views.AdminInstitutionsListView.as_view(),
        name='participants-institutions-list'),
    path('code-names/',
        views.AdminCodeNamesListView.as_view(),
        name='participants-code-names-list'),

    path('email/',
        views.EmailTeamRegistrationView.as_view(),
        name='participants-email'),

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
