from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('debtates/edit/',
            views.EditDebateAdjudicatorsView.as_view(),
            name='edit-debate-adjudicators'),
        path('edit-legacy/',
            views.LegacyEditAdjudicatorAllocationView.as_view(),
            name='legacy-adjallocation-round-edit'),
        path('create/',
            views.LegacyCreateAutoAllocation.as_view(),
            name='legacy-adjallocation-auto-allocate'),
        path('importance/set/',
            views.LegacySaveDebateImportance.as_view(),
            name='legacy-adjallocation-save-debate-importance'),
        path('panel/set/',
            views.LegacySaveDebatePanel.as_view(),
            name='legacy-adjallocation-save-debate-panel'),
        path('panels/edit',
            views.EditPanelAdjudicatorsView.as_view(),
            name='edit-panel-adjudicators'),
    ])),
    path('conflicts/', include([
        path('adjudicator-team/',
            views.AdjudicatorTeamConflictsView.as_view(),
            name='adjallocation-conflicts-adj-team'),
        path('adjudicator-adjudicator/',
            views.AdjudicatorAdjudicatorConflictsView.as_view(),
            name='adjallocation-conflicts-adj-adj'),
        path('adjudicator-institution/',
            views.AdjudicatorInstitutionConflictsView.as_view(),
            name='adjallocation-conflicts-adj-inst'),
        path('team-institution/',
            views.TeamInstitutionConflictsView.as_view(),
            name='adjallocation-conflicts-team-inst'),
    ])),
]
