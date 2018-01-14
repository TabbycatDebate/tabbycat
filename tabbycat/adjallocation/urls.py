from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^round/(?P<round_seq>\d+)/', include([
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
    ])),
]
