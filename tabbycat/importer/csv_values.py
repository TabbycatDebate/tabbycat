"""Value conversions shared by command and wizard importers."""

TRUE_VALUES = ('true', 'yes', 't', 'y', '1')
FALSE_VALUES = ('false', 'no', 'f', 'n', '0')


def convert_bool(value):
    if value.lower() in TRUE_VALUES:
        return True
    elif value.lower() in FALSE_VALUES:
        return False
    else:
        raise ValueError('Invalid boolean value: %s' % (value,))
