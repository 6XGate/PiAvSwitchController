from typing             import Dict, Any
from serial             import Serial
from support            import Driver
from support.validation import validate_arg

class Extron(Driver):
    """Extron SIS Driver for Extron matrix switches using RS-232 mode."""

    __TIE_VIDEO = "{0}*{1}%"
    __TIE_AUDIO = "{0}*{1}$"

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes a new instances of the Extron driver.
        :param config: The configuration data from the configuration about the device.
        """

        super().__init__(config, Driver.CAN_DECOUPLE_AUDIO_OUTPUT)

        validate_arg('maxInputs'  in self.config, 'Missing `maxInputs` for Extron switch')
        validate_arg('maxOutputs' in self.config, 'Missing `maxOutputs` for Extron switch')
        validate_arg('tty'        in self.config, 'Missing `tty` for Extron switch')

        self.max_inputs  = int(self.config['maxInputs'])
        self.max_outputs = int(self.config['maxOutputs'])
        self.tty         = str(config['tty'])
        self.serial      = Serial("/dev/{}".format(self.tty))

        if self.max_outputs > 1:
            self.capabilities = int(self.capabilities | Driver.HAS_MULTIPLE_OUTPUTS)

    def __del__(self):
        """Cleans up an instance of the Extron driver."""
        if isinstance(self.serial, Serial):
            self.serial.close()

    def set_tie(self, input_channel: int, video_output_channel: int, audio_output_channel: int) -> None:
        """
        Sets input and output ties.
        :param input_channel:        The input channel of the tie.
        :param video_output_channel: The output video channel of the tie.
        :param audio_output_channel: The output audio channel of the tie.
        """
        validate_arg(1 <= input_channel <= self.max_inputs,         'Input channel is out of range')
        validate_arg(1 <= video_output_channel <= self.max_outputs, 'Video output channel is out of range')
        validate_arg(1 <= audio_output_channel <= self.max_outputs, 'Audio output channel is out of range')

        self.__send_command(Extron.__TIE_VIDEO.format(input_channel, video_output_channel))
        self.__send_command(Extron.__TIE_AUDIO.format(input_channel, audio_output_channel))

    def __send_command(self, command: str) -> None:
        """
        Sends a command to the switch.
        :param command: The command to send.
        """
        self.serial.write(command.encode())
        self.serial.reset_input_buffer()
