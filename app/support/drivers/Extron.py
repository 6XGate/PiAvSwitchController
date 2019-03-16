from typing import Dict, Any
import os
import io
import socket

import serial

from .. import Driver, DriverRegistration
from ..validation import validate_value


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

        validate_value("maxInputs" in self.config, "Missing `maxInputs` for Extron switch")
        validate_value("maxOutputs" in self.config, "Missing `maxOutputs` for Extron switch")
        validate_value("tty" in self.config or "host" in self.config, "Missing `tty` or `host` for Extron switch")

        self.max_inputs = int(self.config["maxInputs"])
        self.max_outputs = int(self.config["maxOutputs"])
        if "tty" in self.config:
            tty_path = os.path.realpath(os.path.join(os.path.sep, "dev", self.config["tty"]))
            self.host = None
            self.serial = serial.Serial(tty_path, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
        else:
            self.host = self.config["host"]
            self.serial = None

        if self.max_outputs > 1:
            self.capabilities = int(self.capabilities | Driver.HAS_MULTIPLE_OUTPUTS)

    def __del__(self):
        """Cleans up an instance of the Extron driver."""
        if self.serial is not None:
            self.serial.close()

    @staticmethod
    def register() -> DriverRegistration:
        """Registers the Extron SIS driver."""
        return DriverRegistration("extron", "Extron SIS", lambda config: Extron(config))

    def set_tie(self, input_channel: int, video_output_channel: int, audio_output_channel: int) -> None:
        """
        Sets input and output ties.
        :param input_channel:        The input channel of the tie.
        :param video_output_channel: The output video channel of the tie.
        :param audio_output_channel: The output audio channel of the tie.
        """
        validate_value(1 <= input_channel <= self.max_inputs, "Input channel is out of range")
        validate_value(1 <= video_output_channel <= self.max_outputs, "Video output channel is out of range")
        validate_value(1 <= audio_output_channel <= self.max_outputs, "Audio output channel is out of range")

        command = "{0}\r\n{1}".format(
            Extron.__TIE_VIDEO.format(input_channel, video_output_channel),
            Extron.__TIE_AUDIO.format(input_channel, audio_output_channel)
        )

        self.__send_command(command)

    def __send_command(self, command: str) -> None:
        """
        Sends a command to the switch.
        :param command: The command to send.
        """
        if self.serial is not None:
            # Send the command to the serial connection.
            self.serial.write(command.encode())
            self.serial.reset_input_buffer()
        else:
            # Open a network connection and send the command.
            with socket.create_connection((self.host, 23)) as connection:
                with connection.makefile(mode='wb') as stream:  # type: io.BufferedWriter
                    stream.write(command.encode())
                    stream.flush()
