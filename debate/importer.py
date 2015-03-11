"""Functions for importing from CSV files into the database.
All 'file' arguments must be """

import csv
import logging
logger = logging.getLogger(__name__)

import debate.models as m

class TournamentDataImporter(object):
    """Imports data for a tournament from CSV files passed as arguments."""

    ROUND_DRAW_STAGES = {
        ("preliminary", "p"): "P",
        ("elimination", "break", "e", "b"): "E",
    }

    ROUND_DRAW_TYPES = {
        ("random", "r"): "R",
        ("round-robin", "round robin", "d"): "D",
        ("power-paired", "power paired", "p"): "P",
        ("first elimination", "first-elimination", "1st elimination", "1e", "f"): "F",
        ("subsequent elimination", "subsequent-elimination", "2nd elimination", "2e", "b"): "B",
    }

    def __init__(self, tournament, **kwargs):
        self.tournament = tournament
        self.strict = kwargs.get('strict', False)

    def _lookup(self, d, code, name):
        for k, v in d.iteritems():
            if code.lower() in k:
                return v
        logger.warning("Unrecognized code for %s: %s", name, code)
        return None

    def auto_make_rounds(self, num_rounds):
        """Makes the number of rounds specified. The first one is random and the
        rest are all silent. The last one is This is intended as a convenience function. For
        anything more complicated, the user should use import_rounds()
        instead."""
        for i in range(1, num_rounds+1):
            m.Round(
                tournament=self.tournament,
                seq=i,
                name='Round %d' % i,
                abbreviation='R%d' % i,
                draw_type=m.Round.DRAW_RANDOM if (i == 1) else m.Round.DRAW_POWERPAIRED,
                feedback_weight=min((i-1)*0.1, 0.5),
                silent=(i == num_rounds),
            ).save()
        logger.info("Auto-made %d rounds", num_rounds)

    def import_rounds(self, f):
        """Makes rounds according to the given file."""
        reader = csv.reader(f)
        reader.next() # header row

        i = 1
        total_errors = 0
        rounds_count = 0
        for line in reader:
            seq = int(line[0])
            if not seq:
                seq = i
            name = str(line[1])
            abbreviation = str(line[2])
            draw_stage = self._lookup(self.ROUND_DRAW_STAGES, str(line[3]) or "p", "draw stage")
            draw_type = self._lookup(self.ROUND_DRAW_TYPES, str(line[4]) or "r", "draw type")
            is_silent = bool(int(line[5]))
            feedback_weight = float(line[6]) or 0.7

            try:
                m.Round(
                    tournament=self.tournament,
                    seq=seq,
                    name=name,
                    abbreviation=abbreviation,
                    draw_type=draw_type,
                    stage=draw_stage,
                    feedback_weight=feedback_weight,
                    silent=is_silent
                ).save()
                rounds_count += 1
                i += 1
                logger.debug("Made round %d: %s", seq, name)
            except Exception as e:
                total_errors += 1
                logger.error('Error making round %s: %s', name, e)

        self.tournament.current_round = m.Round.objects.get(
                tournament=self.tournament, seq=1)
        self.tournament.save()
        return rounds_count, total_errors
