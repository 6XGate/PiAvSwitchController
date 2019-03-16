#!/usr/bin/python3
import sys
import logging

import dbus

from state import State

__version__ = "0.7.0"


def _do_install() -> None:
    """Installs any necessary dependencies."""
    import installer

    installer.install()


def _do_setup() -> None:
    """Performs any necessary setup tasks."""
    import setup

    setup.perform()


def _run_app() -> None:
    """Runs the application."""
    import app

    app.main()


def _may_shut_down() -> None:
    """Will shutdown the system if the user requested."""
    import app

    if State.current.shutting_down:
        app.shutdown()


def _main() -> int:
    """The main entry point for the application."""
    with State():
        logging.info("Starting A/V Switch Controller {}".format(__version__))
        logging.info("Last version `{0}` using configuration from `{1}`".format(
            State.current.last_setup_version, State.current.config_file_path))

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
            _run_app()
        except Exception as e:
            logging.exception(e)
            return 1

    logging.info('Clean exit')
    try:
        _may_shut_down()
    except Exception as e:
        logging.exception(e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(_main())
