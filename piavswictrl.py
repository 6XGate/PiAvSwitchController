#!/usr/bin/env python3

import sys
import signal

from support.Switch import load_switches
from support.Device import load_devices
from support.config import load_config
from ui.Main        import Main

__version__ = "0.2.0"

root = None # type: Main

# noinspection PyUnusedLocal
def on_quit(signum: int, frame) -> None:
    root.destroy()

def main():
    global root

    config = load_config()
    load_switches(config['switches'])
    load_devices(config['devices'])

    signal.signal(signal.SIGTERM, on_quit)

    root = Main()
    root.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(main())
