import os
import shutil

import xdg.BaseDirectory
from xdg.DesktopEntry import DesktopEntry

import tkinter as tk
from tkinter import messagebox

# noinspection PyUnresolvedReferences
import __main__ as program

# TODO:
#    # Planned features
#    - Easy:  We will be asking the user if they want to setup an auto-startup entry here and doing so when allowed.
#    - Easy:  Save and read if we've already asked about the start-up entry.
#    - Easy:  Ensure we only run installation on new version...
#    - Minor: Migrate of configuration data.
#    - Major: Setup UI for switches, monitors, and devices.


class _Setup:
    def __init__(self):
        self.__python = shutil.which('python3')
        self.__my_name = 'org.sleepingcats.PiAvSwitchController'
        self.__my_path = os.path.realpath(os.path.abspath(program.__file__))
        self.__user_auto_start_directory = os.path.join(xdg.BaseDirectory.xdg_config_home, 'autostart')
        self.__auto_start_entry = os.path.join(self.__user_auto_start_directory, "{}.desktop".format(self.__my_name))
        self.__auto_start_directories = list(xdg.BaseDirectory.load_config_paths('autostart'))

    def has_startup(self) -> bool:
        if self.__user_auto_start_directory not in self.__auto_start_directories:
            return False

        if not os.path.isfile(self.__auto_start_entry):
            return False

        return True

    def add_startup(self) -> None:
        entry = DesktopEntry()
        entry.addGroup(DesktopEntry.defaultGroup)
        entry.set('Type', 'Application')
        entry.set('Name', self.__my_name)
        entry.set('Exec', "{0} \"{1}\"".format(self.__python, self.__my_path))
        entry.write(self.__auto_start_entry)


def perform() -> None:
    dummy_root = tk.Tk()
    dummy_root.withdraw()

    setup = _Setup()
    if not setup.has_startup():
        if messagebox.askyesno('A/V Switch Controller',
                               'Do you want to automatically start the A/V Switch Controller'):
            setup.add_startup()

    dummy_root.destroy()
