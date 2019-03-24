from uuid import UUID

from .data import drivers


class DeviceDefinition:
    """Provides the necessary information to know about a device and its driver."""

    # The device can have a decoupled audio channel.
    HAS_DECOUPLED_AUDIO = 1 << 0
    # The device supports user controlled aspect ratio.
    HAS_MANUAL_ASPECT_RATIO = 1 << 1
    # The device supports user controlled overscan and underscan.
    HAS_MANUAL_OVERSCAN_AND_UNDERSCAN = 1 << 2

    def __init__(self, guid: str, driver_guid: str, title: str,
                 maximum_inputs: int, maximum_outputs: int = 0,
                 capabilities: int = 0):
        """
        Initializes a new device definition.
        :param guid:            The GUID for the device.
        :param driver_guid:     The GUID of the driver for the device.
        :param title:           The title of the device.
        :param maximum_inputs:  The maximum number of inputs the device provides.
        :param maximum_outputs: The maximum number of outputs the device provides, zero if it is a monitor.
        :param capabilities:    The capability flags for the device.
        """
        driver_uuid = UUID(driver_guid)
        if driver_uuid not in drivers:
            raise ValueError("No driver defined for {0}, using uuid:{1}".format(title, driver_guid))

        self.guid = UUID(guid)
        self.driver_guid = driver_uuid
        self.driver_definition = drivers[driver_uuid]
        self.title = title
        self.maximum_inputs = maximum_inputs
        self.maximum_outputs = maximum_outputs
        self.capabilities = capabilities
