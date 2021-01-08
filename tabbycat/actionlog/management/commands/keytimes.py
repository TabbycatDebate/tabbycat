import csv
import datetime

from django.utils import timezone

from actionlog.models import ActionLogEntry
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Prints a summary of key action log times in preliminary rounds"

    def handle_tournament(self, tournament, **options):

        writer = csv.writer(self.stdout)

        headings = [
            'round',
            'create',
            'importance',
            'adj-auto',
            'adj-done',
            'venues',
            'motion',
            'starts-at',
            'first-in',
            'first-conf',
            'last-in',
            'last-conf',
        ]
        writer.writerow(headings)

        rounds = tournament.prelim_rounds()

        for round in rounds:

            queryset = round.actionlogentry_set.order_by('timestamp')

            # Find the last adj save before venue allocation
            venues_last_allocated = queryset.filter(type=ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE).last()
            adj_saves = queryset.filter(type=ActionLogEntry.ACTION_TYPE_ADJUDICATORS_SAVE)
            if venues_last_allocated:
                adj_saves = adj_saves.filter(timestamp__lte=venues_last_allocated.timestamp)
            last_adj_save = adj_saves.last()

            entries = [
                queryset.filter(type=ActionLogEntry.ACTION_TYPE_DRAW_CREATE).first(),
                queryset.filter(type__in=[
                    ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT,
                    ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_AUTO,
                ]).first(),
                queryset.filter(type__in=[
                    ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO,
                    ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_DEBATES_AUTO,
                ]).first(),
                last_adj_save,
                venues_last_allocated,
                # "start at" times goes here
                queryset.filter(type__in=[
                    ActionLogEntry.ACTION_TYPE_BALLOT_CREATE,
                    ActionLogEntry.ACTION_TYPE_BALLOT_SUBMIT,
                ]).first(),
                queryset.filter(type=ActionLogEntry.ACTION_TYPE_BALLOT_CONFIRM).first(),
                queryset.filter(type__in=[
                    ActionLogEntry.ACTION_TYPE_BALLOT_CREATE,
                    ActionLogEntry.ACTION_TYPE_BALLOT_SUBMIT,
                ]).last(),
                queryset.filter(type=ActionLogEntry.ACTION_TYPE_BALLOT_CONFIRM).last(),
            ]
            times = [timezone.localtime(entry.timestamp) if entry else None for entry in entries]
            date = next((t for t in times[:5][::-1] if t is not None), None)

            if round.starts_at and date is not None:
                starts_at = datetime.datetime.combine(date.date(), round.starts_at)
                times.insert(5, starts_at - datetime.timedelta(minutes=15))
                times.insert(6, starts_at)
            else:
                times.insert(5, None)
                times.insert(6, None)

            row = [round.name]
            row.extend(x.strftime("%H:%M") if x else None for x in times)
            writer.writerow(row)
