import django.db.models.deletion
import utils.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adjallocation', '0010_alter_adjudicatoradjudicatorconflict_unique_together_and_more'),
        ('participants', '0021_team_seed'),
    ]

    operations = [
        migrations.CreateModel(
            name='N1RuleAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('adjudicator', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='participants.adjudicator',
                    verbose_name='adjudicator',
                )),
                ('institution', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='participants.institution',
                    verbose_name='covered institution',
                )),
                ('team', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='participants.team',
                    verbose_name='independent team',
                )),
            ],
            options={
                'verbose_name': 'N-1 rule assignment',
                'verbose_name_plural': 'N-1 rule assignments',
            },
        ),
        migrations.AddConstraint(
            model_name='n1ruleassignment',
            constraint=utils.models.UniqueConstraint(
                fields=('adjudicator', 'institution'),
                name='adjallo_n1ruleassignment_adjudicator__institution_uniq',
            ),
        ),
    ]