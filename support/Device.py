from typing import Dict, Any, Union, List
from .Tie import Tie
from .config import get_config_path
from .validation import validate_arg

# A tie channel may be a single channel for input and output, or a video and audio channel for output.
TieChannel = Union[int, Dict[str, int]]
TieConfig = Dict[str, TieChannel]


class Device:
    """Represents an input device."""

    def __init__(self, device_index: int, config: dict):
        """
        Initializes a new instance of the Device class.
        :param device_index: The device index for error reporting.
        :param config:       The device configuration such as channel ties.
        """
        validate_arg('ties' in config, "Configuration for `{0}` missing `ties`".format(device_index))
        validate_arg(isinstance(config['ties'], dict), "Ties for `{0}` is not an object".format(device_index))

        self.id = device_index
        self.title = str(config['title'] if 'title' in config else device_index)
        self.image = str(get_config_path(config['image']) if 'image' in config else '')
        self.ties = []  # type: List[Tie]

        self.__load_tie(config['ties'])

    def select(self) -> None:
        """Connect channel ties to select the device."""
        for tie in self.ties:
            tie.switch.set_tie(tie.input, tie.output['video'], tie.output['audio'])

    def __load_tie(self, switch_ties: Dict[str, TieConfig]) -> None:
        """
        Loads the ties for a switch.
        :param switch_ties: The tie configuration.
        """
        for switch_id, tie_config in switch_ties.items():
            self.ties.append(Tie(switch_id, tie_config))


# The loaded devices.
devices = []  # type: List[Device]


def load_devices(config: List[Dict[str, Any]]) -> None:
    """
    Loads the devices from the configuration data.
    :param config: The device configuration data.
    """
    index = 0
    for device_config in config:
        devices.append(Device(index, device_config))
        index = index + 1
