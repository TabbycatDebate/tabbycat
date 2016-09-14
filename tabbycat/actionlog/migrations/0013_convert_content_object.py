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
                action.content_type = ContentType.objects.get_for_model(value)
                action.object_id = value.id
                action.save()
                done = True


class Migration(migrations.Migration):

    dependencies = [
        ('actionlog', '0012_add_content_object'),

        # We require all models to be up to date with fields, since their
        # objects are retrieved in the getattr(action, field) call. (It's
        # possible to write the migration without this, but we'd have specify
        # the model of every field specifically.)
        ('draw', '0009_auto_20160621_1129'),  # Debate
        ('results', '0001_initial'),  # BallotSubmission
        ('adjfeedback', '0003_auto_20160103_1927'),  # AdjudicatorFeedback, AdjudicatorTestScoreHistory
        ('tournaments', '0014_delete_old_availability_models'),  # Round, Tournament (select_related by Round)
        ('motions', '0006_auto_20160621_1129'),  # Motion
        ('breakqual', '0012_convert_aida_pre2015_to_1996'),  # BreakCategory
        ('participants', '0005_auto_20160112_1448'),  # Adjudicator, Institution (select_related by Adjudicator)
    ]

    operations = [
        migrations.RunPython(convert_content_objects, reverse_code=migrations.RunPython.noop),
    ]
