from django.conf.urls import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse
    def foo(request):
        return HttpResponseRedirect(reverse(view))
    return foo

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'debate.views.index'),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),

    (r'^t/(?P<tournament_slug>[-\w_]+)/', include('debate.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )