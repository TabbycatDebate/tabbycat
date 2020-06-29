from itertools import zip_longest

from adjallocation.preformed import copy_panels_to_debates, registry
from utils.management.base import RoundCommand


class Command(RoundCommand):

    help = "Runs the auto-allocator to assign preformed panels to debates"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("-a", "--allocator", choices=registry.keys(), default="hungarian",
            help="Which allocator to use (default: hungarian)")
        parser.add_argument("-q", "--quiet", action="store_true",
            help="Don't print the final full allocation out at the end")
        parser.add_argument("-n", "--dry-run", action="store_true",
            help="Don't write allocation to database")

    def handle_round(self, round, **options):
        panels = round.preformedpanel_set.all()
        debates = round.debate_set.all()

        allocator_class = registry[options["allocator"]]
        allocator = allocator_class(debates, panels, round)

        debates, panels = allocator.allocate()

        if not options["dry_run"]:
            copy_panels_to_debates(debates, panels)
            print("Copied panels to {:d} debates.".format(len(debates)))
        else:
            print("Dry run requested, not saving to database.")

        if not options["quiet"]:
            print("Allocations:")
            feedback_weight = round.feedback_weight
            for debate, panel in zip_longest(debates, panels, fillvalue=None):
                print("To debate: {}".format(debate))
                if panel is None:
                    print("   - no panel")
                else:
                    for adj, pos in panel.adjudicators.with_positions():
                        print("   - {pos} {score:.1f} {adj.name}".format(
                            adj=adj, pos=pos,
                            score=adj.weighted_score(feedback_weight)),
                        )
