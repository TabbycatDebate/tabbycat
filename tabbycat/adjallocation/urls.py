from django.conf.urls import url

from . import views

urlpatterns = [
    # Old busted
    url(r'^create_old/$',
        views.create_adj_allocation,
        name='create_adj_allocation'),
    url(r'^edit_old/$',
        views.draw_adjudicators_edit,
        name='draw_adjudicators_edit'),
    url(r'^_get_old/$',
        views.draw_adjudicators_get,
        name='draw_adjudicators_get'),
    url(r'^save_old/$',
        views.SaveAdjudicatorsView.as_view(),
        name='save_adjudicators'),
    url(r'^_update_importance/$',
        views.update_debate_importance,
        name='update_debate_importance'),
    url(r'^conflicts_old/$',
        views.adj_conflicts,
        name='adj_conflicts'),
    # New Hotness
    url(r'^edit/$',
        views.EditAdjudicatorAllocationView.as_view(),
        name='edit_adj_allocation'),
    url(r'^importance/set/$',
        views.SetDebateImportance.as_view(),
        name='set_debate_importance'),

]
