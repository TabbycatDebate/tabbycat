from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('edit/',
            views.EditAdjudicatorAllocationView.as_view(),
            name='adjallocation-round-edit'),
        path('create/',
            views.CreateAutoAllocation.as_view(),
            name='adjallocation-auto-allocate'),
        path('importance/set/',
            views.SaveDebateImportance.as_view(),
            name='adjallocation-save-debate-importance'),
        path('panel/set/',
            views.SaveDebatePanel.as_view(),
            name='adjallocation-save-debate-panel'),
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
