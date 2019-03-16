from typing import Dict, Any
import os
import io
import socket

import serial

from .. import Driver, DriverRegistration
from ..validation import validate_value


class TeslaSmart(Driver):
    """Tesla-Smart HDMI and SDI switch driver."""

    __SET_CHANNEL = b"\xAA\xBB\x03\x01%b\xEE"

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes a new instances of the Tesla-Smart driver.
        :param config:
        """
        super().__init__(config, 0)

        validate_value("maxInputs" in self.config, "Missing `maxInputs` for Tesla-Smart switch")
        validate_value("tty" in self.config or "host" in self.config, "Missing `tty` or `host` for Extron switch")

        if "tty" in self.config:
            tty_path = os.path.realpath(os.path.join(os.path.sep, "dev", self.config["tty"]))
            self.host = None
            self.serial = serial.Serial(tty_path, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
        else:  # "host" in self.config
            self.host = self.config["host"]
            self.serial = None

        self.max_inputs = int(self.config['maxInputs'])

    def __del__(self):
        """Cleans up an instance of the Tesla-Smart driver."""
        if self.serial is not None:
            self.serial.close()

    @staticmethod
    def register() -> DriverRegistration:
        """Registers the Tesla-Smart driver."""
        return DriverRegistration("tesla-smart", "Tesla-Smart", lambda config: TeslaSmart(config))

    def set_tie(self, input_channel: int, video_output_channel: int, audio_output_channel: int) -> None:
        """
        Sets input and output ties.
        :param input_channel:        The input channel of the tie.
        :param video_output_channel: The output video channel of the tie.
        :param audio_output_channel: The output audio channel of the tie.
        """
        validate_value(1 <= input_channel <= self.max_inputs, "Input channel is out of range")
        validate_value(video_output_channel == 0, 'Video output channel is out of range')
        validate_value(audio_output_channel == 0, 'Audio output channel is out of range')

        self.__send_command(TeslaSmart.__SET_CHANNEL % input_channel.to_bytes(1, "big", signed=False))

    def __send_command(self, command: bytes) -> None:
        """
        Sends a command to the switch.
        :param command: The command to send.
        """
        if self.serial is not None:
            # Send the command to the serial connection.
            self.serial.write(command)
            self.serial.reset_input_buffer()
        else:
            # Open a network connection and send the command.
            with socket.create_connection((self.host, 5000)) as connection:
                with connection.makefile(mode='wb') as stream:  # type: io.BufferedWriter
                    stream.write(command)
                    stream.flush()
