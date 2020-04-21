from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError
from django.db.models import Exists, OuterRef, Prefetch

from participants.models import Speaker
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Modifies the break category eligibility of every team to match the " \
           "speaker category eligibility of their speakers, that is, the team " \
           "is eligible for the break category if and only if all speakers in the " \
           "team are eligible for the speaker category. Requires the slugs" \
           "of both categories to be the same."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("slug", type=str, nargs='+',
            help="Slug of break category to modify and speaker category to check")
        parser.add_argument("-n", "--dry-run", action="store_true",
            help="Don't modify the database, just print what would be changed")

    def handle_tournament(self, tournament, **options):
        for slug in options["slug"]:
            try:
                break_category = tournament.breakcategory_set.get(slug=slug)
            except ObjectDoesNotExist:
                raise CommandError("There's no break category with slug '%s'" % slug)

            if not tournament.speakercategory_set.filter(slug=slug).exists():
                raise CommandError("There's no speaker category with slug '%s'" % slug)

            break_subquery = tournament.breakcategory_set.filter(
                team=OuterRef('pk'), slug=slug,
            )
            speaker_subquery = tournament.speakercategory_set.filter(
                speaker=OuterRef('pk'), slug=slug,
            )
            team_queryset = tournament.team_set.prefetch_related(
                Prefetch('speaker_set', queryset=Speaker.objects.annotate(eligible=Exists(speaker_subquery))),
            ).annotate(
                currently_eligible=Exists(break_subquery),
            )

            for team in team_queryset:
                should_be_eligible = all(speaker.eligible for speaker in team.speaker_set.all())

                if not team.currently_eligible and should_be_eligible:
                    if not options["dry_run"]:
                        message = "Making {team.short_name} ({speakers}) eligible for {category.name}"
                        team.break_categories.add(break_category)
                    else:
                        message = "Would make {team.short_name} ({speakers}) eligible for {category.name}"
                    self.stdout.write(message.format(
                        team=team, speakers=", ".join(s.name for s in team.speaker_set.all()),
                        category=break_category,
                    ))

                elif team.currently_eligible and not should_be_eligible:
                    if not options["dry_run"]:
                        message = "Removing {team.short_name} ({speakers}) from {category.name}"
                        team.break_categories.remove(break_category)
                    else:
                        message = "Would remove {team.short_name} ({speakers}) from {category.name}"
                    self.stdout.write(message.format(
                        team=team, speakers=", ".join(s.name for s in team.speaker_set.all()),
                        category=break_category,
                    ))

                elif team.currently_eligible and should_be_eligible and options["verbosity"] > 1:
                    self.stdout.write(" - {team.short_name} ({speakers}) is correctly marked eligible for {category.name}".format(
                        team=team, speakers=", ".join(s.name for s in team.speaker_set.all()),
                        category=break_category,
                    ))
