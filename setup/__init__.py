import os

import xdg.BaseDirectory
from xdg.DesktopEntry import DesktopEntry

import tkinter as tk
from tkinter import messagebox

from state import State

# TODO:
#    # Planned features
#    - Minor: Migrate of configuration data.
#    - Major: Setup UI for switches, monitors, and devices.


class _Setup:
    """Defines any setup process."""

    # noinspection SpellCheckingInspection
    def __init__(self):
        """Initializes a new instance of the _Setup class."""
        self.__user_auto_start_directory = os.path.join(xdg.BaseDirectory.xdg_config_home, 'autostart')
        self.__auto_start_entry = os.path.join(self.__user_auto_start_directory,
                                               "{}.desktop".format(State.current.my_name))
        self.__auto_start_directories = list(xdg.BaseDirectory.load_config_paths('autostart'))

    def has_startup(self) -> bool:
        """Determines whether an auto-start entry exists."""
        if self.__user_auto_start_directory not in self.__auto_start_directories:
            return False

        if not os.path.isfile(self.__auto_start_entry):
            return False

        return True

    def add_startup(self) -> None:
        """Creates the auto-start entry if the user wants one."""
        entry = DesktopEntry()
        entry.addGroup(DesktopEntry.defaultGroup)
        entry.set('Type', 'Application')
        entry.set('Name', State.current.my_name)
        entry.set('Exec', "{0} \"{1}\"".format(State.current.python, State.current.my_path))
        entry.write(self.__auto_start_entry)


def perform() -> None:
    """Performs any setup process need on fresh installs or upgrades."""
    if State.current.version == State.current.last_setup_version:
        # No need to perform any setup.
        return

    print('Performing first time or update setup...')

    dummy_root = tk.Tk()
    dummy_root.withdraw()

    setup = _Setup()
    if not setup.has_startup():
        if messagebox.askyesno(State.current.my_title,
                               'Do you want to automatically start the A/V Switch Controller with your system?'):
            setup.add_startup()

    dummy_root.destroy()
