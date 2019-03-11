from typing import List
import logging

import dbus
import dbus.service

from state import State

log = logging.getLogger(__name__)


class _Installer:
    """Provides the necessary processes for handling the dependencies for the A/V switch controller"""

    # noinspection SpellCheckingInspection
    def __init__(self):
        """Initializes a new _Installer class."""
        # The required dependencies.
        self.__dependencies = [
            "python3-numpy",
            "python3-serial",
            "python3-xdg",
            "python3-tk",
            "python3-pil",
            "python3-pil.imagetk",
        ]

        # The missing dependencies to install.
        self.__missing = []  # type: List[str]

        # Connect to the PackageKit session interface.
        bus = dbus.SessionBus()
        self.__name = dbus.service.BusName("org.sleepingscats.PiAvSwitchController", bus)
        kit = bus.get_object("org.freedesktop.PackageKit", "/org/freedesktop/PackageKit")

        # Get the package installation query method.
        query = dbus.Interface(kit, "org.freedesktop.PackageKit.Query")
        self.__is_installed_method = query.get_dbus_method("IsInstalled")

        # Get the package install method.
        modify = dbus.Interface(kit, "org.freedesktop.PackageKit.Modify")
        self.__install_method = modify.get_dbus_method("InstallPackageNames")

    def check(self) -> bool:
        """Determines whether any dependencies are missing."""
        for dependency in self.__dependencies:
            if not bool(self.__is_installed_method(dependency, "")):
                self.__missing.append(dependency)

        return len(self.__missing) > 0

    def install(self) -> None:
        """Installs any missing dependencies."""
        self.__install_method(0, self.__missing, "show-confirm-search,hide-finished", timeout=3600)


def install() -> None:
    """Checks for and installs any missing dependencies."""
    if State.current.version == State.current.last_setup_version:
        # No need to perform any setup.
        return

    log.info("Performing first time or update installation...")

    installer = _Installer()
    if installer.check():
        log.info("Installing required dependencies...")
        installer.install()
