from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0015_alter_bulknotification_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentmessage',
            name='esp_message_id',
            field=models.CharField(blank=True, db_index=True, max_length=254, null=True, verbose_name='email provider message ID'),
        ),
    ]
