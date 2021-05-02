"""Base classes for tournament data importers."""

import csv
import logging
import re
from collections import Counter
from types import GeneratorType

from django.core.exceptions import FieldError, MultipleObjectsReturned, ObjectDoesNotExist, ValidationError

NON_FIELD_ERRORS = '__all__'
DUPLICATE_INFO = 19  # Logging level just below INFO
logging.addLevelName(DUPLICATE_INFO, 'DUPLICATE_INFO')

TRUE_VALUES = ('true', 'yes', 't', 'y', '1')
FALSE_VALUES = ('false', 'no', 'f', 'n', '0')


def convert_bool(value):
    if value.lower() in TRUE_VALUES:
        return True
    elif value.lower() in FALSE_VALUES:
        return False
    else:
        raise ValueError('Invalid boolean value: %s' % (value,))


def make_interpreter(DELETE=[], **kwargs):  # noqa: N803
    """Convenience function for building an interpreter. The default interpreter
    (i.e. the one returned if no arguments are passed to this function) just
    removes blank values."""
    def interpreter(lineno, line):
        # remove blank and unwanted values
        line = {
            fieldname: value for fieldname, value in line.items() if (
                value != '' and
                value is not None and
                fieldname not in DELETE and
                not any(callable(delete) and delete(fieldname) for delete in DELETE)
            )
        }

        # populate interpreted values
        for fieldname, interpret in kwargs.items():
            if not callable(interpret): # if it's a value, always populate
                line[fieldname] = interpret
            elif fieldname in line: # if it's a function, interpret only if already there
                line[fieldname] = interpret(line[fieldname])

        return line
    return interpreter


def make_lookup(name, choices):
    """Convenience function for building a lookup function, which maps valid
    user input values to a standardized string. Lookups are case-insensitive.
    `name` is a string used in an error message if lookup fails.

    `choices` should be a dict mapping a tuple of valid choices to a value. All
    choices must be specified as lower-case. For example, one entry in the
    choices dict might be: {('female', 'f'): 'F'}
    """
    def lookup(val):
        if not val:
            return ''
        for k, v in choices.items():
            if val.lower().replace("-", " ") in k:
                return v
        raise ValueError("Unrecognised value for %s: %s" % (name, val))
    return staticmethod(lookup)


class TournamentDataImporterFatal(Exception):
    pass


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
            message = "Model validation failed: " + str(ve)
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
        interpreter = make_interpreter(
            institution=lambda x: participants.models.Institution.objects.get(name=x),
        )
        self._import(f, participants.models.Speaker, interpreter)

    See the documentation for _import for more details.
    """

    def __init__(self, tournament, **kwargs):
        self.tournament = tournament
        self.strict = kwargs.get('strict', True)
        self.logger = kwargs.get('logger', None) or logging.getLogger(__name__) # don't evaluate default unless necessary
        if 'loglevel' in kwargs:
            self.logger.setLevel(kwargs['loglevel'])
        self.expect_unique = kwargs.get('expect_unique', True)
        self.reset_counts()

    def reset_counts(self):
        self.counts = Counter()
        self.errors = TournamentDataImporterError()

    def _import(self, csvfile, model, interpreter=make_interpreter(), expect_unique=None):
        """Parses the object given in f, using the callable interpreter to parse
        each line, and passing the arguments to the given model's constructor.
        `csvfile` can be any object that is supported by csv.DictReader(), which
        includes file objects and lists of strings.

        If `csvfile` supports the seek() method (e.g., file objects),
        `csvfile.seek(0)` will be called, to allow this function to be called
        multiple times on the same file. This means that csvfile, if a file
        object, must be seekable.

        `interpreter` takes a dict in the form returned by `csv.DictReader`, and
        generally must return a dict of keyword argments that can be passed to
        the model constructor. If `interpreter(line)` returns None, the line is
        skipped. `interpreter` can be a generator or return a list of dicts; if
        so, one instance is created for each dict yielded. If omitted, the dict
        returned by `csv.DictReader` will be passed through a default
        interpreter, which just removes blank fields.

        Returns a dict mapping line numbers to instances created in this import.
        If `interpreter` is a generator or returns a list, the keys will be
        2-tuples (lineno, itemno) instead.

        Callers may also access two attributes, which are updated every time
        this function is called. The first, `self.counts` is a Counter object
        (from Python's collections module) in which the keys are models (e.g.
        Round, Team) and the values are the number that were created. The
        second, `self.errors` is a (possibly empty) TournamentDataImporterError
        object. If `self.strict` is True, then `self.errors` will always be
        empty (since otherwise it would have raised it as an exception);
        otherwise, it will contain the errors raised during the import attempt.

        If `expect_unique` is True, this function checks that there are no
        duplicate objects before saving any of the objects it creates. If
        `expect_unique` is False, it will just skip objects that would be
        duplicates and log a DUPLICATE_INFO message to say so.
        """
        if hasattr(csvfile, 'seek') and callable(csvfile.seek):
            csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        kwargs_seen = list()
        instances = dict()
        errors = TournamentDataImporterError()
        if expect_unique is None:
            expect_unique = self.expect_unique
        skipped_because_existing = 0
        boolean_fields = [field.name for field in model._meta.get_fields()
                          if hasattr(field, 'get_internal_type') and
                          field.get_internal_type() == 'BooleanField']

        for lineno, line in enumerate(reader, start=2):

            # Strip whitespace first
            for k in line:
                if isinstance(line[k], str):
                    line[k] = line[k].strip()

            # Interpret the line
            try:
                kwargs_list = interpreter(lineno, line)
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
                list_provided = False
                kwargs_list = [kwargs_list]
            else:
                list_provided = True

            # Create the instances
            for itemno, kwargs in enumerate(kwargs_list, start=1):

                # Extra conversion for booleans (Django's BooleanField.to_python() is too restrictive)
                boolean_error = False
                for fieldname in kwargs:
                    if fieldname in boolean_fields:
                        try:
                            kwargs[fieldname] = convert_bool(kwargs[fieldname])
                        except ValueError as e:
                            errors.add(lineno, model, str(e))
                            boolean_error = True
                if boolean_error:
                    continue

                description = model.__name__ + "(" + ", ".join(["%s=%r" % args for args in kwargs.items()]) + ")"

                # Check if it's a duplicate
                kwargs_expect_unique = kwargs.copy()
                if kwargs_expect_unique in kwargs_seen:
                    if expect_unique:
                        message = "Duplicate " + description
                        errors.add(lineno, model, message)
                    else:
                        self.logger.log(DUPLICATE_INFO, "Skipping duplicate " + description)
                    continue
                kwargs_seen.append(kwargs_expect_unique)

                # Create (but don't save) an instance (or handle an error)
                try:
                    inst = model.objects.get(**kwargs)
                except ObjectDoesNotExist:
                    inst = model(**kwargs)  # normal case (create object)
                except MultipleObjectsReturned as e:
                    if expect_unique:
                        errors.add(lineno, model, str(e))
                    continue
                except FieldError as e:
                    match = re.match(r"Cannot resolve keyword '(\w+)' into field.", str(e))
                    if match:
                        message = "There's an unrecognized column header in this file: {}".format(match.group(1))
                        self.logger.error(message)
                        self.logger.error("I was trying to import %s at the time.", model._meta.verbose_name_plural)
                        self.logger.error("The original error was: " + str(e))
                        self.logger.error("If you're writing a new importer, it might be that you "
                                "need to delete some columns from the dict in your interpreter.")
                        self.logger.error("If using construct_interpreter(), you can do this with the DELETE argument.")
                        raise TournamentDataImporterFatal(message)
                    else:
                        raise
                except ValueError as e:
                    errors.add(lineno, model, str(e))
                    continue
                except ValidationError as e:
                    errors.update_with_validation_error(lineno, model, e)
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

                key = (lineno, itemno) if list_provided else lineno
                self.logger.debug("To create from line %s: %s", key, description)
                instances[key] = inst

        # Report errors, if any
        if errors:
            if self.strict:
                for message in errors.itermessages():
                    self.logger.error(message)
                raise errors
            else:
                for message in errors.itermessages():
                    self.logger.warning(message)
                self.errors.update(errors)

        # Create the instances
        for lineno, inst in instances.items():
            inst.save()
            self.logger.debug("Made %s from line %s: %r", model._meta.verbose_name, lineno, inst)

        self.logger.info("Imported %d %s", len(instances), model._meta.verbose_name_plural)
        if skipped_because_existing:
            self.logger.info("(skipped %d %s)", skipped_because_existing, model._meta.verbose_name_plural)

        self.counts.update({model: len(instances)})

        return instances
