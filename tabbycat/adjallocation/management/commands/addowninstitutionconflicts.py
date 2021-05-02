from django.db.models import F

from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Adds missing institution conflicts for each teams's and adjudicator's own institution."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--adjudicators-only", action="store_true",
            help="Only add for adjudicators, skip teams")
        parser.add_argument("--teams-only", action="store_true",
            help="Only add for teams, skip adjudicators")

    def handle_tournament(self, tournament, **options):
        if not options["teams_only"]:
            self.add_for_queryset(tournament.adjudicator_set)
        if not options["adjudicators_only"]:
            self.add_for_queryset(tournament.team_set)

    def add_for_queryset(self, qs):
        conflict_model = qs.model.institution_conflicts.through
        field = qs.model.__name__.lower()

        existing = qs.filter(institution_conflicts=F('institution')).count()
        qs = qs.filter(institution__isnull=False).exclude(institution_conflicts=F('institution'))
        missing = qs.count()

        conflict_model.objects.bulk_create([
            conflict_model(**{field: obj, "institution": obj.institution}) for obj in qs
        ])
        self.stdout.write("Done, created {missing} previously-missing {model} own-institution conflicts.".format(
            missing=missing, model=qs.model._meta.verbose_name))
        self.stdout.write("{existing} {models} already had own-institution conflicts defined.".format(
            existing=existing, models=qs.model._meta.verbose_name_plural))
