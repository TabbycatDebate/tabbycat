from django.urls import include, path

from . import views


urlpatterns = [

    path('t/<slug:tournament_slug>/', include([
        path('r/<int:round_seq>/', include([
        ])),

        path('breakcategory/', include([
            path('',
                views.BreakCategoryViewSet.as_view({'get': 'list', 'post': 'create'}),
                name='api-breakcategory-list'),
            path('<slug:slug>/', include([
                path('',
                    views.BreakCategoryViewSet.as_view({'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}),
                    name='api-breakcategory-detail'),
                path('eligibility/',
                    views.BreakEligibilityView.as_view(),
                    name='api-breakcategory-eligibility'),
            ])),
        ])),
        path('speakercategory/', include([
            path('',
                views.SpeakerCategoryViewSet.as_view({'get': 'list', 'post': 'create'}),
                name='api-speakercategory-list'),
            path('<slug:slug>/', include([
                path('',
                    views.SpeakerCategoryViewSet.as_view({'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}),
                    name='api-speakercategory-detail'),
                path('eligibility/',
                    views.SpeakerEligibilityView.as_view(),
                    name='api-speakercategory-eligibility'),
            ])),
        ])),
    ])),

]
