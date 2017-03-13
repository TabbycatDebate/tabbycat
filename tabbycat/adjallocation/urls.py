from django.conf.urls import url

from . import views

urlpatterns = [
    # New Hotness
    url(r'^edit/$',
        views.EditAdjudicatorAllocationView.as_view(),
        name='edit_adj_allocation'),
    url(r'^create/$',
        views.CreateAutoAllocation.as_view(),
        name='create_auto_allocation'),
    url(r'^importance/set/$',
        views.SaveDebateImportance.as_view(),
        name='save_debate_importance'),
    url(r'^panel/set/$',
        views.SaveDebatePanel.as_view(),
        name='save_debate_panel'),
]
