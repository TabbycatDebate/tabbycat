from django.core.management.base import CommandError

from adjallocation.allocators import registry
from tournaments.models import Round
from utils.management.base import RoundCommand


class Command(RoundCommand):

    help = ("Runs the auto-allocator to assign adjudicators to debates. This "
            "always allocates adjudicators to debates (or preformed panels) "
            "directly, even if preformed panels exist.")

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("-a", "--allocator", default="hungarian",
            choices=list(registry.keys()) + ["hungarian"],
            help="Which allocator to use. The option 'hungarian' (default) "
            "chooses between 'hungarian-voting' and 'hungarian-consensus' "
            "according to the tournament \"ballots per debate\" preference.")
        parser.add_argument("-p", "--preformed", action="store_true",
            help="Allocate to preformed panels instead")
        parser.add_argument("-f", "--force", action="store_true",
            help="Run even if draw status is not confirmed")
        parser.add_argument("-q", "--quiet", action="store_true",
            help="Don't print the final full allocation out at the end")
        parser.add_argument("-n", "--dry-run", action="store_true",
            help="Don't write allocation to database, but print out final allocation instead")

    def handle_round(self, round, **options):
        if (not options["preformed"] and not options["force"] and
                round.draw_status != Round.STATUS_CONFIRMED):
            raise CommandError("Draw status isn't confirmed (it's {}), use "
                "--force to run anyway".format(round.get_draw_status_display().lower()))

        if options["preformed"]:
            debates = round.preformedpanel_set.all()
        else:
            debates = round.debate_set.all()

        allocator_key = options["allocator"]
        if allocator_key == 'hungarian':
            allocator_key = 'hungarian-voting' if round.ballots_per_debate == 'per-adj' else 'hungarian-consensus'
            self.stdout.write("Using allocator: " + allocator_key)  # only print if not specified by user

        adjs = round.active_adjudicators.all()
        allocator_class = registry[allocator_key]
        allocator = allocator_class(debates, adjs, round)

        allocations, user_warnings = allocator.allocate()

        if not options["dry_run"]:
            for alloc in allocations:
                alloc.save()
            self.stdout.write(self.style.SUCCESS("Saved debate adjudicators for {:d} debates.".format(len(allocations))))
        else:
            self.stdout.write(self.style.MIGRATE_LABEL("Dry run requested, not saving to database."))

        if not options["quiet"]:
            self.stdout.write(self.style.MIGRATE_HEADING("Allocations:"))
            feedback_weight = round.feedback_weight
            for alloc in allocations:
                self.stdout.write("In {}".format(alloc.container))
                for adj, pos in alloc.with_positions():
                    self.stdout.write("   - {pos} {score:.1f} {adj.name}".format(
                        adj=adj, pos=pos,
                        score=adj.weighted_score(feedback_weight)),
                    )

        if user_warnings:
            self.stdout.write(self.style.WARNING("Warnings:"))
            for msg in user_warnings:
                self.stdout.write(" - " + self.style.WARNING(msg))
