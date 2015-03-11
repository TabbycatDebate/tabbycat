"""Functions for importing from CSV files into the database.
All 'file' arguments must be """

import logging
logger = logging.getLogger(__name__)

import debate.models as m

class TournamentDataImporter(object):
"""Imports data for a tournament from CSV files passed as arguments."""

    def __init__(self, tournament, **kwargs):
        self.tournament = tournament
        self.strict = kwargs.get('strict', False)

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
                abbreviation = 'R%d' % i,
                draw_type = m.Round.DRAW_RANDOM if (i == 1) else m.Round.DRAW_POWERPAIRED,
                feedback_weight = min((i-1)*0.1, 0.5),
                silent = (i == num_rounds),
            ).save()
        logger.info("Auto-made {0:d} rounds".format(num_rounds))

    def import_rounds(self, file):
        """Makes rounds according to the given file."""
