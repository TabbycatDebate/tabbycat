from django.db import migrations


def copy_ballots_per_debate(apps, schema_editor):
    Tournament = apps.get_model('tournaments', 'Tournament')  # noqa: N806
    TournamentPreferenceModel = apps.get_model('options', 'TournamentPreferenceModel')  # noqa: N806

    for tournament in Tournament.objects.all():

        try:
            all_ballots = TournamentPreferenceModel.objects.get(
                section='debate_rules', name='ballots_per_debate',
                instance_id=tournament.id)
        except TournamentPreferenceModel.DoesNotExist:
            continue

        prelim_ballots, _ = TournamentPreferenceModel.objects.get_or_create(
            section='debate_rules', name='ballots_per_debate_prelim',
            instance_id=tournament.id)
        prelim_ballots.raw_value = all_ballots.raw_value
        prelim_ballots.save()

        elim_ballots, _ = TournamentPreferenceModel.objects.get_or_create(
            section='debate_rules', name='ballots_per_debate_elim',
            instance_id=tournament.id)
        elim_ballots.raw_value = all_ballots.raw_value
        elim_ballots.save()

        all_ballots.delete()


def reverse_copy_ballots_per_debate(apps, schema_editor):
    Tournament = apps.get_model('tournaments', 'Tournament')  # noqa: N806
    TournamentPreferenceModel = apps.get_model('options', 'TournamentPreferenceModel')  # noqa: N806

    for tournament in Tournament.objects.all():

        try:
            prelim_ballots = TournamentPreferenceModel.objects.get(
                section='debate_rules', name='ballots_per_debate_prelim',
                instance_id=tournament.id)
        except TournamentPreferenceModel.DoesNotExist:
            continue

        all_ballots = TournamentPreferenceModel.objects.get_or_create(
            section='debate_rules', name='ballots_per_debate',
            instance_id=tournament.id)
        all_ballots.raw_value = prelim_ballots.raw_value
        all_ballots.save()

        prelim_ballots.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0002_move_welcome_message'),
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_ballots_per_debate, copy_ballots_per_debate, elidable=True),
    ]
