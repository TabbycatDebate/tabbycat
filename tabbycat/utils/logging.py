import logging


class ExceptFilter(logging.Filter):
    """The negative of the base Python filter: Only allows records *not* below
    a certain point in the logger hierarchy.
    See: https://docs.python.org/3/library/logging.html#filter-objects
    """

    def filter(self, record):
        return not super().filter(record)
