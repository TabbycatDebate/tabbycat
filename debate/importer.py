"""Functions for importing from CSV files into the database.
All 'file' arguments must be """

import csv
import logging
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError

import debate.models as m

class TournamentDataImporterError(Exception):
    """Inspired by ValidationError, but adapted for the importer's needs."""

    def __init__(self):




class TournamentDataImporter(object):
    """Imports data for a tournament from CSV files passed as arguments."""

    ROUND_STAGES = {
        ("preliminary", "p"): "P",
        ("elimination", "break", "e", "b"): "E",
    }

    ROUND_DRAW_TYPES = {
        ("random", "r"): "R",
        ("round robin", "d"): "D",
        ("power paired", "p"): "P",
        ("first elimination", "1st elimination", "1e", "f"): "F",
        ("subsequent elimination", "2nd elimination", "2e", "b"): "B",
    }

    def __init__(self, tournament, **kwargs):
        self.tournament = tournament
        self.strict = kwargs.get('strict', True)
        self.header_row = kwargs.get('header_row', True)
        self.logger = kwargs.get('logger', None) or logging.getLogger(__name__) # don't evaluate default unless necessary

    def _lookup(self, d, code, name):
        for k, v in d.iteritems():
            if code.lower().replace("-"," ") in k:
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
        self.logger.log(logging.ERROR if self.strict else logging.WARNING, message)

    def _import(self, f, line_parser, model, expect_unique=True):
        """Parses the file object given in f, using the callable line_parser to
        parse each line, and passing the arguments to the given model's
        constructor.

        'line_parser' must take a single argument, a tuple (the CSV line), and
        return a dict of arguments that can be passed to the model constructor.
        """
        reader = csv.reader(f)
        if self.header_row:
            reader.next()
        insts = list()
        errors = TournamentDataImporterError() # initially blank

        for i, line in enumerate(reader, start=1):
            try:
                kwargs = line_parser(line)
            except (ObjectDoesNotExist, MultipleObjectsReturned, ValueError,
                    TypeError, IndexError) as e:
                message = "Couldn't parse line to create %s: " % (model._meta.verbose_name, i) + e.message
                errors.add(i, message)
                self._log(message)
                continue

            if kwargs is None:
                continue

            try:
                inst = model.objects.get(**kwargs)
            except MultipleObjectsReturned as e:
                if expect_unique:
                    errors.add(i, e.message)
                    self._log(e.message)
                continue
            except ObjectDoesNotExist as e:
                inst = model(**kwargs)
            else:
                self.logger.info("Skipping %s: %s, already exists", model._meta.verbose_name, inst)
                continue

            try:
                inst.full_clean()
            except ValidationError as e:
                if hasattr(e, 'error_dict'):
                    pass # CONTINUE HERE
                e.message = "Model validation for %s failed, in line %d: " % (model._meta.verbose_name, i) + e.message
                errors.append(e)
                self._log(e)
                continue

            insts.append(inst)

        if self.strict and errors:
            raise errors

        for inst in insts:
            self.logger.debug("Made %s: %s", model._meta.verbose_name, inst)
            inst.save()

        self.logger.info("Imported %d %ss", len(insts), model._meta.verbose_name)

        return len(insts), len(errors)

    def import_rounds(self, f):
        """Imports rounds from a file.
        Each line has:
            seq, name, abbreviation, stage, draw_type, silent, feedback_weight
        """
        def _round_line_parser(line):
            kwargs = dict()
            kwargs['tournament'] = self.tournament
            kwargs['seq'] = int(line[0])
            kwargs['name'] = line[1]
            kwargs['abbreviation'] = line[2]
            kwargs['stage'] = self._lookup(self.ROUND_STAGES, line[3] or "p", "draw stage")
            kwargs['draw_type'] = self._lookup(self.ROUND_DRAW_TYPES, line[4] or "r", "draw type")
            kwargs['silent'] = bool(int(line[5]))
            kwargs['feedback_weight'] = float(line[6]) or 0.7
            return kwargs
        result = self._import(f, _round_line_parser, m.Round)

        # Set the round with the lowest known seqno to be the current round.
        # TODO (as above)
        self.tournament.current_round = m.Round.objects.get(
                tournament=self.tournament, seq=1)
        self.tournament.save()

        return result

    def import_institutions(self, f):
        """Imports institutions from a file.
        Each line has:
            name, code, abbreviation
        """
        def _institution_line_parser(line):
            kwargs = dict()
            kwargs['name'] = line[0] or None
            kwargs['code'] = line[1] or None
            kwargs['abbreviation'] = line[2]
            return kwargs
        return self._import(f, _institution_line_parser, m.Institution)

    def import_venue_groups(self, f):
        """Imports venue groups from a file.
        Each line has:
            name, short_name[, team_capacity]
        """
        def _venue_group_line_parser(line):
            kwargs = dict()
            kwargs['tournanent'] = self.tournament
            kwargs['name'] = line[0]
            kwargs['short_name'] = line[1]
            if len(line) > 2:
                kwargs['team_capacity'] = line[2]
            return kwargs
        return self._import(f, _venue_group_line_parser, m.VenueGroup)

    def import_venues(self, f):
        """Imports venues from a file, also creating venue groups as needed.
        Each line has:
            name, priority, venue_group.name, time
        """
        def _venue_group_line_parser(line):
            if not line[2]:
                return None
            kwargs = dict()
            # kwargs['tournament'] = self.tournament # check whether VenueGroup should have tournament field?
            kwargs['name'] = line[2] or None
            return kwargs
        self._import(f, _venue_group_line_parser, m.VenueGroup, expect_unique=False)

        def _venue_line_parser(line):
            kwargs = dict()
            kwargs['tournament'] = self.tournament
            kwargs['name'] = line[0]
            kwargs['priority'] = line[1] if len(line) > 1 else 10
            kwargs['group'] = m.VenueGroup.objects.get(tournament=self.tournament, name=line[2]) if len(line) > 2 else None
            kwargs['time'] = line[3] if len(line) > 3 else None
            return kwargs
        self._import(f, _venue_line_parser, m.Venue)


    def import_config(self, f):
        VALUE_TYPES = {"string": str, "int": int, "float": float, "bool": bool}
        def _config_line_parser(line):
            kwargs = dict()
            key = line[0]
            try:
                coerce = VALUE_TYPES[line[1]]
            except KeyError:
                raise ValueError("Unrecognized value type in config: {0:r}".format(line[1]))
            value = coerce(line[2])
