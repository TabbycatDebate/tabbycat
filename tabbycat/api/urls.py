from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

pref_router = SimpleRouter(trailing_slash=False)
pref_router.register('preferences', views.TournamentPreferenceViewSet)

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}

urlpatterns = [

    path('',
        views.APIRootView.as_view(),
        name='api-root'),

    path('/v1', include([
        path('',
            views.APIV1RootView.as_view(),
            name='api-v1-root'),

        path('/tournaments', include([

            path('',
                views.TournamentViewSet.as_view(list_methods),
                name='api-tournament-list'),

            path('/<slug:tournament_slug>', include([

                path('',
                    views.TournamentViewSet.as_view(detail_methods),
                    name='api-tournament-detail'),

                path('/motions', include([
                    path('',
                        views.MotionViewSet.as_view(list_methods),
                        name='api-motion-list'),
                    path('/<int:pk>',
                        views.MotionViewSet.as_view(detail_methods),
                        name='api-motion-detail'),
                ])),

                path('/feedback-questions', include([
                    path('',
                        views.FeedbackQuestionViewSet.as_view(list_methods),
                        name='api-feedbackquestion-list'),
                    path('/<int:pk>',
                        views.FeedbackQuestionViewSet.as_view(detail_methods),
                        name='api-feedbackquestion-detail'),
                ])),

                path('/feedback', include([
                    path('',
                        views.FeedbackViewSet.as_view(list_methods),
                        name='api-feedback-list'),
                    path('/<int:pk>',
                        views.FeedbackViewSet.as_view(detail_methods),
                        name='api-feedback-detail'),
                ])),

                path('/rounds', include([
                    path('',
                        views.RoundViewSet.as_view(list_methods),
                        name='api-round-list'),

                    path('/<int:round_seq>', include([
                        path('',
                            views.RoundViewSet.as_view(detail_methods),
                            name='api-round-detail'),

                        path('/pairings', include([
                            path('',
                                views.PairingViewSet.as_view(list_methods),
                                name='api-pairing-list'),
                            path('/<int:debate_pk>', include([
                                path('',
                                    views.PairingViewSet.as_view(detail_methods),
                                    name='api-pairing-detail'),

                                path('/ballots', include([
                                    path('',
                                        views.BallotViewSet.as_view(list_methods),
                                        name='api-ballot-list'),
                                    path('/<int:pk>',
                                        views.BallotViewSet.as_view(detail_methods),
                                        name='api-ballot-detail'),
                                ])),
                            ])),
                        ])),
                    ])),
                ])),

                path('/break-categories', include([

                    path('',
                        views.BreakCategoryViewSet.as_view(list_methods),
                        name='api-breakcategory-list'),

                    path('/<int:pk>', include([
                        path('',
                            views.BreakCategoryViewSet.as_view(detail_methods),
                            name='api-breakcategory-detail'),
                        path('/eligibility',
                            views.BreakEligibilityView.as_view(),
                            name='api-breakcategory-eligibility'),
                        path('/break',
                            views.BreakingTeamsView.as_view(
                                {'get': 'list', 'post': 'create', 'delete': 'destroy', 'patch': 'update'},
                            ),
                            name='api-breakcategory-break'),
                    ])),
                ])),

                path('/speaker-categories', include([

                    path('',
                        views.SpeakerCategoryViewSet.as_view(list_methods),
                        name='api-speakercategory-list'),

                    path('/<int:pk>', include([
                        path('',
                            views.SpeakerCategoryViewSet.as_view(detail_methods),
                            name='api-speakercategory-detail'),
                        path('/eligibility',
                            views.SpeakerEligibilityView.as_view(),
                            name='api-speakercategory-eligibility'),
                    ])),
                ])),

                path('/institutions',
                    views.InstitutionViewSet.as_view({'get': 'list'}),
                    name='api-institution-list'),
                path('/teams', include([
                    path('',
                         views.TeamViewSet.as_view(list_methods),
                         name='api-team-list'),
                    path('/<int:pk>',
                         views.TeamViewSet.as_view(detail_methods),
                         name='api-team-detail'),
                    path('/standings',
                         views.TeamStandingsView.as_view(),
                         name='api-team-standings'),
                ])),
                path('/adjudicators', include([
                    path('',
                        views.AdjudicatorViewSet.as_view(list_methods),
                        name='api-adjudicator-list'),
                    path('/<int:pk>', include([
                        path('',
                            views.AdjudicatorViewSet.as_view(detail_methods),
                            name='api-adjudicator-detail'),
                        path('/checkin',
                            views.AdjudicatorCheckinsView.as_view(),
                            name='api-adjudicator-checkin'),
                    ])),
                ])),
                path('/speakers', include([
                    path('',
                         views.SpeakerViewSet.as_view(list_methods),
                         name='api-speaker-list'),
                    path('/<int:pk>', include([
                        path('',
                            views.SpeakerViewSet.as_view(detail_methods),
                            name='api-speaker-detail'),
                        path('/checkin',
                            views.SpeakerCheckinsView.as_view(),
                            name='api-speaker-checkin'),
                    ])),
                    path('/standings', include([
                        path('',
                            views.SubstantiveSpeakerStandingsView.as_view(),
                            name='api-substantive-speaker-standings'),
                        path('/replies',
                            views.ReplySpeakerStandingsView.as_view(),
                            name='api-reply-speaker-standings'),
                    ])),
                ])),
                path('/venues', include([
                    path('',
                        views.VenueViewSet.as_view(list_methods),
                        name='api-venue-list'),
                    path('/<int:pk>', include([
                        path('',
                            views.VenueViewSet.as_view(detail_methods),
                            name='api-venue-detail'),
                        path('/checkin',
                            views.VenueCheckinsView.as_view(),
                            name='api-venue-checkin'),
                    ])),
                ])),
                path('/venue-categories', include([
                    path('',
                        views.VenueCategoryViewSet.as_view(list_methods),
                        name='api-venuecategory-list'),
                    path('/<int:pk>',
                        views.VenueCategoryViewSet.as_view(detail_methods),
                        name='api-venuecategory-detail'),
                ])),

                url('/', include(pref_router.urls)),  # Preferences
            ])),


        ])),
        path('/institutions', include([
            path('',
                 views.GlobalInstitutionViewSet.as_view(list_methods),
                 name='api-global-institution-list'),
            path('/<int:pk>',
                 views.GlobalInstitutionViewSet.as_view(detail_methods),
                 name='api-global-institution-detail'),
        ])),
    ])),
]
