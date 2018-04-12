# Override all formats with British English, except as specified below
from django.conf.locale.en_GB.formats import *  # noqa: F403,F401

# Avoid months as numerals, to avoid ambiguity between British and American English
SHORT_DATE_FORMAT = 'j M Y'        # '8 Feb 2018'
SHORT_DATETIME_FORMAT = 'j M Y P'  # '8 Feb 2018 4:33 p.m.'

BADGE_DATETIME_FORMAT = 'j M H:i'  # '8 Feb 16:33'
