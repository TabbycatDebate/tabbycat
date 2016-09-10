from django.apps import AppConfig


class ParticipantsConfig(AppConfig):
    name = 'participants'

    def ready(self):
        from . import signals  # noqa: F401
