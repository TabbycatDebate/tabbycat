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
    path('conflicts/adjudicator-team/',
        views.AdjudicatorTeamConflictsView.as_view(),
        name='adjallocation-conflicts-adj-team'),
]
