from typing import Any, Callable
import os
import sys
import logging
import logging.handlers

import configparser
from distutils.version import StrictVersion as Version

# noinspection PyUnresolvedReferences
import __main__ as program


class _StandardOutputFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return super().filter(record) and record.levelno == logging.INFO


class _StandardErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return super().filter(record) and logging.WARN <= record.levelno


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
        self.my_base = os.path.join("org.sleepingcats", "PiAvSwitchController")
        self.my_name = "org.sleepingcats.PiAvSwitchController"
        self.my_title = "A/V Switch Controller"
        self.my_path = os.path.realpath(os.path.abspath(program.__file__))
        self.my_dir = os.path.dirname(self.my_path)
        self.shutting_down = False

        # XDG paths, we get these without XDG to avoid the dependency until we install it.
        xdg_config_home = os.getenv("XDG_CONFIG_HOME", os.path.expandvars(os.path.join("$HOME", ".config")))
        xdg_cache_home = os.getenv("XDG_CACHE_HOME", os.path.expandvars(os.path.join("$HOME", ".cache")))

        # Path for the state data.
        self.__state_file_path = os.path.join(xdg_config_home, self.my_base, "state.ini")

        # Path for storing log files.
        self.__log_file_path = os.path.join(xdg_cache_home, self.my_base, "user.log")
        os.makedirs(os.path.dirname(self.__log_file_path), exist_ok=True)

        # Path for the configuration file.
        self.config_file_path = os.path.join(self.my_dir, "config", "piavswictrl.json")
        self.config_dir = os.path.dirname(self.config_file_path)

        # Setup basic logging data.
        console_format = logging.Formatter(fmt='%(message)s')
        file_handler = logging.handlers.RotatingFileHandler(self.__log_file_path, maxBytes=4194304, backupCount=4)
        file_handler.setFormatter(logging.Formatter(fmt='%(asctime)-15s - %(levelname)8s: %(name)s; %(message)s'))
        output_handler = logging.StreamHandler(stream=sys.stdout)
        output_handler.addFilter(_StandardOutputFilter())
        output_handler.setFormatter(console_format)
        error_handler = logging.StreamHandler(stream=sys.stderr)
        error_handler.addFilter(_StandardErrorFilter())
        error_handler.setFormatter(console_format)

        logging.basicConfig(level=logging.INFO, handlers=(file_handler, output_handler, error_handler))
        self.__my_log = logging.getLogger(__name__)

        # Default values
        self.last_setup_version = Version("0.0.0")

        self.__config = configparser.ConfigParser()

    def __enter__(self):
        """The `with` entry handler, reads the `state.ini` data."""
        try:
            self.__config.read(self.__state_file_path)
            self.__read()
        except IOError as e:
            # It's not there, or we will default the values and attempt to overwrite the file.
            pass

        return self

    def __exit__(self, *args):
        """The `with` exit handler, saves the `state.ini` data."""
        # Let's always update this
        self.last_setup_version = self.version

        # Make sure the path exists.
        config_directory = os.path.dirname(self.__state_file_path)
        if not os.path.isdir(config_directory):
            os.makedirs(config_directory)

        # Now, open and save the configuration.
        with open(self.__state_file_path, "w") as file:
            self.__write()
            self.__config.write(file)

    @staticmethod
    def get_app_path(sub: str = '') -> str:
        """
        Resolves an application path.
        :param sub: If present, a relative from the application path to be resolved; otherwise, the base path is returned.
        :return:    The absolute resolved path.
        """
        return os.path.abspath(os.path.join(State.current.my_dir, sub))

    @staticmethod
    def get_config_path(sub: str = '') -> str:
        """
        Resolves a configuration path.
        :param sub: If present, a relative from the configuration file to be resolved; otherwise, the base path is returned.
        :return:    The absolute resolved path.
        """
        return os.path.abspath(os.path.join(State.current.config_dir, sub))

    def __read(self):
        """Reads the values from `state.ini` data."""
        self.last_setup_version = self.__get("General", "last setup version", True,
                                             self.last_setup_version, lambda value: Version(value))

    def __write(self):
        """Writes values to `state.ini` data."""
        self.__config.clear()
        self.__config.add_section("General")
        self.__config.set("General", "last setup version", str(self.last_setup_version))
        self.__config.set("General", "config file path", str(self.config_file_path))

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
