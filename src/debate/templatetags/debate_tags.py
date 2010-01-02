from django import template
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.conf import settings

import re
import os

register = template.Library()

STATIC_PATH = settings.MEDIA_ROOT
version_cache = {}

rx = re.compile(r'^(.*)\.(.*?)$')
def version(path_string, base_url=settings.MEDIA_URL):
    
    if not hasattr(settings, 'ENABLE_MEDIA_VERSIONING') or not settings.ENABLE_MEDIA_VERSIONING:
        return base_url + path_string

    try:
        if path_string in version_cache:
            mtime = version_cache[path_string]
        else:
            mtime = os.path.getmtime(os.path.join(settings.MEDIA_ROOT, path_string))
            version_cache[path_string] = mtime

        return base_url + rx.sub(r'\1.%d.\2' % mtime, path_string)
    except:
        return base_url + path_string 
register.simple_tag(version) 

def aff_count(team, round):
    return team.get_aff_count(round.seq)
register.simple_tag(aff_count)

def neg_count(team, round):
    return team.get_neg_count(round.seq)
register.simple_tag(neg_count)

