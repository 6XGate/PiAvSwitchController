from typing import Dict, Any
import os

import serial

from .. import Driver, DriverRegistration
from ..validation import validate_value
from .libraries.sony_bvm_rs485.protocol import AddressKind, Address, Command, CommandBlock


class SonyBvmDSeries(Driver):
    """Sony BVM D-series Monitor Driver"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes a new instance of the Sony BVM D-series monitor driver.
        :param config:   The device configuration.
        """
        super().__init__(config, 0)

        validate_value("tty" in self.config, "Missing `tty` for Sony D-series monitor")

        tty_path = os.path.realpath(os.path.join(os.path.sep, "dev", self.config["tty"]))
        self.serial = serial.Serial(tty_path, 38400, serial.EIGHTBITS, serial.PARITY_ODD, serial.STOPBITS_ONE)

    def __del__(self):
        """Cleans up an instance of the Sony BVM D-series monitor driver."""
        self.serial.close()

    @staticmethod
    def register() -> DriverRegistration:
        """Registers the Sony BVD-D series driver."""
        return DriverRegistration("sony-bvm-d", "Sony BVM-D series", lambda config: SonyBvmDSeries(config))

    def set_tie(self, input_channel: int, video_output_channel: int, audio_output_channel: int) -> None:
        """
        Sets input and output ties.
        :param input_channel:        The input channel of the tie.
        :param video_output_channel: The output video channel of the tie.
        :param audio_output_channel: The output audio channel of the tie.
        """
        validate_value(1 <= input_channel <= 99, "Input channel is out of range")
        validate_value(video_output_channel == 0, "Video output channel is out of range")
        validate_value(audio_output_channel == 0, "Audio output channel is out of range")

        # Not sure why, but all channel sets have 1 as their first argument.
        self.__send_command(Command.SET_CHANNEL, 1, input_channel)

    def power_on(self) -> None:
        """Powers on the monitor."""
        self.__send_command(Command.POWER_ON)

    def power_off(self) -> None:
        """Powers off the monitor."""
        self.__send_command(Command.POWER_OFF)

    def __send_command(self, command: Command, arg0: int = -1, arg1: int = -1) -> None:
        """
        Sends a command to the monitor.
        :param command: The command to send.
        :param arg0:    The first argument of the command.
        :param arg1:    The second argument of the command.
        """
        source = Address(AddressKind.ALL, 0)
        destination = Address(AddressKind.ALL, 0)

        command = CommandBlock(destination, source, command, arg0, arg1)
        packet = command.package()

        packet.write(self.serial)
