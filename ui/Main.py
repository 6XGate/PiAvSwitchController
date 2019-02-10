import functools
import tkinter as tk
from tkinter        import ttk
from PIL            import Image, ImageTk
from support.Device import devices, Device

def select_input(device: Device):
    device.select()

class Main(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Pi Game Switch')
        self.attributes('-fullscreen', True)

        # Get the number of columns and rows we will have.
        columns = int(self.winfo_screenwidth() / 128) - 1
        rows    = int(self.winfo_screenheight() / 128) - 1

        # Configure the layout
        self.__frame = ttk.Frame(self)
        self.__frame.grid(columns=columns, rows=rows, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.__buttons = []
        self.__images  = []

        column = 0
        row    = 0
        for device in devices:
            command = functools.partial(select_input, device)
            if len(device.image) > 0:
                image = ImageTk.PhotoImage(Image.open(device.image))
                self.__images.append(image)
                button = ttk.Button(self.__frame, image=image, command=command)
                button.grid(column=column, row=row, sticky=(tk.N, tk.W))
                self.__buttons.append(button)
            else:
                text   = device.title
                button = ttk.Button(self.__frame, text=text, command=command)
                button.grid(column=column, row=row, sticky=(tk.N, tk.W))
                self.__buttons.append(button)

            column = column + 1
            if column == columns:
                row    = row + 1
                column = 0
