"""Configuration settings.

This file specifies a class that acts as the interface between the model and
views, and the database.

The general mechanics of configuration settings are as follows:
  - All configuration settings are stored as an instance of the Config model.
  - There is no guarantee that a Config instance actually exists for any
    particular setting. However, if none exists, then the Configuration class in
    this file will return the default value.

Configuration setting definitions are stored at the bottom of this file."""

def ConfigurationSetting(key, type, *args, **kwargs):
    """Factory function. Returns an instance of an appropriate subclass of
    BaseConfigurationSetting."""
    types = {
        "int": IntegerConfigurationSetting,
        "str": StringConfigurationSetting,
        "float": FloatConfigurationSetting,
        "bool": BooleanConfigurationSetting,
        "choice": ChoiceConfigurationSetting,
    }
    klass = types[type];
    return klass(key, *args, **kwargs)


class BaseConfigurationSetting(object):
    """Represents a single configuration setting.
    Mainly a passive data class, knows nothing about the actual configuration values,
    basically just provides the setting definition to other classes.
    Do not instantiate this class directly. Use Configuration.define()."""

    db2py = NotImplemented
    py2db = NotImplemented

    def __init__(self, key, type="int", desc="", help="", default=None, **kwargs):

        self.key = key
        self.desc = desc
        self.help = help
        self.default = default


class IntegerConfigurationSetting(ConfigurationSetting):
    db2py = int
    py2db = str

    def field(self):
        return forms.IntegerField(help_text=self.desc)

    def widget(self):
        pass



class ConfigurationGroup(object):
    """Mainly a convenience class. Behaves as an iterable.
    Provides access to a pre-defined subset of configuration settings.
    Do not instantiate directly."""

    pass

class Configuration(object):
    """Represents the entire configurtion for a tournament."""

    settings = dict()
    groups = dict()

    def __init__(self, tournament):
        self._t = tournament

    def form(self):
        """Returns a Form for the configuration."""
        pass

    def get(self, key):
        """Returns the value associated with that key."""

    def set(self, key, value):
        """Sets the value associated with a key."""


    def get_group(self, key):
        """Returns a ConfigurationGroup object for access to the settings in that
        group."""

    @classmethod
    def define(self, key, **kwargs):
        pass