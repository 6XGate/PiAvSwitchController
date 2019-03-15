import signal

import dbus

from .support.Switch import load_switches
from .support.Device import load_devices
from .support.config import load_config
from .ui.Main import Main

root = None  # type: Main


# noinspection PyUnusedLocal
def on_quit(signum: int, frame) -> None:
    root.destroy()


def main() -> None:
    global root

    config = load_config()
    load_switches(config['switches'])
    load_devices(config['devices'])

    signal.signal(signal.SIGTERM, on_quit)

    root = Main()
    root.mainloop()


# noinspection SpellCheckingInspection
def shutdown() -> None:
    bus = dbus.SystemBus()
    kit = bus.get_object("org.freedesktop.login1", "/org/freedesktop/login1")
    manager = dbus.Interface(kit, "org.freedesktop.login1.Manager")
    manager.PowerOff(False)
