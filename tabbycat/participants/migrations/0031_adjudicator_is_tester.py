from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0030_adjudicator_registration_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjudicator',
            name='is_tester',
            field=models.BooleanField(blank=True, default=False, help_text='Whether this adjudicator tests other adjudicators. Members of the adjudication core count as testers whether or not this is checked', verbose_name='tester'),
        ),
    ]
