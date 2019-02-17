import io
from typing import Union
from enum import IntEnum
from serial import Serial
from .errors import *

# Sony BVM D-series RS-485 Serial Protocol (Current Understanding)
#
# This driver is based on the current understanding of the protocol from observation of the remote output.  This may not
# be entirely correct and will be missing other information.  Since the packet format vaguely mimics the 9-pin protocol,
# the packet types use those names.
#
# Packet Format
# - Byte 1:        Packet type
# - Byte 2:        Packet size (N)
# - Byte 3 to N-1: Packet data (D)
# - Byte 3+N:      Packet checksum; ~(sum(D)) - (N - 1)
#
# Command-block Format
# - Byte 1:    Destination address
# - Byte 2:    Source address
# - Byte 3..4: Command
# - Byte 5:    Arg zero
# - Byte 6:    Arg one
#
# Address Format
# - Bits 7..5: Address kind
#   - C - All connected monitors, the address number should be zero.
#   - 8 - A monitor group, the address number should be the group number.
#   - 0 - A single monitor, the address number should be the monitor number.
# - Bits 4..0: Address number


class PacketType(IntEnum):
    """Identifies the type of a packet."""

    TRANSPORT_CONTROL = 2  # A simple data packet.


class Packet:
    """Represents a data packet that encapsulates the command blocks."""

    def __init__(self, packet_type: PacketType, packet_data: bytes, packet_size: int = -1, checksum: int = -1):
        """
        Initializes a new instance of the Packet class.
        :param packet_type: The type of the packet.
        :param packet_data: The data of the packet.
        :param packet_size: If being parsed, the size of the packet to be confirmed.
        :param checksum:    If being parsed, the checksum of the packet to be confirmed.
        """
        # If parsing a packet, ensure the size matches.
        if packet_size >= 0 and packet_size != len(packet_data):
            raise PacketError()

        self.type = packet_type
        self.data = packet_data

        # If parsing a packet, ensure the checksum is valid.
        if checksum >= 0:
            expected_checksum = self.__calculate_checksum()
            if expected_checksum != checksum:
                raise ChecksumError()

    @classmethod
    def read(cls, connection: Union[io.BufferedIOBase, Serial]):
        """
        Reads and parses the next packet from a connection.
        :param connection: The connection from which to read packets.
        :return: The parsed packet.
        :rtype:  Packet
        """
        packet_type = connection.read(1)
        if len(packet_type) == 0:
            raise PacketError()

        packet_size = connection.read(1)
        if len(packet_size) == 0:
            raise PacketError()

        packet_data = connection.read(packet_size[0])

        checksum = connection.read(1)
        if len(checksum) == 0:
            raise PacketError()

        return Packet(PacketType(packet_type[0]), packet_data, packet_size[0], checksum[0])

    def write(self, connection: Union[io.BufferedIOBase, Serial]) -> None:
        """
        Writes a packet to a connection.
        :param connection: The connection to which to write the packet.
        """
        checksum = self.__calculate_checksum()
        size = len(self.data)

        connection.write(self.type.to_bytes(1, byteorder='big', signed=False))
        connection.write(size.to_bytes(1, byteorder='big', signed=False))
        connection.write(self.data)
        connection.write(checksum.to_bytes(1, byteorder='big', signed=False))

    def __calculate_checksum(self) -> int:
        """
        Calculates the checksum for a packet.
        :return: The packet checksum.
        """
        # Sum all bytes.
        x = 0
        for byte in self.data:
            x = x + byte

        # Take only the eight least significant bytes of the two's compliment, and subtract the size, less one byte.
        x = ~x & 0xFF
        x = x - (len(self.data) - 1)

        return x


class AddressKind(IntEnum):
    """Identifies the kind of address being used."""

    ALL = 0xC0      # All monitors are being addressed.
    GROUP = 0x80    # A group of monitors is addressed.
    MONITOR = 0x00  # Only a single monitor is addressed.


class Address:
    """Identifies the source or destination of a command block."""

    def __init__(self, kind: AddressKind, address: int):
        """
        Creates a new instance of the Address class.
        :param kind:    The kind of address being specified.
        :param address: The address value.
        """
        self.kind = kind
        self.address = address

    @classmethod
    def read(cls, address: int):
        """
        Parses a raw address value.
        :param address: The raw address value.=
        :rtype:  Address
        :return: An Address from the raw value.
        """
        return Address(AddressKind(address & 0xE0), address & 0x1F)

    def package(self) -> int:
        """
        Creates the raw address value.
        :return: Returns the raw address value.
        """
        return self.kind.value | self.address


class Command(IntEnum):
    """Identifies the command being send or received."""

    SET_CHANNEL = 0x2100  # Sets the channel
    POWER_ON = 0x293E     # Powers on the monitor
    BUTTON = 0x3F44       # Emits a control module button


class CommandBlock:
    """Represents a command block."""

    def __init__(self, destination: Address, source: Address, command: Command, arg0: int = -1, arg1: int = -1):
        """
        Initializes a new instance of the CommandBlock class.
        :param destination: The destination address.
        :param source:      The source address.
        :param command:     The command.
        :param arg0:        The first argument of the command, if applicable.
        :param arg1:        The second argument of the command, if applicable.
        """
        self.destination = destination
        self.source = source
        self.command = command
        self.arg0 = arg0
        self.arg1 = arg1

    @classmethod
    def read(cls, packet: Packet):
        """
        Parses the command block from a packet.
        :param packet: A packet containing a command block.
        :return: The parsed command block.
        :rtype:  CommandBlock
        """
        stream = io.BytesIO(packet.data)

        destination = stream.read(1)
        if len(destination) == 0:
            raise CommandBlockError()

        source = stream.read(1)
        if len(source) == 0:
            raise CommandBlockError()

        command = stream.read(2)
        if len(command) != 2:
            raise CommandBlockError()

        destination_address = Address.read(destination[0])
        source_address = Address.read(source[0])
        command_id = Command(int.from_bytes(command, byteorder='big', signed=False))

        arg0 = stream.read(1)
        if len(arg0) == 0:
            return CommandBlock(destination_address, source_address, command_id)

        arg1 = stream.read(1)
        if len(arg1) == 0:
            return CommandBlock(destination_address, source_address, command_id, arg0[0])

        return CommandBlock(destination_address, source_address, command_id, arg0[0], arg1[0])

    def package(self) -> Packet:
        """
        Creates a packet for the command block.
        :return:
        """
        stream = io.BytesIO()
        stream.write(self.destination.package().to_bytes(1, byteorder='big', signed=False))  # Destination address
        stream.write(self.source.package().to_bytes(1, byteorder='big', signed=False))       # Source address
        stream.write(self.command.value.to_bytes(2, byteorder='big', signed=False))          # Command
        if self.arg0 >= 0:
            stream.write(self.arg0.to_bytes(1, byteorder='big', signed=False))               # Argument zero
            if self.arg1 >= 0:
                stream.write(self.arg1.to_bytes(1, byteorder='big', signed=False))           # Argument one

        data = stream.getbuffer().tobytes()
        return Packet(PacketType.TRANSPORT_CONTROL, data)
