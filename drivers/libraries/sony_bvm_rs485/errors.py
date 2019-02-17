class SonyDriverError(Exception):
    pass


class PacketError(SonyDriverError):
    pass


class ChecksumError(SonyDriverError):
    pass


class CommandBlockError(SonyDriverError):
    pass
