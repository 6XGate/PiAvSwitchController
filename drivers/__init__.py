from typing import Dict, Callable, Any

from support import Driver
from support.validation import validate_arg
from .Extron import Extron
from .SonyMonitor import SonyBvmDSeries

# Registered drivers, a name mapped to a callable that will except the device configuration for the driver.
drivers = {
    'extron': lambda config: Extron(config),
    'sony-bvm-d': lambda config: SonyBvmDSeries(config)
}  # type: Dict[str, Callable[[Dict[str, Any]], Driver]]


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
    return drivers[name](config['config'])
