from typing import Any, Dict
import logging

from .. import Driver, DriverRegistration
from ..validation import validate_arg
from .Extron import Extron
from .SonyMonitor import SonyBvmDSeries

log = logging.getLogger(__name__)


def register_drivers(*registry: DriverRegistration) -> Dict[str, DriverRegistration]:
    """
    Registers drivers.
    :param registry: The registration information for drivers to register.
    :return: The look-up registry.
    """
    return {registration.id: registration for registration in registry}


# Registered drivers.
drivers = register_drivers(
    Extron.register(),
    SonyBvmDSeries.register(),
)


def load_driver(switch_id: str, config: Dict[str, Any]) -> Driver:
    """
    Loads a driver for a specific switch.
    :param switch_id: The identifier of the switch, for error reporting.
    :param config:    The configuration of the switch.
    :return: The driver as specified in the switch configuration.
    """

    # Get the name of the driver.
    validate_arg('driver' in config, "Driver not specified for `{0}`".format(switch_id))
    name = str(config['driver'])

    # Now construct an instance of the driver for the switch.
    validate_arg(name in drivers, "Driver `{0}` does not exist".format(name))
    validate_arg('config' in config, "Switch configuration not specified for `{0}`".format(switch_id))

    # Get some basic information to log out.
    title = str(config['title'] if 'title' in config else switch_id)
    registration = drivers[name]
    log.info("Loading `{0}` for `{1}` as `{2}`".format(registration.title, title, switch_id))

    return registration.ctor(config['config'])
