from django.urls import include, path

from . import views


urlpatterns = [
    path('institution/', include([
        path('new/', views.CreateInstitutionFormView.as_view(),
            name='reg-create-institution'),
        path('<slug:url_key>/', include([
            path('',
                views.InstitutionalLandingPageView.as_view(),
                name='reg-inst-landing'),
            path('adjudicator/',
                views.InstitutionalCreateAdjudicatorFormView.as_view(),
                name='reg-inst-create-adj'),
            path('team/',
                views.InstitutionalCreateTeamFormView.as_view(),
                name='reg-inst-create-team'),
        ])),
    ])),
    path('adjudicator/',
        views.BaseCreateAdjudicatorFormView.as_view(),
        name='reg-create-adjudicator'),
    path('team/', include([
        path('',
            views.BaseCreateTeamFormView.as_view(),
            name='reg-create-team'),
        path('<int:pk>/speaker/',
            views.CreateSpeakerFormView.as_view(),
            name='reg-create-speaker'),
    ])),
]
