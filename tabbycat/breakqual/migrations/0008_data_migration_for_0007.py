# -*- coding: utf-8 -*-

# This is a data migration. It does the following to follow up 0007_auto_20160806_2020:
#
#  - 0007 changed the semantics of BreakCategory.priority from lowest-first to
#    highest-first (to be consistent with priority fields in other models).
#    This migration updates the priorities by inverting them (setting them to
#    the negative of what they were), so that operation is unaffected by the
#    new semantics.
#
#  - 0007 changed the keys of BreakCategory.rule. This migration updates the
#    field to the equivalent new values.

from __future__ import unicode_literals

from django.db import migrations


RULE_UPDATE_VALUE_MAP = {
    's': 'standard',
    'a': 'aida-pre2015',
    'b': 'aida-2016-australs',
}

def update_breakcategory_priorities_and_rules(apps, schema_editor):
    BreakCategory = apps.get_model("breakqual", "BreakCategory")
    for category in BreakCategory.objects.all():
        category.priority = -category.priority
        try:
            category.rule = RULE_UPDATE_VALUE_MAP[category.rule]
        except KeyError:
            category.rule = 'standard'
        category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('breakqual', '0007_auto_20160806_2020'),
    ]

    operations = [
        migrations.RunPython(update_breakcategory_priorities_and_rules),
    ]
