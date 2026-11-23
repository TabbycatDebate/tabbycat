import uuid

from django.conf import settings
from django.db import models


class CSVImportRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expires_at = models.DateTimeField(db_index=True)
    state = models.JSONField()
