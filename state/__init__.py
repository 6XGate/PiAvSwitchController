from typing import Any, Callable
import os
import sys

import configparser
from distutils.version import StrictVersion as Version

# noinspection PyUnresolvedReferences
import __main__ as program


class State:
    """Contains state data for the program."""

    # Keeps the current state.
    current = None  # type: State

    # noinspection SpellCheckingInspection
    def __init__(self):
        """Initializes a new instance of the State class"""
        # The current state.
        State.current = self

        # Program common names are paths.
        self.python = sys.executable
        self.version = Version(program.__version__)
        self.my_base = 'org.sleepingcats/PiAvSwitchController'
        self.my_name = 'org.sleepingcats.PiAvSwitchController'
        self.my_title = 'A/V Switch Controller'
        self.my_path = os.path.realpath(os.path.abspath(program.__file__))

        # Paths for the state data, we do this without XDG to avoid the dependency until we install it.
        xdg_config_home = os.getenv('XDG_CONFIG_HOME', os.path.expandvars('$HOME/.config'))
        self.__config_file_path = os.path.join(xdg_config_home, self.my_base, 'state.ini')

        # Default values
        self.last_setup_version = Version('0.0.0')

        self.__config = configparser.ConfigParser()

    def __enter__(self):
        """The `with` entry handler, reads the `state.ini` data."""
        try:
            self.__config.read(self.__config_file_path)
            self.__read()
        except IOError:
            # It's not there, or we will default the values and attempt to overwrite the file.
            pass

        return self

    def __exit__(self, *args):
        """The `with` exit handler, saves the `state.ini` data."""
        # Let's always update this
        self.last_setup_version = self.version

        # Make sure the path exists.
        config_directory = os.path.dirname(self.__config_file_path)
        if not os.path.isdir(config_directory):
            os.makedirs(config_directory)

        # Now, open and save the configuration.
        with open(self.__config_file_path, 'w') as file:
            self.__write()
            self.__config.write(file)

    def __read(self):
        """Reads the values from `state.ini` data."""
        self.last_setup_version = self.__get('General', 'last setup version', True,
                                             self.last_setup_version, lambda value: Version(value))

    def __write(self):
        """Writes values to `state.ini` data."""
        self.__config.clear()
        self.__config.add_section('General')
        self.__config.set('General', 'last setup version', str(self.last_setup_version))

    def __get(self, section: str, key: str, raw: bool, base: Any, convert: Callable[[Any], Any] = lambda value: value):
        """
        Gets a value from the `state.ini` data.
        :param section: The name of the section that contains the value.
        :param key:     The key of the value.
        :param raw:     Determines whether to read the raw value or expand any variables.
        :param base:    The default value.
        :param convert: A converter for the value.
        :return: The converted value or the base default.
        :rtype Any
        """
        try:
            return convert(self.__config.get(section, key, raw=raw))
        except IOError:
            return base
        except configparser.Error:
            return base
