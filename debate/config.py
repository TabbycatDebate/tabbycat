"""Configuration settings.
This file specifies a class that acts as the interface between the
model and views, and the database."""

class ConfigurationSetting(object):
    """Represents a single configuration setting.
    Mainly a passive data class, knows nothing about the actual configuration values,
    basically just provides the setting definition to other classes.
    Do not instantiate this class directly. Use Configuration.define()."""

    def __init__(self, key, type="int", desc="", help="", default=None, **kwargs):


        self.key = key
        self.desc = desc
        self.help = help
        self.default = default

        if "coerce" in kwargs:
            self._coerce = coerce
        if "field" in kwargs:
            self._field = field
        if "widget" in kwargs:
            self._widget = widget

    def coerce(self, value):
        if hasattr(self, "_coerce"):
            return self._coerce(value)

    def field(self):
        if hasattr(self, "_field"):
            return self._field

    def widget(self):
        if hasattr(self, "_widget"):
            return self._widget

class ConfigurationGroup(object):
    """Mainly a convenience class.
    Provides access to a pre-defined subset of configuration settings.
    Do not instantiate directly."""

    pass

class Configuration(object):

    settings = dict()
    groups = dict()

    def __init__(self, tournament):
        self._t = tournament

    def form(self):
        """Returns a Form for the configuration."""
        pass

    def get(self, key):
        """Returns the value associated with that key."""

    def get_group(self, key):
        """Returns a ConfigurationGroup object for access to the settings in that
        group."""

    @classmethod
    def define(self, key, **kwargs):
        pass