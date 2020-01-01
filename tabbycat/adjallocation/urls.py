from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('debates/edit/',
            views.EditDebateAdjudicatorsView.as_view(),
            name='edit-debate-adjudicators'),
        path('panels/edit/',
            views.EditPanelAdjudicatorsView.as_view(),
            name='edit-panel-adjudicators'),
    ])),
    path('panels/edit/',
        views.PanelAdjudicatorsIndexView.as_view(),
        name='panel-adjudicators-index'),
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
