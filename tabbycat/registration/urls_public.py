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
            path('view-response/',
                views.CoachViewResponseFormView.as_view(),
                name='reg-inst-view-response'),
            path('transfer-slots/',
                views.SlotTransferRequestFormView.as_view(),
                name='reg-inst-transfer-slots'),
            path('adjudicator/',
                views.InstitutionalCreateAdjudicatorFormView.as_view(),
                name='reg-inst-create-adj'),
            path('observer/',
                views.InstitutionalCreateObserverFormView.as_view(),
                name='reg-inst-create-observer'),
            path('team/',
                views.InstitutionalCreateTeamFormView.as_view(),
                name='reg-inst-create-team'),
        ])),
    ])),
    path('adjudicator/',
        views.PublicCreateAdjudicatorFormView.as_view(),
        name='reg-create-adjudicator'),
    path('observer/',
        views.PublicCreateObserverFormView.as_view(),
        name='reg-create-observer'),
    path('team/', include([
        path('',
            views.PublicCreateTeamFormView.as_view(),
            name='reg-create-team'),
        path('<int:pk>/speaker/',
            views.CreateSpeakerFormView.as_view(),
            name='reg-create-speaker'),
    ])),
]
