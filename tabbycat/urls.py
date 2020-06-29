from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.urls import include, path
from django.utils.translation import gettext as _
from django.views.i18n import JavaScriptCatalog

import tournaments.views
from importer.views import LoadDemoView

admin.autodiscover()

# ==============================================================================
# Base Patterns
# ==============================================================================

urlpatterns = [

    # Indices
    path('',
        tournaments.views.PublicSiteIndexView.as_view(),
        name='tabbycat-index'),
    path('start/',
        tournaments.views.BlankSiteStartView.as_view(),
        name='blank-site-start'),
    path('create/',
        tournaments.views.CreateTournamentView.as_view(),
        name='tournament-create'),
    path('load-demo/',
        LoadDemoView.as_view(),
        name='load-demo'),
    path('inactive/',
        tournaments.views.PublicSiteInactiveTournamentsView.as_view(),
        name='tabbycat-inactive-tournaments'),

    # Top Level Pages
    path('donations/',
        tournaments.views.DonationsView.as_view(),
        name='donations'),
    path('style/',
        tournaments.views.StyleGuideView.as_view(),
        name='style-guide'),

    # Set language override
    path('i18n/',
        include('django.conf.urls.i18n')),

    # JS Translations Catalogue; includes all djangojs files in locale folders
    path('jsi18n/',
         JavaScriptCatalog.as_view(domain="djangojs"),
         name='javascript-catalog'),

    # Summernote (WYSYWIG)
    path('summernote/',
        include('django_summernote.urls')),

    # Admin area
    path('jet/',
        include('jet.urls', 'jet')),
    path('database/',
        admin.site.urls),

    # Accounts
    path('accounts/', include([
        path('logout/',
            auth_views.LogoutView.as_view(),
            {'next_page': '/'},  # override to specify next_page
            name='logout'),
        path('',
            include('django.contrib.auth.urls')),
    ])),

    # Notifications
    path('notifications/',
        include('notifications.urls')),

    # API
    path('api',
        include('api.urls')),

    # Tournament URLs
    path('<slug:tournament_slug>/',
        include('tournaments.urls')),
]

if settings.DEBUG and settings.ENABLE_DEBUG_TOOLBAR:  # Only serve debug toolbar when on DEBUG
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))


# ==============================================================================
# Logout/Login Confirmations
# ==============================================================================

# These messages don't always work properly with unit tests, so set fail_silently=True

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    if kwargs.get('user'):
        messages.info(request,
            _("Hi, %(user)s — you just logged in!")  % {'user': kwargs['user'].username},
            fail_silently=True)
    else: # should never happen, but just in case
        messages.info(request, _("Welcome! You just logged in!"), fail_silently=True)


# ==============================================================================
# Redirect Method
# ==============================================================================

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.urls import reverse

    def foo(request):
        return HttpResponseRedirect(reverse(view))

    return foo
