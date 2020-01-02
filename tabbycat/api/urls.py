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

            url('', include(pref_router.urls)),  # Preferences
        ])),
    ])),

]
