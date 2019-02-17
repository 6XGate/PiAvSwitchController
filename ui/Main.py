import functools
import tkinter as tk

from typing import List, Dict, Union
from PIL import Image, ImageEnhance, ImageTk
from support.Device import devices, Device


class Colors:
    FRAME = "Black"
    BUTTON_NORMAL = "Dark Grey"
    BUTTON_SELECTED = "White"


class Main(tk.Tk):

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
        for device in devices:
            # Create the button.
            # noinspection SpellCheckingInspection
            button_config = {
                'borderwidth': 0,
                'highlightthickness': 0,
                'activebackground': Colors.BUTTON_NORMAL,
                'background': Colors.BUTTON_NORMAL
            }
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

            # Generate a partial to bind the command to the device.
            command = functools.partial(self.__select_device, button, device)

            # Add the new button.
            button.config(command=command)
            button.grid(column=column, row=row, sticky=(tk.N, tk.W))
            button.grid_configure(padx=1, pady=1)
            self.__buttons.append(button)

            # Move the column and row positions as necessary.
            column = column + 1
            if column == columns:
                row = row + 1
                column = 0

    def __select_device(self, button: tk.Button, device: Device):
        selected = self.__selected
        if selected:
            selected.config(activebackground=Colors.BUTTON_NORMAL, background=Colors.BUTTON_NORMAL)
            if selected in self.__normal_images:
                selected.config(image=self.__normal_images[selected])

        device.select()
        self.__selected = button
        button.config(activebackground=Colors.BUTTON_SELECTED, background=Colors.BUTTON_SELECTED)
        if button in self.__selected_images:
            button.config(image=self.__selected_images[button])

    def __idle_poll(self) -> None:
        self.after(500, self.__idle_poll)
