from django.conf.urls import *
from django.core.urlresolvers import reverse

from . import views

urlpatterns = [

    url(r'^$',                                  views.public_index,     name='public_index'),

    url(r'^admin/$',                            views.tournament_home,  name='tournament_home'),

    #url(r'^admin/actions/$', 'action_log', name='action_log'),

    # TODO: 'core' app functionality?
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment_check/$', views.round_increment_check,     name='round_increment_check'),
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment/$',       views.round_increment,   name='round_increment'),
    url(r'^divisions/$',                                            views.public_divisions,  name='public_divisions'),
    url(r'^admin/division_allocations/$',                           views.division_allocations,  name='division_allocations'),
    url(r'^admin/division_allocations/save/$',                      views.save_divisions,    name='save_divisions'),
    url(r'^admin/division_allocations/create/$',                    views.create_division_allocation,    name='create_division_allocation'),

    # TODO: unclear if these fit in feedback or not given they also work for ballots
    url(r'^admin/randomised_urls/$',                                                views.randomised_urls, name='randomised_urls'),
    url(r'^admin/randomised_urls/generate/$',                                       views.generate_randomised_urls, name='generate_randomised_urls'),

    # WADL-specific; unclear if draws or participants
    url(r'^all_tournaments_all_venues/$',                                           views.all_tournaments_all_venues, name='all_tournaments_all_venues'),
    url(r'^all_tournaments_all_venues/all_draws/(?P<venue_id>\d+)$',                views.all_draws_for_venue, name='all_draws_for_venue'),
    url(r'^all_tournaments_all_institutions/all_draws/(?P<institution_id>\d+)$',    views.all_draws_for_institution, name='all_draws_for_institution'),

    # Allocations App
    url(r'^admin/allocations/round/(?P<round_seq>\d+)/',    include('allocations.urls')),

    # Printing App
    url(r'^admin/print/round/(?P<round_seq>\d+)/',          include('printing.urls')),

    # Standings App
    url(r'^standings/',                                     include('standings.urls_public')),
    url(r'^tab/',                                           include('standings.urls_public')),
    url(r'^admin/standings/round/(?P<round_seq>\d+)/',      include('standings.urls_admin')),

    # Break App
    url(r'^break/',                                         include('breaking.urls_public')),
    url(r'^admin/break/',                                   include('breaking.urls_admin')),

    # Availability App
    url(r'^admin/availability/round/(?P<round_seq>\d+)/',   include('availability.urls')),

    # Motions App
    url(r'^motions/',                                       include('motions.urls_public')),
    url(r'^admin/motions/round/(?P<round_seq>\d+)/',        include('motions.urls_admin')),

    # Action Log App
    url(r'^admin/action_log/',                              include('action_log.urls')),

    # Config App
    url(r'^admin/options/',                                 include('options.urls')),

    # Feedback App
    url(r'^feedback/',                                      include('feedback.urls_public')),
    url(r'^admin/feedback/',                                include('feedback.urls_admin')),

    # Results App
    url(r'^results/',                                       include('results.urls_public')),
    url(r'^admin/results/',                                 include('results.urls_admin')),

    # Draws App
    url(r'^draw/',                                          include('draws.urls_public')),
    url(r'^admin/draw/',                                    include('draws.urls_admin')),

    # Participants App
    url(r'^participants/',                                  include('participants.urls_public')),

]