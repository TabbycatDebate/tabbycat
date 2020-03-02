from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

pref_router = SimpleRouter()
pref_router.register('preferences', views.TournamentPreferenceViewSet)

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}

urlpatterns = [

    path('',
        views.APIRootView.as_view(),
        name='api-root'),

    path('tournaments/', include([

        path('',
            views.TournamentViewSet.as_view(list_methods),
            name='api-tournament-list'),

        path('<slug:tournament_slug>/', include([

            path('',
                views.TournamentViewSet.as_view(detail_methods),
                name='api-tournament-detail'),

            path('rounds/', include([
                path('<int:round_seq>/', include([
                ])),
            ])),

            path('break-categories/', include([

                path('',
                    views.BreakCategoryViewSet.as_view(list_methods),
                    name='api-breakcategory-list'),

                path('<int:pk>/', include([
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

                path('<int:pk>/', include([
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
                path('<int:pk>/',
                     views.InstitutionViewSet.as_view(detail_methods),
                     name='api-institution-detail'),
            ])),
            path('teams/', include([
                path('',
                     views.TeamViewSet.as_view(list_methods),
                     name='api-team-list'),
                path('<int:pk>/',
                     views.TeamViewSet.as_view(detail_methods),
                     name='api-team-detail'),
            ])),
            path('adjudicators/', include([
                path('',
                     views.AdjudicatorViewSet.as_view(list_methods),
                     name='api-adjudicator-list'),
                path('<int:pk>/',
                     views.AdjudicatorViewSet.as_view(detail_methods),
                     name='api-adjudicator-detail'),
            ])),
            path('speakers/', include([
                path('',
                     views.SpeakerViewSet.as_view(list_methods),
                     name='api-speaker-list'),
                path('<int:pk>/',
                     views.SpeakerViewSet.as_view(detail_methods),
                     name='api-speaker-detail'),
            ])),

            url('', include(pref_router.urls)),  # Preferences
        ])),


    ])),
    path('institutions/', include([
        path('',
             views.GlobalInstitutionViewSet.as_view(list_methods),
             name='api-global-institution-list'),
        path('<int:pk>/',
             views.GlobalInstitutionViewSet.as_view(detail_methods),
             name='api-global-institution-detail'),
    ])),
]
