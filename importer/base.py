"""Base classes for tournament data importers."""

import csv
import logging
import itertools
import random
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from collections import Counter
from types import GeneratorType

from participants.models import Team
from participants.emoji import EMOJI_LIST

NON_FIELD_ERRORS = '__all__'
DUPLICATE_INFO = 19 # logging level just below INFO
logging.addLevelName(DUPLICATE_INFO, 'DUPLICATE_INFO')

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
            self.model = model._meta.verbose_name.lower()
            self.field = field
            self.message = message

        def __str__(self):
            if self.field == NON_FIELD_ERRORS:
                return "line %d, creating %s: %s" % (self.lineno, self.model, self.message)
            else:
                return "line %d, creating %s, in field '%s': %s" % (self.lineno, self.model, self.field, self.message)

    def __init__(self):
        self.entries = []

    def __bool__(self):
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
            for field, error_list in list(ve.error_dict.items()):
                for error in error_list:
                    self.add(lineno, model, "; ".join(error), field)
        elif hasattr(ve, 'error_list'):
            for error in ve.error_list:
                self.add(lineno, model, "; ".join(error), NON_FIELD_ERRORS)
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


class BaseTournamentDataImporter(object):
    """Base class for tournament data importers.

    Subclasses should have a number of import_* arguments, each of which should
    call self._import one or more times. The simplest import_* function would
    look like this:

    def import_things(self, f):
        def _speaker_line_parser(line):
            return {
                'instutition': participants.models.Institution.objects.get(name=line[0]),
                'name':        line[1]
            }
        counts, errors = self._import(f, _thing_line_parser, participants.models.Speaker)
        return counts, errors

    See the documentation for _import for more details.
    """

    def __init__(self, tournament, **kwargs):
        self.tournament = tournament
        self.strict = kwargs.get('strict', True)
        self.header_row = kwargs.get('header_row', True)
        self.logger = kwargs.get('logger', None) or logging.getLogger(__name__) # don't evaluate default unless necessary
        if 'loglevel' in kwargs:
            self.logger.setLevel(kwargs['loglevel'])
        self.expect_unique = kwargs.get('expect_unique', True)

    def _lookup(self, d, code, name):
        if not code:
            return None
        for k, v in d.items():
            if code.lower().replace("-"," ") in k:
                return v
        raise ValueError("Unrecognized code for %s: %s" % (name, code))

    def _import(self, csvfile, line_parser, model, counts=None, errors=None,
                expect_unique=None, generated_fields=[]):
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
        If 'line_parser' returns None, the line is skipped. 'line_parser' can
        be a generator; if so, one instance is created for each dict yielded.

        Returns a tuple of two objects. The first is a Counter object (from
        Python's collections module) in which the keys are models (e.g. Round,
        Team) and the values are the number that were created. The second is a
        (possibly empty) TournamentDataImporterError object. If self.strict is
        True, then the returned TournamentDataImporterError will always be empty
        (since otherwise it would have raised it as an exception); otherwise, it
        will contain the errors raised during the import attempt.

        If 'counts' and/or 'errors' are provided, this function adds the counts
        and errors from this _import call and returns them instead. This
        modifies the original counts_in and errors_in. This allows easy daisy-
        chaining of successive _import calls. If provided, 'counts_in' should
        behave like a Counter object and 'errors_in' should behave like a
        TournamentDataImporterError object.

        If 'expect_unique' is True, this function checks that there are no
        duplicate objects before saving any of the objects it creates. If
        'expect_unique' is False, it will just skip objects that would be
        duplicates and log a DUPLICATE_INFO message to say so.

        If 'generated_fields' is given, it must be a callable, and the
        uniqueness checks will not take into account any of the generated
        fields. This should be used for fields that are generated with each
        object, not given in the CSV files.
        """
        if hasattr(csvfile, 'seek') and callable(csvfile.seek):
            csvfile.seek(0)
        reader = csv.reader(csvfile)
        if self.header_row:
            next(reader)
        kwargs_seen = list()
        insts = list()
        if counts is None:
            counts = Counter()
        if errors is None:
            errors = TournamentDataImporterError()
        if expect_unique is None:
            expect_unique = self.expect_unique
        skipped_because_existing = 0

        for lineno, line in enumerate(reader, start=2 if self.header_row else 1):
            try:
                kwargs_list = line_parser(line)
                if isinstance(kwargs_list, GeneratorType):
                    kwargs_list = list(kwargs_list) # force evaluation
            except (ObjectDoesNotExist, MultipleObjectsReturned, ValueError,
                    TypeError, IndexError) as e:
                message = "Couldn't parse line: " + str(e)
                errors.add(lineno, model, message)
                continue

            if kwargs_list is None:
                continue
            if isinstance(kwargs_list, dict):
                kwargs_list = [kwargs_list]

            for kwargs in kwargs_list:
                description = model.__name__ + "(" + ", ".join(["%s=%r" % args for args in kwargs.items()]) + ")"

                # Check if it's a duplicate
                kwargs_expect_unique = kwargs.copy()
                for key in generated_fields:
                    if key in kwargs_expect_unique:
                        del kwargs_expect_unique[key]
                if kwargs_expect_unique in kwargs_seen:
                    if expect_unique:
                        message = "Duplicate " + description
                        errors.add(lineno, model, message)
                    else:
                        self.logger.log(DUPLICATE_INFO, "Skipping duplicate " + description)
                    continue
                kwargs_seen.append(kwargs_expect_unique)

                # Fill in the generated fields
                for key in generated_fields:
                    kwargs[key] = kwargs[key]()

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
                    skipped_because_existing += 1
                    if expect_unique:
                        message = description + " already exists"
                        errors.add(lineno, model, message)
                    else:
                        self.logger.log(DUPLICATE_INFO, "Skipping %s, already exists", description)
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
            self.logger.debug("Made %s: %s", model._meta.verbose_name.lower(), inst)
            inst.save()

        self.logger.info("Imported %d %s", len(insts), model._meta.verbose_name_plural.lower())
        if skipped_because_existing:
            self.logger.info("(skipped %d %s)", skipped_because_existing, model._meta.verbose_name_plural.lower())

        counts.update({model: len(insts)})
        return counts, errors

    def initialise_emoji_options(self):
        """Initialises a list of permissible emoji. Should be called before
        self.get_emoji()."""

        # Get list of all emoji already in use. Teams without emoji are assigned by team ID.
        assigned_emoji_teams = Team.objects.filter(emoji__isnull=False).values_list('emoji', flat=True)
        unassigned_emoji_teams = Team.objects.filter(emoji__isnull=True).values_list('id', flat=True)

        # Start with a list of all emoji...
        self.emoji_options = list(range(0, len(EMOJI_LIST) - 1))

        # Then remove the ones that are already in use
        for index in itertools.chain(assigned_emoji_teams, unassigned_emoji_teams):
            if index in self.emoji_options:
                self.emoji_options.remove(index)

    def get_emoji(self):
        """Retrieves an emoji. If there are any not currently in returns one of
        those. Otherwise, returns any one at random."""
        try:
            emoji_id = random.choice(self.emoji_options)
        except IndexError:
            self.logger.error("No more choices left for emoji, choosing at random")
            return EMOJI_LIST[random.randint(0, len(EMOJI_LIST) - 1)][0]
        self.emoji_options.remove(emoji_id)
        return EMOJI_LIST[emoji_id][0]
