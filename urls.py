import django.contrib.auth.views as auth_views
import tournaments.views

from django.conf import settings
from django.conf.urls import *
from django.contrib import admin, messages
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver
from django.views.generic.base import RedirectView

admin.autodiscover()

# ==============================================================================
# Base Patterns
# ==============================================================================

urlpatterns = [

    # Indices
    url(r'^$',
        tournaments.views.index,
        name='tabbycat-index'),
    url(r'^t/(?P<tournament_slug>[-\w_]+)/',
        include('tournaments.urls')),
    url(r'^start/',
        tournaments.views.BlankSiteStartView.as_view(),
        name='blank-site-start'),
    url(r'^tournament/create/',
        tournaments.views.CreateTournamentView.as_view(),
        name='tournament-create'),

    # Admin area
    url(r'^jet/',
        include('jet.urls', 'jet')),
    url(r'^admin/',
        include(admin.site.urls)),

    # Accounts
    url(r'^accounts/login/$',
        auth_views.login,
        name='auth-login'),
    url(r'^accounts/logout/$',
        auth_views.logout,
        {'next_page': '/'}),

    # Favicon for old browsers that ignore the head link
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/favicon.ico'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        # Only serve debug toolbar when on DEBUG
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

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
