from django.conf.urls import url

from . import views

urlpatterns = [
    # New Hotness
    url(r'^edit/$',
        views.EditAdjudicatorAllocationView.as_view(),
        name='edit-adj-allocation'),
    url(r'^create/$',
        views.CreateAutoAllocation.as_view(),
        name='adjudicators-auto-allocate'),
    url(r'^importance/set/$',
        views.SaveDebateImportance.as_view(),
        name='save-debate-importance'),
    url(r'^panel/set/$',
        views.SaveDebatePanel.as_view(),
        name='save-debate-panel'),
]
