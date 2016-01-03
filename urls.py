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

    url(r'^admin/',                             include(admin.site.urls)),
    url(r'^accounts/login/$',                   views.login),
    url(r'^accounts/logout/$',                  views.logout, name='logout'),
    url(r'^$',                                  index),
    url(r'^t/(?P<tournament_slug>[-\w_]+)/',    include('tournaments.urls')),
    url(r'^static/(?P<path>.*)$',               serve, {'document_root': settings.STATIC_ROOT}),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/',                     include(debug_toolbar.urls)),
    ]