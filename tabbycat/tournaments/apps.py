from django.apps import AppConfig


class TournamentsConfig(AppConfig):
    name = 'tournaments'

    def ready(self):
        from . import signals  # noqa: F401
