# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.db import migrations

logger = logging.getLogger(__name__)


def convert_content_objects(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ActionLogEntry = apps.get_model("actionlog", "ActionLogEntry")

    for action in ActionLogEntry.objects.all():
        done = False
        for field in ('debate', 'ballot_submission', 'adjudicator_feedback',
                      'round', 'motion', 'adjudicator_test_score_history',
                      'break_category', 'adjudicator'):
            value = getattr(action, field)
            if value is not None:
                if done:
                    logger.warning("Two optional fields on %s", action)
                action.content_type = ContentType.objects.get_for_model(value.__class__)
                action.object_id = value.id
                action.save()
                done = True


class Migration(migrations.Migration):

    dependencies = [
        ('actionlog', '0012_add_content_object'),
    ]

    operations = [
        migrations.RunPython(convert_content_objects, reverse_code=migrations.RunPython.noop),
    ]
