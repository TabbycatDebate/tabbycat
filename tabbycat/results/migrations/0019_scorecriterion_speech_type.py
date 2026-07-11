from django.db import migrations, models
import django.utils.translation


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0018_ballotsubmission_forfeit"),
    ]

    operations = [
        migrations.AddField(
            model_name="scorecriterion",
            name="speech_type",
            field=models.CharField(
                choices=[
                    ("A", django.utils.translation.gettext_lazy("All speeches")),
                    ("S", django.utils.translation.gettext_lazy("Substantive speeches")),
                    ("R", django.utils.translation.gettext_lazy("Reply speeches")),
                ],
                default="A",
                max_length=1,
                verbose_name="speech type",
            ),
        ),
    ]
