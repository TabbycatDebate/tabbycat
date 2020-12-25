from django.urls import path

from . import views

urlpatterns = [

    # Display
    path('display/',
        views.AssistantDrawDisplayView.as_view(),
        name='draw-assistant-display'),
    path('round/current/display-by-venue/',
        views.AssistantDrawDisplayForCurrentRoundsByVenueView.as_view(),
        name='draw-assistant-display-current-rounds-by-venue'),
    path('round/current/display-by-team/',
        views.AssistantDrawDisplayForCurrentRoundsByTeamView.as_view(),
        name='draw-assistant-display-current-rounds-by-team'),
    path('round/<int:round_seq>/display-by-venue/',
        views.AssistantDrawDisplayForSpecificRoundByVenueView.as_view(),
        name='draw-assistant-display-specific-round-by-venue'),
    path('round/<int:round_seq>/display-by-team/',
        views.AssistantDrawDisplayForSpecificRoundByTeamView.as_view(),
        name='draw-assistant-display-specific-round-by-team'),
]
