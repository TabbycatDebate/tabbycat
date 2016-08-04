# -*- coding: utf-8 -*-

# This is a data migration. It was written manually and its purpose is to
# convert the old "panellist_feedback_enabled" preference to the new
# "feedback_paths" preference. For it to work, you must *not* have run
# `python manage.py checkpreferences` (or `dj checkpreferences`) after commit
# 32e52f9 ("Remove deprecated panellist_feedback_enabled option #350"), which
# removes the old preference. Note that on a Heroku instance, this means that
# commits 32e52f9 through 385d428 ("Implement and close #351") must never have
# been deployed, since the post-compile script runs checkpreferences.
#
# If the old preference doesn't exist, this data migration silently fails.

from __future__ import unicode_literals

from django.db import migrations

TRUE_CONSTANTS = ("True", "true", "TRUE", "1", "YES", "Yes", "yes")


def convert_panellist_feedback_preference(apps, schema_editor):
    TournamentPreferenceModel = apps.get_model("options", "TournamentPreferenceModel")

    old_prefs = TournamentPreferenceModel.objects.filter(section="feedback",
            name="panellist_feedback_enabled")

    for pref in old_prefs:

        # Ordinarily, we're not really meant to access the `raw_value` field
        # directly. But with data migrations the model we're dealing with (the
        # historical version) doesn't actually have any of the non-field
        # properties (i.e., `pref.value` would raise an AttributeError), so we
        # don't really have a choice here.
        new_value = "with-p-on-c" if pref.raw_value in TRUE_CONSTANTS else "minimal"

        # If there already exists a preference, leave it alone.
        if not TournamentPreferenceModel.objects.filter(section="feedback",
                name="feedback_paths", instance_id=pref.instance_id).exists():
            TournamentPreferenceModel.objects.create(section="feedback",
                    name="feedback_paths", instance_id=pref.instance_id, raw_value=new_value)

        # The checkpreferences command would do this, but since this preference
        # doesn't exist anymore, we may as well delete it now.
        pref.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0005_auto_20160228_1838'),
    ]

    operations = [
        migrations.RunPython(convert_panellist_feedback_preference),
    ]
