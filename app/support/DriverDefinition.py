from typing import Callable

from uuid import UUID

from . import Driver


class DriverDefinition:
    """Defines information about the driver."""

    # The device uses a TCP/IP or character device stream.
    USES_STREAMS = 1

    def __init__(self, guid: str, title: str, factory: Callable[[], Driver], flags: int = 0):
        """
        Initializes a new driver definition.
        :param guid:    The GUID for the driver.
        :param title:   The title of the driver.
        :param factory: The factory for the driver.
        :param flags:   The information flags for the driver.
        """
        self.guid = UUID(guid)
        self.title = title
        self.factory = factory
        self.flags = flags
