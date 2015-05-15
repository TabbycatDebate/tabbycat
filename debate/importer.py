"""Functions for importing from CSV files into the database.
All 'file' arguments must be """

import csv
import logging
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from collections import Counter

import debate.models as m

NON_FIELD_ERRORS = '__all__'

class TournamentDataImporterError(Exception):
    """Inspired by Django's ValidationError, but adapted for the importer's
    needs. This keeps track of multiple errors and is initialized blank.
    Before raising, check whether there is anything in it:
        errors = TournamentDataImporterError()
        ...
        if errors:
            raise errors
    """

    class Entry(object):
        def __init__(self, lineno, model, message, field=NON_FIELD_ERRORS):
            self.lineno = lineno
            self.model = model._meta.verbose_name
            self.field = field
            self.message = message

        def __str__(self):
            if self.field == NON_FIELD_ERRORS:
                return "line %d, creating %s: %s" % (self.lineno, self.model, self.message)
            else:
                return "line %d, creating %s, in field '%s': %s" % (self.lineno, self.model, self.field, self.message)

    def __init__(self):
        self.entries = []

    def __nonzero__(self):
        return len(self.entries) > 0

    def __len__(self):
        return len(self.entries)

    def __str__(self):
        """Returns a newline-delimited string of error messages."""
        return "\n".join(map(str, self.entries))

    def add(self, *args, **kwargs):
        """Adds a new error. Takes the arguments of the Entry constructor."""
        self.entries.append(self.Entry(*args, **kwargs))

    def update_with_validation_error(self, lineno, model, ve):
        """Adds the information in a Django ValidationError to this error."""
        if hasattr(ve, 'error_dict'):
            for field, error_list in ve.error_dict.items():
                for error in error_list:
                    self.add(lineno, model, error.message, field)
        elif hasattr(ve, 'error_list'):
            for error in ve.error_list:
                self.add(lineno, model, error.message, NON_FIELD_ERRORS)
        else:
            message = "Model validation failed: "+ str(ve)
            self.add(lineno, model, message, NON_FIELD_ERRORS)

    def update(self, tdie):
        """Adds the entries in another TournamentDataImporterError to this one."""
        self.entries.extend(tdie.entries)

    def itermessages(self):
        """Iterates through the error messages."""
        for entry in self.entries:
            yield str(entry)


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

    # --------------------------------------------------------------------------
    # Helper methods
    # --------------------------------------------------------------------------

    def _lookup(self, d, code, name):
        for k, v in d.iteritems():
            if code.lower().replace("-"," ") in k:
                return v
        self.logger.warning("Unrecognized code for %s: %s", name, code)
        return None

    def _import(self, csvfile, line_parser, model, counts=None, errors=None,
                expect_unique=True):
        """Parses the object given in f, using the callable line_parser to parse
        each line, and passing the arguments to the given model's constructor.
        'csvfile' can be any object that is supported by csv.reader(), which
        includes file objects and lists of strings.

        If csvfile supports the seek() method (e.g., file objects),
        csvfile.seek(0) will be called, to allow this function to be called
        multiple times on the same file. This means that csvfile, if a file
        object, must be seekable.

        'line_parser' must take a single argument, a tuple (the CSV line), and
        return a dict of arguments that can be passed to the model constructor.
        If 'line_parser' returns None, the line is skipped.

        Returns a tuple of two objects. The first is a Counter object (from
        Python's collections module) in which the keys are models (e.g. Round,
        Team) and the values are the number that were created. The second is a
        (possibly empty) TournamentDataImporterError object. If self.strict is
        True, then the returned TournamentDataImporterError will always be empty
        (since otherwise it would have raised it as an exception); otherwise, it
        will contain the errors raised during the import attempt.

        If 'counts_in' and/or 'errors_in' are provided, this function adds the
        counts and errors from this _import call and returns them instead. This
        modifies the original counts_in and errors_in. This allows easy daisy-
        chaining of successive _import calls. If provided, 'counts_in' should
        behave like a Counter object and 'errors_in' should behave like a
        TournamentDataImporterError object.
        """
        if hasattr(csvfile, 'seek') and callable(csvfile.seek):
            csvfile.seek(0)
        reader = csv.reader(csvfile)
        if self.header_row:
            reader.next()
        kwargs_seen = list()
        insts = list()
        if counts is None:
            counts = Counter()
        if errors is None:
            errors = TournamentDataImporterError()

        for lineno, line in enumerate(reader, start=1):
            try:
                kwargs = line_parser(line)
            except (ObjectDoesNotExist, MultipleObjectsReturned, ValueError,
                    TypeError, IndexError) as e:
                message = "Couldn't parse line: " + str(e)
                errors.add(lineno, model, message)
                continue

            if kwargs is None:
                continue

            description = model._meta.verbose_name + "(" + ", ".join(["%s=%r" % args for args in kwargs.items()]) + ")"

            # Check if it's a duplicate
            if kwargs in kwargs_seen:
                if expect_unique:
                    message = "Duplicate " + description
                    errors.add(lineno, model, message)
                else:
                    self.logger.info("Skipping duplicate " + description)
                continue
            kwargs_seen.append(kwargs)

            # Retrieve the instance or create it if it doesn't exist
            try:
                inst = model.objects.get(**kwargs)
            except ObjectDoesNotExist as e:
                inst = model(**kwargs)
            except MultipleObjectsReturned as e:
                if expect_unique:
                    errors.add(lineno, model, e.message)
                continue
            else:
                if expect_unique:
                    message = description + "already exists"
                    errors.add(lineno, model, message)
                else:
                    self.logger.info("Skipping %s, already exists", description)
                continue

            try:
                inst.full_clean()
            except ValidationError as e:
                errors.update_with_validation_error(lineno, model, e)
                continue

            insts.append(inst)

        if errors:
            if self.strict:
                for message in errors.itermessages():
                    self.logger.error(message)
                raise errors
            else:
                for message in errors.itermessages():
                    self.logger.warning(message)

        for inst in insts:
            self.logger.debug("Made %s: %s", model._meta.verbose_name, inst)
            inst.save()

        self.logger.info("Imported %d %ss", len(insts), model._meta.verbose_name)

        counts.update({model: len(insts)})
        return counts, errors

    # --------------------------------------------------------------------------
    # Import methods
    # --------------------------------------------------------------------------

    def import_rounds(self, f):
        """Imports rounds from a file.
        Each line has:
            seq, name, abbreviation, stage, draw_type, silent, feedback_weight
        """
        def _round_line_parser(line):
            return {
                'tournament'      : self.tournament,
                'seq'             : int(line[0]),
                'name'            : line[1],
                'abbreviation'    : line[2],
                'stage'           : self._lookup(self.ROUND_STAGES, line[3] or "p", "draw stage"),
                'draw_type'       : self._lookup(self.ROUND_DRAW_TYPES, line[4] or "r", "draw type"),
                'silent'          : bool(int(line[5])),
                'feedback_weight' : float(line[6]) or 0.7,
            }
        counts, errors = self._import(f, _round_line_parser, m.Round)

        # Set the round with the lowest known seqno to be the current round.
        # TODO (as above)
        self.tournament.current_round = m.Round.objects.get(
                tournament=self.tournament, seq=1)
        self.tournament.save()

        return counts, errors

    def import_institutions(self, f):
        """Imports institutions from a file.
        Each line has:
            name, code, abbreviation
        """
        def _institution_line_parser(line):
            return {
                'name'         : line[0],
                'code'         : line[1],
                'abbreviation' : line[2],
            }
        return self._import(f, _institution_line_parser, m.Institution)

    def import_venue_groups(self, f):
        """Imports venue groups from a file.
        Each line has:
            name, short_name[, team_capacity]
        """
        def _venue_group_line_parser(line):
            kwargs = {
                'name'       : line[0],
                'short_name' : line[1],
            }
            if len(line) > 2:
                kwargs['team_capacity'] = line[2]
            return kwargs
        return self._import(f, _venue_group_line_parser, m.VenueGroup)

    def import_venues(self, f, auto_create_groups=True):
        """Imports venues from a file, also creating venue groups as needed
        (unless 'auto_create_groups' is False).

        Each line has:
            name, priority, venue_group.name, time
        """

        if auto_create_groups:
            def _venue_group_line_parser(line):
                if not line[2]:
                    return None
                return {
                    'name'       : line[2],
                    'short_name' : line[2][:25],
                }
            counts, errors = self._import(f, _venue_group_line_parser,
                    m.VenueGroup, expect_unique=False)

        def _venue_line_parser(line):
            return {
                'tournament' : self.tournament,
                'name'       : line[0],
                'priority'   : int(line[1]) if len(line) > 1 else 10,
                'group'      : m.VenueGroup.objects.get(name=line[2]) if len(line) > 2 else None,
                'time'       : line[3] if len(line) > 3 else None,
            }
        counts, errors = self._import(f, _venue_line_parser, m.Venue, counts=counts, errors=errors)

        return counts, errors

    def import_teams(self, f):
        # TODO
        pass

    def import_speakers(self, f, auto_create_teams=True):
        """Imports speakers from a file, also creating teams as needed (unless
        'auto_create_teams' is False). Institutions are not created as needed;
        if an institution doesn't exist, an error is raised.

        Each line has:
            name, institution_name, team_name, use_team_name_as_prefix, gender,
                    novice_status.
        """

        if auto_create_teams:
            def _team_line_parser(line):
                return {
                    'tournament'             : self.tournament,
                    'institution'            : m.Institution.objects.lookup(line[1]),
                    'reference'              : line[2],
                    'short_reference'        : line[2][:35],
                    'use_institution_prefix' : int(line[3]) if len(line) > 3 else 0,
                }
            counts, errors = self._import(f, _team_line_parser, m.Team, expect_unique=False)
        else:
            counts = Counter()
            errors = TournamentDataImporterError()

        def _speaker_line_parser(line):
            institution = m.Institution.objects.lookup(line[1])
            return {
                'name'   : line[0],
                'team'   : m.Team.objects.get(institution=institution,
                                      reference=line[2], tournament=self.tournament),
                'gender' : line[4] if len(line) > 4 else None,
                'novice' : int(line[5]) if len(line) > 5 and line[5] else None,
            }
        counts, errors = self._import(f, _speaker_line_parser, m.Speaker, counts=counts, errors=errors)

        return counts, errors

    def import_adjudicators(self, f):
        """Imports adjudicators from a file. Institutions are not created as
        needed; if an institution doesn't exist, an error is raised. Conflicts
        are created from the same file, if present.

        Each line has:
            name, institution, rating, gender, novice, cellphone, email,
                    notes, institution_conflicts, team_conflicts
        """
        def _adjudicator_line_parser(line):
            return {
                'name': line[0],
                'institution': m.Institution.objects.lookup(line[1]),
                'test_score': float(line[2]),
                'gender': line[3] if len(line) > 3 else None,
                'novice': int(line[4]) if len(line) > 4 and line[4] else False,
                'phone': line[5] if len(line) > 5 else None,
                'email': line[6] if len(line) > 6 else None,
                'notes': line[7] if len(line) > 7 else None,
            }
        counts, errors = self._import(f, _adjudicator_line_parser, m.Adjudicator)



        # TODO CONTINUE HERE
        # adjudicator conflicts
        # adjudicator-institution conflicts
        # test score history

        return counts, errors


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

    # --------------------------------------------------------------------------
    # Other methods
    # --------------------------------------------------------------------------

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

