from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework.routers import SimpleRouter

from . import views

pref_router = SimpleRouter(trailing_slash=False)
pref_router.register('preferences', views.TournamentPreferenceViewSet)

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'post': 'update', 'patch': 'partial_update', 'delete': 'destroy'}

urlpatterns = [

    path('',
        views.APIRootView.as_view(),
        name='api-root'),

    path('/schema', include([
        path('.yml', SpectacularAPIView.as_view(), name='api-schema'),
        path('/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc'),
    ])),

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

                path('/full', views.FullTournamentViewSet.as_view({'get': 'retrieve'}),
                    name='api-tournament-full'),

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

                path('/score-criteria', include([
                    path('',
                        views.ScoreCriterionViewSet.as_view(list_methods),
                        name='api-score-criteria-list'),
                    path('/<int:pk>',
                        views.ScoreCriterionViewSet.as_view(detail_methods),
                        name='api-score-criteria-detail'),
                ])),

                path('/rounds', include([
                    path('',
                        views.RoundViewSet.as_view(list_methods),
                        name='api-round-list'),

                    path('/<int:round_seq>', include([
                        path('',
                            views.RoundViewSet.as_view(detail_methods),
                            name='api-round-detail'),

                        path('/availabilities',
                            views.AvailabilitiesViewSet.as_view(),
                            name='api-availability-list'),

                        path('/pairings', include([
                            path('',
                                views.PairingViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'delete_all'}),
                                name='api-pairing-list'),
                            path('/generate-draw',
                                views.GeneratePairingView.as_view(),
                                name='api-generate-pairing'),
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

                        path('/preformed-panels', include([
                            path('',
                                views.PreformedPanelViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'delete_all', 'put': 'add_blank'}),
                                name='api-preformedpanel-list'),
                            path('/<int:debate_pk>',
                                views.PreformedPanelViewSet.as_view(detail_methods),
                                name='api-preformedpanel-detail'),
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
                    path('/standings', include([
                        path('',
                            views.TeamStandingsView.as_view(),
                             name='api-team-standings'),
                        path('/rounds',
                            views.TeamRoundStandingsRoundsView.as_view({'get': 'list'}),
                            name='api-team-round-standings'),
                    ])),
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
                        path('/rounds',
                            views.SpeakerRoundStandingsRoundsView.as_view({'get': 'list'}),
                            name='api-speaker-round-standings'),
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

                path('/user-groups', include([
                    path('',
                        views.GroupViewSet.as_view(list_methods),
                        name='api-group-list'),
                    path('/<int:pk>',
                        views.GroupViewSet.as_view(detail_methods),
                        name='api-group-detail'),
                ])),

                path('/me',
                    views.ParticipantIdentificationView.as_view({'get': 'retrieve'}),
                    name='api-tournament-detail'),

                path('/', include(pref_router.urls)),  # Preferences
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

        path('/users', include([
            path('',
                views.UserViewSet.as_view(list_methods),
                name='api-user-list'),
            path('/<int:pk>',
                views.UserViewSet.as_view(detail_methods),
                name='api-user-detail'),
        ])),
    ])),
]
