from django.urls import include, path

from . import views

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}

urlpatterns = [

    path('<slug:tournament_slug>/', include([
        path('<int:round_seq>/', include([
        ])),

        path('breakcategory/', include([
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
        path('speakercategory/', include([
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
    ])),

]
