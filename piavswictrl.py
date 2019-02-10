#!/usr/bin/env python3

import sys

from support.Switch import load_switches
from support.Device import load_devices
from support.config import load_config
from ui.Main        import Main

__version__ = "0.0.0"

def main():
    config = load_config()
    load_switches(config['switches'])
    load_devices(config['devices'])

    root = Main()
    root.mainloop()

if __name__ == "__main__":
    main()
    sys.exit()
