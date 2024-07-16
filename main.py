import tkinter as tk
import math

from tkinter import filedialog
from PIL import ImageTk, Image

# key dimensions
window_width = 1000
window_height = 700
canvas_width = 820
canvas_height = 620
canvas_padx = 10
canvas_pady = 10


class WaterMarker():
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("💧MarkIt.")
        self.window.minsize(width=window_width, height=window_height)

        block_image = tk.LabelFrame(self.window, bg="brown")
        block_image.config()
        block_image.pack()

        # TODO: make this into a function bind with a button
        image_pil = Image.open('grey_box.png')
        image_resize = image_pil.resize(self.resize_image(image_pil.width, image_pil.height))
        self.image = ImageTk.PhotoImage(image_resize)
        
        self.image_datum_x = math.floor((canvas_width - self.image.width()) / 2)
        self.image_datum_y = math.floor((canvas_height - self.image.height()) / 2)

        self.canvas = tk.Canvas(block_image, bg='white', width=canvas_width, height=canvas_height)
        self.canvas.create_image(self.image_datum_x, self.image_datum_y, image=self.image, anchor='nw')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.clicked_canvas)
        self.canvas.bind("<Motion>", self.hover_canvas)
    
    # key functions
    def resize_image(self, width:int, height:int): # TODO: rename this.
        ratio:float =  min((canvas_width - canvas_padx * 2) / width, (canvas_height - canvas_pady * 2) / height) 
        size:tuple[int, int] = math.floor(width * ratio * 0.99), math.floor(height * ratio * 0.99)
        # size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def operate(self):
        self.window.mainloop()
        
    # mouse location functions
    def clicked_canvas(self, event):
        # set opaque watermark at clicked location
        x, y = event.x, event.y
        print(f"\nclicked at: x:{x}, y:{y} in canvas.")
        mouse_loc = self.mouse_loc_calibrate(x, y)
        x0, y0 = mouse_loc
        x1, y1 = mouse_loc
        self.canvas.create_oval(x0, y0, x1, y1, fill='blue')
        
        # TODO: add code: color a pixel at clicked location.

    def hover_canvas(self, event):
        # set translucent watermark at hover location
        x, y = event.x, event.y
        msg = f"hover over: x:{x}, y:{y} in canvas."
        print(msg, end='')
        print('\b' * len(msg), end='', flush=True)

    # temp functions
    def mouse_loc_calibrate(self, x:int, y:int):
        x_min = self.image_datum_x
        y_min = self.image_datum_y
        x_max = self.image_datum_x + self.image.width()
        y_max = self.image_datum_y + self.image.height()
        if x_max > x > x_min and y_max > y > y_min:
            mouse_loc = x, y
        elif x <= x_min and y <= y_min:
            mouse_loc = x_min, y_min
        elif x >= x_max and y <= y_min:
            mouse_loc = x_max, y_min
        elif x <= x_min and y >= y_max:
            mouse_loc = x_min, y_max
        elif x > x_max and y >= y_max:
            mouse_loc = x_max, y_max
        elif x_max >= x >= x_min and y <= y_min:
            mouse_loc = x, y_min
        elif x <= x_min and y_max >= y >= y_min:
            mouse_loc = x_min, y
        elif x_max >= x >= x_min and y >= y_max:
            mouse_loc = x, y_max
        elif x >= x_max and y_max >= y >= y_min:
            mouse_loc = x_max, y
        else:
            raise ValueError(f"not in elif tree? '{x}, {y}', ")
        return mouse_loc

        
    def cal_mark_loc(self, mark_size:tuple[int, int], image_size:tuple[int, int], mouse_loc:tuple[int, int]):
        mark_width, mark_height = mark_size
        image_width, image_height = image_size
        x, y = mouse_loc
    
wm = WaterMarker()
wm.operate()