from typing import Dict, Any

from .validation import validate_arg
from .drivers import load_driver


class Switch:
    """Represents a switching device."""

    def __init__(self, switch_id: str, config: Dict[str, Any]):
        """
        Initializes a new instance of the Switch class.
        :param switch_id: The identifier used when referencing the switch.
        :param config:    The device configuration.
        """
        validate_arg(len(switch_id) > 0, 'Switch ID cannot be empty')
        validate_arg(isinstance(config['config'], dict),
                     "Configuration block for `{0}` is not an object".format(switch_id))

        self.id = switch_id
        self.title = str(config['title'] if 'title' in config else switch_id)
        self.driver = load_driver(switch_id, config)

    def set_tie(self, input_channel: int, video_output_channel: int, audio_output_channel: int) -> None:
        """
        Sets input and output ties.
        :param input_channel:        The input channel of the tie.
        :param video_output_channel: The output video channel of the tie.
        :param audio_output_channel: The output audio channel of the tie.
        """
        self.driver.set_tie(input_channel, video_output_channel, audio_output_channel)

    def power_on(self) -> None:
        """Powers on the switch or monitor."""
        self.driver.power_on()

    def power_off(self) -> None:
        """Powers off the switch or monitor."""
        self.driver.power_off()


# The loaded switches.
switches = {}  # type: Dict[str, Switch]


def load_switches(config: Dict[str, Dict[str, Any]]) -> None:
    """
    Loads all the switches from the configuration.
    :param config: The switch section of the configuration data.
    """
    for switch_id, switch_config in config.items():
        switches[switch_id] = Switch(switch_id, switch_config)
