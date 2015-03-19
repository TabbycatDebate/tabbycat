"""Functions for importing from CSV files into the database.
All 'file' arguments must be """

import csv
import logging

import debate.models as m

class TournamentDataImporter(object):
    """Imports data for a tournament from CSV files passed as arguments."""

    ROUND_STAGES = {
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
        self.strict = kwargs.get('strict', True)
        self.header_row = kwargs.get('header_row', True)
        self.logger = kwargs.get('logger', None) or logging.getLogger(__name__)

    def _lookup(self, d, code, name):
        for k, v in d.iteritems():
            if code.lower() in k:
                return v
        self.logger.warning("Unrecognized code for %s: %s", name, code)
        return None

    def auto_make_rounds(self, num_rounds):
        """Makes the number of rounds specified. The first one is random and the
        rest are all power-paired. The last one is silent. This is intended as a
        convenience function. For anything more complicated, the user should use
        import_rounds() instead."""
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
        self.logger.info("Auto-made %d rounds", num_rounds)

    def _log(self, message):
        self.logger.log(logging.ERROR if self.strict else logging.WARNING, e.message)

    def _import(self, f, line_parser, model):
        """Parses the file object given in f, using the callable line_parser to
        parse each line, and passing the arguments to the given model's
        constructor.

        'line_parser' must take two arguments: a tuple (the CSV line) and the
        line number, and return a dict of arguments that can be passed to the
        model constructor.
        """
        reader = csv.reader(f)
        if self.header_row:
            reader.next()
        insts = list()
        errors = list()

        for i, line in enumerate(reader, start=1):
            try:
                kwargs = line_parser(line, i)
            except (DoesNotExist, MultipleObjectsReturned, ValueError,
                    TypeError, IndexError) as e:
                message = "Couldn't parse file to create %s, in line %d: " % (model.__name__, i) + e.message
                errors.append(message)
                self._log(message)

            inst = model(**kwargs)

            try:
                inst.full_clean()
            except ValidationError as e:
                e.message = "Model validation for %s failed, in line %d: " % (model.__name__, i) + e.message
                errors.append(e)
                self._log(e)
                continue

            insts.append(inst)

        if self.strict and errors:
            raise ValidationError(errors)

        for inst in insts:
            self.logger.debug("Made %s: %s" % (model.__name__, inst))
            inst.save()

        return len(insts), len(errors)

    def import_rounds(self, f):
        def _rounds_line_parser(line, i):
            kwargs = dict()
            kwargs['tournament'] = self.tournament
            kwargs['seq'] = int(line[0]) or i
            kwargs['name'] = str(line[1])
            kwargs['abbreviation'] = str(line[2])
            kwargs['stage'] = self._lookup(self.ROUND_STAGES, str(line[3]) or "p", "draw stage")
            kwargs['draw_type'] = self._lookup(self.ROUND_DRAW_TYPES, str(line[4]) or "r", "draw type")
            kwargs['silent'] = bool(int(line[5]))
            kwargs['feedback_weight'] = float(line[6]) or 0.7
            return kwargs
        result = self._import(f, _rounds_line_parser, m.Round)

        # Set the round with the lowest known seqno to be the current round.
        # TODO (as above)
        self.tournament.current_round = m.Round.objects.get(
                tournament=self.tournament, seq=1)
        self.tournament.save()

        return result
