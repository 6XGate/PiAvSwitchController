from typing import List, Dict, Union, Callable
import os
import functools

import tkinter as tk
import numpy as np
from PIL import Image, ImageEnhance, ImageTk

from ..support.Device import devices, Device
from ..support.Switch import switches

ButtonTarget = Union[None, Device, Image.Image]


class Colors:
    FRAME = "Black"
    BUTTON_NORMAL = "Dark Grey"
    BUTTON_SELECTED = "White"


def shutdown_system():
    # noinspection SpellCheckingInspection
    os.system('sudo poweroff')


class Main(tk.Tk):
    """The main window."""

    def __init__(self):
        super().__init__()
        self.after_idle(self.__idle_poll)
        self.title('Pi Game Switch')
        self.attributes('-fullscreen', True)
        self.__normal_images = {}  # type: Dict[tk.Button, tk.PhotoImage]
        self.__selected_images = {}  # type: Dict[tk.Button, tk.PhotoImage]
        self.__buttons = []  # type: List[tk.Button]
        self.__frame = tk.Frame(self, cursor='none', background=Colors.FRAME)
        self.__selected = None  # type: Union[None, tk.Button]

        # Configure the layout
        self.__frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Get the number of columns we will have.
        columns = int(self.winfo_screenwidth() / 130)

        column = 0
        row = 0

        def selector(target: Device):
            target.select()

        for device in devices:
            # Create the command callback partial.
            command = functools.partial(selector, device)  # type: Callable[[], None]

            button = self.__make_button(command, device)
            button.grid(column=column, row=row, sticky=(tk.N, tk.W))
            button.grid_configure(padx=1, pady=1)

            self.__buttons.append(button)

            # Move the column and row positions as necessary.
            column = column + 1
            if column == columns:
                row = row + 1
                column = 0

        def power_off():
            for name, switch in switches.items():
                switch.power_off()
            shutdown_system()

        power_off_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './res/poweroff.png'))
        button = self.__make_button(power_off, Image.open(power_off_image_path))
        button.grid(column=column, row=row, sticky=(tk.N, tk.W))
        button.grid_configure(padx=1, pady=1)
        self.__buttons.append(button)

        def power_on():
            for name, switch in switches.items():
                switch.power_on()

        self.after_idle(power_on)

    def __activate_button(self, command: Callable[[], None], button: tk.Button):
        selected = self.__selected
        if selected:
            selected.config(activebackground=Colors.BUTTON_NORMAL, background=Colors.BUTTON_NORMAL)
            if selected in self.__normal_images:
                selected.config(image=self.__normal_images[selected])

        command()
        self.__selected = button
        button.config(activebackground=Colors.BUTTON_SELECTED, background=Colors.BUTTON_SELECTED)
        if button in self.__selected_images:
            button.config(image=self.__selected_images[button])

    def __idle_poll(self) -> None:
        self.after(500, self.__idle_poll)

    def __make_button(self, command: Callable[[tk.Button], None], target: ButtonTarget) -> tk.Button:
            # noinspection SpellCheckingInspection
            button_config = {
                'borderwidth': 0,
                'highlightthickness': 0,
                'activebackground': Colors.BUTTON_NORMAL,
                'background': Colors.BUTTON_NORMAL
            }

            if isinstance(target, Device):
                # Device button
                device = target
                if len(device.image) > 0:
                    # Get the selected image.
                    selected = ImageTk.PhotoImage(Image.open(device.image))
                    # Generate the normal image.
                    enhancer = ImageEnhance.Brightness(Image.open(device.image))
                    normal = ImageTk.PhotoImage(enhancer.enhance(0.66))

                    button = tk.Button(self.__frame, image=normal, **button_config)
                    self.__selected_images[button] = selected
                    self.__normal_images[button] = normal
                else:
                    text = device.title
                    button = tk.Button(self.__frame, text=text, **button_config)

                # Generate a partial to bind the button and command to __activate_button.
                bound_command = functools.partial(self.__activate_button, command, button)  # type: Callable[[], None]
                button.config(command=bound_command)
                return button
            elif isinstance(target, Image.Image):
                # Special button
                # Get the selected image.
                selected = ImageTk.PhotoImage(target)
                # Generate the normal image.
                enhancer = ImageEnhance.Brightness(Image.fromarray(np.asarray(target)))
                normal = ImageTk.PhotoImage(enhancer.enhance(0.66))

                button = tk.Button(self.__frame, image=normal, **button_config)
                self.__selected_images[button] = selected
                self.__normal_images[button] = normal

                # Generate a partial to bind the button and command to __activate_button.
                bound_command = functools.partial(self.__activate_button, command, button)  # type: Callable[[], None]
                button.config(command=bound_command)
                return button
