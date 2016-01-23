from django.conf.urls import *
from django.conf import settings
from django.contrib import admin

from django.contrib.auth import views
from django.views.static import serve
from tournaments.views import index

admin.autodiscover()

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse
    def foo(request):
        return HttpResponseRedirect(reverse(view))
    return foo

urlpatterns = [

    url(r'^$',                                  index),

    url(r'^t/(?P<tournament_slug>[-\w_]+)/',    include('tournaments.urls')),

    url(r'^admin/',                             include(admin.site.urls)),

    url(r'^accounts/login/$',                   views.login),

    url(r'^accounts/logout/$',                  views.logout,
        {'next_page': '/'}),

    url(r'^static/(?P<path>.*)$',               serve,
        {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/',                     include(debug_toolbar.urls)),
    ]


# LOGOUT AND LOGIN Confirmations
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver
from django.contrib import messages
@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.add_message(request, messages.SUCCESS, 'Later ' + kwargs['user'].username +  ' — you were logged out!')

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    messages.add_message(request, messages.SUCCESS, 'Hi ' + kwargs['user'].username +  ' — you just logged in!')

