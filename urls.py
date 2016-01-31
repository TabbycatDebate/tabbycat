from django.conf.urls import *
from django.conf import settings
from django.contrib import admin

import django.contrib.auth.views as auth_views
import tournaments.views
from django.views.static import serve

admin.autodiscover()

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse
    def foo(request):
        return HttpResponseRedirect(reverse(view))
    return foo

urlpatterns = [

    # Indices
    url(r'^$',                                  tournaments.views.index,      name='tabbycat-index'),
    url(r'^t/(?P<tournament_slug>[-\w_]+)/',    include('tournaments.urls')),
    url(r'^start/',                             tournaments.views.BlankSiteStartView.as_view(), name='blank-site-start'),

    # Admin area
    url(r'^jet/',                               include('jet.urls', 'jet')),
    url(r'^admin/',                             include(admin.site.urls)),

    # Accounts
    url(r'^accounts/login/$',                   auth_views.login,             name='auth-login'),
    url(r'^accounts/logout/$',                  auth_views.logout,
        {'next_page': '/'}),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        # Only serve debug toolbar when on DEBUG
        url(r'^__debug__/',                     include(debug_toolbar.urls)),
    ]
if hasattr(settings, "LOCAL_SETTINGS") and settings.DEBUG is False:
        urlpatterns += [
            url(r'^static/(?P<path>.*)$',           serve,
            {'document_root': settings.STATIC_ROOT}),
        ]


# LOGOUT AND LOGIN Confirmations
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver
from django.contrib import messages
@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.success(request, 'Later, ' + kwargs['user'].username +  ' — you were logged out!')

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    messages.success(request, 'Hi, ' + kwargs['user'].username +  ' — you just logged in!')

