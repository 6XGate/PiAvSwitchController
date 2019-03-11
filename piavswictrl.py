#!/usr/bin/python3
import sys
import logging

import dbus

from state import State

__version__ = "0.6.0"


def _do_install() -> None:
    import installer

    installer.install()


def _do_setup() -> None:
    import setup

    setup.perform()


def _run_app() -> int:
    import app

    return app.main()


def _main() -> int:
    with State():
        logging.info("Starting A/V Switch Controller {}".format(__version__))

        # Perform any installation tasks that might be required.
        try:
            _do_install()
        except dbus.exceptions.DBusException as e:
            logging.error("Failed to install dependencies")
            logging.exception(e)
            return 1
        except Exception as e:
            logging.error("Failed to install dependencies")
            logging.exception(e)
            return 1

        try:
            _do_setup()
        except Exception as e:
            logging.exception(e)
            return 1

        try:
            return _run_app()
        except Exception as e:
            logging.exception(e)
            return 1


if __name__ == "__main__":
    sys.exit(_main())
