from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin, messages
from django.contrib.auth.views import logout as auth_logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.views.generic.base import RedirectView

import tournaments.views

admin.autodiscover()

# ==============================================================================
# Base Patterns
# ==============================================================================

urlpatterns = [

    # Indices
    url(r'^$',
        tournaments.views.PublicSiteIndexView.as_view(),
        name='tabbycat-index'),
    url(r'^start/',
        tournaments.views.BlankSiteStartView.as_view(),
        name='blank-site-start'),
    url(r'^create/',
        tournaments.views.CreateTournamentView.as_view(),
        name='tournament-create'),
    url(r'^load_demo/',
        tournaments.views.LoadDemoView.as_view(),
        name='load-demo'),

    # Top Level Pages
    url(r'^donations/',
        tournaments.views.DonationsView.as_view(),
        name='donations'),
    url(r'^fix_debate_teams/(?P<debate_id>\d+)/$',
        tournaments.views.FixDebateTeamsView.as_view(),
        name='fix-debate-teams'),
    url(r'^style/$',
        tournaments.views.StyleGuideView.as_view(),
        name='style-guide'),

    # Admin area
    url(r'^jet/',
        include('jet.urls', 'jet')),
    url(r'^database/',
        include(admin.site.urls)),
    url(r'^admin/(?P<page>[-\w_/]*)$',
        RedirectView.as_view(url='/database/%(page)s', permanent=True)),

    # Accounts
    url(r'^accounts/logout/$',
        auth_logout,
        {'next_page': '/'},  # override to specify next_page
        name='logout'),
    url(r'^accounts/',
        include('django.contrib.auth.urls')),

    # Redirect for old-style tournament URLs
    # Avoid keyword argument name 'tournament_slug' to avoid triggering DebateMiddleware
    url(r'^t/(?P<slug>[-\w_]+)/(?P<page>[-\w_/]*)$',
        tournaments.views.TournamentPermanentRedirectView.as_view()),

    # Tournament URLs
    url(r'^(?P<tournament_slug>[-\w_]+)/',
        include('tournaments.urls')),

    # Draws Cross Tournament
    url(r'^draw/',
        include('draw.urls_crosst'))
]

if settings.DEBUG:  # Only serve debug toolbar when on DEBUG
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))


# ==============================================================================
# Logout/Login Confirmations
# ==============================================================================

# These messages don't always work properly with unit tests, so set fail_silently=True

@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    if kwargs.get('user'):
        messages.info(request,
            _("Later, %(username)s — you were logged out!") % {'username': kwargs['user'].username},
            fail_silently=True)
    else: # should never happen, but just in case
        messages.info(request, _("Later! You were logged out!"), fail_silently=True)


@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    if kwargs.get('user'):
        messages.info(request,
            _("Hi, %(username)s — you just logged in!")  % {'username': kwargs['user'].username},
            fail_silently=True)
    else: # should never happen, but just in case
        messages.info(request, _("Welcome! You just logged in!"), fail_silently=True)


# ==============================================================================
# Redirect Method
# ==============================================================================

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse

    def foo(request):
        return HttpResponseRedirect(reverse(view))

    return foo
