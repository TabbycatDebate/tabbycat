from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="adjudicatorfeedbackquestion",
                    name="question_ptr",
                    field=models.OneToOneField(
                        auto_created=True,
                        on_delete=models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="registration.question",
                    ),
                ),
            ]
        ),
    ]
