from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^create/$',               views.create_adj_allocation,        name='create_adj_allocation'),
    url(r'^edit/$',                 views.draw_adjudicators_edit,       name='draw_adjudicators_edit'),
    url(r'^_get/$',                 views.draw_adjudicators_get,        name='draw_adjudicators_get'),
    url(r'^save/$',                 views.save_adjudicators,            name='save_adjudicators'),
    url(r'^_update_importance/$',   views.update_debate_importance,     name='update_debate_importance'),
    url(r'^conflicts/$',            views.adj_conflicts,                name='adj_conflicts'),

]