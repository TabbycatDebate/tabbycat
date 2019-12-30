from django.urls import include, path

from . import views

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}

urlpatterns = [

    path('',
        views.APIRootView.as_view(),
        name='api-root'),

    path('create/',
        views.TournamentCreateView.as_view(),
        name='api-tournament-create'),

    path('<slug:tournament_slug>/', include([
        path('',
            views.TournamentDetailView.as_view(),
            name='api-tournament-detail'),

        path('<int:round_seq>/', include([
        ])),

        path('break-categories/', include([
            path('',
                views.BreakCategoryViewSet.as_view(list_methods),
                name='api-breakcategory-list'),
            path('<slug:slug>/', include([
                path('',
                    views.BreakCategoryViewSet.as_view(detail_methods),
                    name='api-breakcategory-detail'),
                path('eligibility/',
                    views.BreakEligibilityView.as_view(),
                    name='api-breakcategory-eligibility'),
            ])),
        ])),
        path('speaker-categories/', include([
            path('',
                views.SpeakerCategoryViewSet.as_view(list_methods),
                name='api-speakercategory-list'),
            path('<slug:slug>/', include([
                path('',
                    views.SpeakerCategoryViewSet.as_view(detail_methods),
                    name='api-speakercategory-detail'),
                path('eligibility/',
                    views.SpeakerEligibilityView.as_view(),
                    name='api-speakercategory-eligibility'),
            ])),
        ])),
        path('institutions/', include([
            path('',
                 views.InstitutionViewSet.as_view(list_methods),
                 name='api-institution-list'),
            path('create/',
                 views.InstitutionViewSetCreateView.as_view(),
                 name='api-institution-create'),
        ])),
    ])),

]
