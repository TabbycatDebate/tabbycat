from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def redirect(view):
    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse
    def foo(request):
        return HttpResponseRedirect(reverse(view))
    return foo

urlpatterns = patterns('',
    # Example:
    # (r'^debates/', include('debates.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', redirect('debate_index')),
    (r'^admin/', include(admin.site.urls)),
    (r'^debate/', include('debate.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # Site media
    (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL, 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
