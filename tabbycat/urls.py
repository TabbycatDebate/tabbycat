from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin, messages
from django.contrib.auth.views import logout as auth_logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
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

    # Favicon for old browsers that ignore the head link
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/favicon.ico')),

    # Redirect for old-style tournament URLs
    # Avoid keyword argument name 'tournament_slug' to avoid triggering DebateMiddleware
    url(r'^t/(?P<slug>[-\w_]+)/(?P<page>[-\w_/]*)$',
        tournaments.views.TournamentPermanentRedirectView.as_view()),

    # Tournament URLs
    url(r'^(?P<tournament_slug>[-\w_]+)/',
        include('tournaments.urls')),

    # Participants Cross Tournament
    url(r'^participants/',
        include('participants.urls_crosst')),

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

@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    if kwargs.get('user'):
        messages.success(request, 'Later, ' + kwargs['user'].username + ' — you were logged out!')
    else: # should never happen, but just in case
        messages.success(request, 'Later! You were logged out!')


@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    if kwargs.get('user'):
        messages.success(request, 'Hi, ' + kwargs['user'].username + ' — you just logged in!')
    else: # should never happen, but just in case
        messages.success(request, 'Welcome! You just logged in!')


# ==============================================================================
# Redirect Method
# ==============================================================================

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse

    def foo(request):
        return HttpResponseRedirect(reverse(view))

    return foo
