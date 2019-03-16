from typing import Dict, Union

from .validation import validate_value
from . import Switch, Driver
from .Switch import switches

# A tie channel may be a single channel for input and output, or a video and audio channel for output.
TieChannel = Union[int, Dict[str, int]]
TieConfig = Dict[str, TieChannel]

# A hard output channel set.
TieOutput = Dict[str, int]


class Tie:
    """Represents a channel tie for input and output."""

    def __init__(self, switch_id: str, config: TieConfig):
        """
        Initializes a new instance of the Tie class.
        :param switch_id: The switch identifier for error reporting.
        :param config:    The tie configuration for the switch and a device.
        """
        validate_value(len(switch_id) > 0, 'Switch ID may not be empty')
        validate_value(switch_id in switches, "No such switch `{0}`".format(switch_id))
        validate_value('input' in config, "No input specified for `{0}`".format(switch_id))

        self.switch = switches[switch_id]  # type: Switch
        self.input = int(config['input'])
        self.output = {"video": 0, "audio": 0}  # type: TieOutput
        if self.switch.driver.capabilities & Driver.HAS_MULTIPLE_OUTPUTS:
            validate_value('output' in config, "No output specified for `{0}`".format(switch_id))
            output = config['output']  # type: TieChannel
            if isinstance(output, dict):
                validate_value(self.switch.driver.capabilities & Driver.CAN_DECOUPLE_AUDIO_OUTPUT,
                               "Separate audio and video given for `{0}`, which does not support decoupling".format(
                                   switch_id))
                validate_value('video' in output,
                               "Missing `video` channel on decoupled output for `{0}`".format(switch_id))
                validate_value('audio' in output,
                               "Missing `audio` channel on decoupled output for `{0}`".format(switch_id))
                self.output = output
            elif isinstance(output, int):
                self.output = {"video": output, "audio": output}
