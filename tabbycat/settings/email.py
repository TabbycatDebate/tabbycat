from os import environ

# ==============================================================================
# Email
# ==============================================================================

# Settings for django-anymail, which sends through an email provider's HTTP API.
# Every ANYMAIL_* environment variable is passed on with the prefix removed,
# e.g. ANYMAIL_BREVO_API_KEY becomes ANYMAIL['BREVO_API_KEY'], and
# ANYMAIL_WEBHOOK_SECRET secures the tracking webhooks.
ANYMAIL = {key[len('ANYMAIL_'):]: value for key, value in environ.items()
           if key.startswith('ANYMAIL_') and value}

if environ.get('EMAIL_PROVIDER', ''):
    # Any provider supported by django-anymail, e.g. "brevo", "amazon_ses", "mailjet"
    EMAIL_PROVIDER = environ['EMAIL_PROVIDER'].strip().lower().replace('-', '_')
    EMAIL_BACKEND = 'anymail.backends.%s.EmailBackend' % EMAIL_PROVIDER
    SERVER_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'root@localhost')
    DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'notconfigured@tabbycatsite')

elif environ.get('EMAIL_HOST', ''):
    SERVER_EMAIL = environ['DEFAULT_FROM_EMAIL']
    DEFAULT_FROM_EMAIL = environ['DEFAULT_FROM_EMAIL']
    EMAIL_HOST = environ['EMAIL_HOST']
    EMAIL_HOST_USER = environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = int(environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'

elif environ.get('SENDGRID_API_KEY', ''):
    SERVER_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'root@localhost')
    DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'notconfigured@tabbycatsite')
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = environ['SENDGRID_API_KEY']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

elif environ.get('SENDGRID_USERNAME', ''):
    # These settings are deprecated as of Tabbycat 2.6.0 (Ocicat).
    # When removing, also remove utils.mixins.WarnAboutLegacySendgridConfigVarsMixin and
    # templates/errors/legacy_sendgrid_warning.html (and references thereto).
    USING_LEGACY_SENDGRID_CONFIG_VARS = True
    SERVER_EMAIL = environ['SENDGRID_USERNAME']
    DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL', environ['SENDGRID_USERNAME'])
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
