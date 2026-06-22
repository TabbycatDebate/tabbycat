import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adjallocation', '0011_n1ruleassignment'),
        ('participants', '0021_team_seed'),
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='N1RuleFinePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('fines_paid', models.PositiveIntegerField(default=0, verbose_name='fines paid')),
                ('institution', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='participants.institution',
                    verbose_name='institution',
                )),
                ('team', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='participants.team',
                    verbose_name='independent team',
                )),
                ('tournament', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='n1_fine_payments',
                    to='tournaments.tournament',
                    verbose_name='tournament',
                )),
            ],
            options={
                'verbose_name': 'N-1 rule fine payment',
                'verbose_name_plural': 'N-1 rule fine payments',
            },
        ),
        migrations.AddConstraint(
            model_name='n1rulefinepayment',
            constraint=models.UniqueConstraint(
                condition=models.Q(institution__isnull=False),
                fields=('tournament', 'institution'),
                name='unique_n1fine_institution',
            ),
        ),
        migrations.AddConstraint(
            model_name='n1rulefinepayment',
            constraint=models.UniqueConstraint(
                condition=models.Q(team__isnull=False),
                fields=('tournament', 'team'),
                name='unique_n1fine_team',
            ),
        ),
    ]
