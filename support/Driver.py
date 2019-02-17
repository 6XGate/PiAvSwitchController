from typing import Dict, Any


class Driver:
    """Represents the traits and functionality of a switch driver."""

    HAS_MULTIPLE_OUTPUTS = 1 << 0       # The switch has multiple outputs.
    CAN_DECOUPLE_AUDIO_OUTPUT = 1 << 1  # The switch can have separate output channels for audio and video.

    def __init__(self, config: Dict[str, Any], capabilities: int):
        """
        Initializes a new instance of the Driver class.
        :param config:       The device configuration for the driver.
        :param capabilities: The capabilities of the driver.
        """
        self.config = config
        self.capabilities = capabilities

    def set_tie(self, input_channel: int, video_output_channel: int, audio_output_channel: int) -> None:
        """
        Sets input and output ties.
        :param input_channel:        The input channel of the tie.
        :param video_output_channel: The output video channel of the tie.
        :param audio_output_channel: The output audio channel of the tie.
        """
        pass
