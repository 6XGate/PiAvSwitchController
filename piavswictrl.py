#!/usr/bin/python3
import sys

import dbus

from state import State

__version__ = "0.4.0"


def do_install() -> None:
    import installer

    installer.install()


def do_setup() -> None:
    import setup

    setup.perform()


def run_app() -> int:
    import app

    return app.main()


def main() -> int:
    with State():
        # Perform any installation tasks that might be required.
        try:
            do_install()
        except dbus.exceptions.DBusException as e:
            print("Failed to install dependencies: {}".format(e.get_dbus_message()))
            return 1
        except Exception as e:
            print("Failed to install dependencies: {}".format(e))
            return 1

        try:
            do_setup()
        except Exception as e:
            print(e)
            return 1

        return run_app()


if __name__ == "__main__":
    sys.exit(main())
