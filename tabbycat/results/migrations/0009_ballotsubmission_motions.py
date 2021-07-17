from django.db import migrations
from django.db.models import Count, Prefetch


def modify_ballotsubmission_motions(apps, schema_editor, reverse):
    Tournament = apps.get_model('tournaments', 'Tournament')
    BallotSubmission = apps.get_model('results', 'BallotSubmission')
    Round = apps.get_model('tournaments', 'Round')
    tournaments = Tournament.objects.prefetch_related(Prefetch(
        'round_set', queryset=Round.objects.annotate(
            num_motions=Count('roundmotion')).filter(num_motions=1
        ).prefetch_related('debate_set', 'roundmotion_set')))
    for t in tournaments.all():
        pref, created = t.preferences.get_or_create(section='motions', name='enable_motions', defaults={'raw_value': 'False'})
        if pref.raw_value == 'True':
            continue
        for r in t.round_set.all():
            if r.roundmotion_set.count() != 1:
                continue
            motion_id = None if reverse else r.roundmotion_set.get().motion_id
            BallotSubmission.objects.filter(
                debate__in=list(r.debate_set.all()), motion__isnull=not reverse).update(motion_id=motion_id)


def populate_ballotsubmission_motions(apps, schema_editor):
    modify_ballotsubmission_motions(apps, schema_editor, False)


def depopulate_ballotsubmission_motions(apps, schema_editor):
    modify_ballotsubmission_motions(apps, schema_editor, True)


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0008_auto_20201126_0037'),
        ('motions', '0005_motions_mtm'),
        ('options', '0009_create_motions_section'),
    ]

    operations = [
        migrations.RunPython(populate_ballotsubmission_motions, depopulate_ballotsubmission_motions),
    ]
