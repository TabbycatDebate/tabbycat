from django.db import migrations


def copy_ballots_per_debate(apps, schema_editor):
    Tournament = apps.get_model('tournaments', 'Tournament')  # noqa: N806
    TournamentPreferenceModel = apps.get_model('options', 'TournamentPreferenceModel')  # noqa: N806

    for tournament in Tournament.objects.all():

        all_ballots = TournamentPreferenceModel.objects.get(
            section='debate_rules', name='ballots_per_debate',
            instance_id=tournament.id)

        if all_ballots:
            prelim_ballots = TournamentPreferenceModel(
                section='debate_rules', name='ballots_per_debate_prelim',
                instance_id=tournament.id)
            prelim_ballots.raw_value = all_ballots.raw_value
            prelim_ballots.save()

            elim_ballots = TournamentPreferenceModel(
                section='debate_rules', name='ballots_per_debate_elim',
                instance_id=tournament.id)
            elim_ballots.raw_value = all_ballots.raw_value
            elim_ballots.save()

            all_ballots.delete()


def reverse_copy_ballots_per_debate(apps, schema_editor):
    Tournament = apps.get_model('tournaments', 'Tournament')  # noqa: N806
    TournamentPreferenceModel = apps.get_model('options', 'TournamentPreferenceModel')  # noqa: N806

    for tournament in Tournament.objects.all():

        prelim_ballots = TournamentPreferenceModel.objects.get(
            section='debate_rules', name='ballots_per_debate_prelim',
            instance_id=tournament.id)
        elim_ballots = TournamentPreferenceModel.objects.get(
            section='debate_rules', name='ballots_per_debate_prelim',
            instance_id=tournament.id)

        if prelim_ballots:
            all_ballots = TournamentPreferenceModel(
                section='debate_rules', name='ballots_per_debate',
                instance_id=tournament.id)
            all_ballots.raw_value = prelim_ballots.raw_value
            all_ballots.save()

            prelim_ballots.delete()
            elim_ballots.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0002_move_welcome_message'),
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_ballots_per_debate, copy_ballots_per_debate, elidable=True),
    ]
