from django.urls import include, path

from . import views

urlpatterns = [

    path('round/<int:round_seq>/', include([
        # Display
        path('display/',
            views.AssistantDrawDisplayView.as_view(),
            name='draw-assistant-display'),
        path('display-by-venue/',
            views.AssistantDrawDisplayForRoundByVenueView.as_view(),
            name='draw-assistant-display-by-venue'),
        path('display-by-team/',
            views.AssistantDrawDisplayForRoundByTeamView.as_view(),
            name='draw-assistant-display-by-team'),
    ])),

]
