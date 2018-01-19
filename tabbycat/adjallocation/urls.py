from django.urls import include, path

from . import views

urlpatterns = [
    path('round/<int:round_seq>/', include([
        path('edit/',
            views.EditAdjudicatorAllocationView.as_view(),
            name='edit-adj-allocation'),
        path('create/',
            views.CreateAutoAllocation.as_view(),
            name='adjudicators-auto-allocate'),
        path('importance/set/',
            views.SaveDebateImportance.as_view(),
            name='save-debate-importance'),
        path('panel/set/',
            views.SaveDebatePanel.as_view(),
            name='save-debate-panel'),
    ])),
]
