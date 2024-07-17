import tkinter as tk
import math

from tkinter import filedialog
from PIL import ImageTk, Image

# key dimensions
window_width = 1000
window_height = 700
canvas_width = 860
canvas_height = 660
canvas_padx = 30
canvas_pady = 30
mark_width = 50
mark_height = 50



class WaterMarker():
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("💧MarkIt.")
        self.window.minsize(width=window_width, height=window_height)
        self.window.resizable(width=False, height=False)

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
        
        # TODO: make this into a function bind with a button
        mark_pil = Image.open('watermark.png')
        mark_resize = mark_pil.resize(self.resize_mark(image_pil.width, image_pil.height))
        self.mark = ImageTk.PhotoImage(mark_resize)
        self.watermark_lbl = tk.Label(self.canvas, image=self.mark) # type: ignore
        self.watermark_lbl.config(border=0)
    
    # key functions
    def operate(self):
        self.window.mainloop()
        
    def resize_image(self, width:int, height:int): # TODO: rename this.
        ratio:float =  min((canvas_width - canvas_padx * 2) / width, (canvas_height - canvas_pady * 2) / height) 
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def resize_mark(self, width:int, height:int):
        ratio:float =  min(mark_width/width, mark_height/height) 
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    # mouse location functions
    def clicked_canvas(self, event):
        # set opaque watermark at clicked location
        x, y = event.x, event.y
        print(f"\nclicked at: x:{x}, y:{y} in canvas.")
        mouse_loc = self.mouse_loc_calibrate(x, y)
        # x0, y0 = mouse_loc
        # x1, y1 = mouse_loc
        # self.canvas.create_oval(x0, y0, x1, y1, fill='blue')
        
        
        
        x = mouse_loc[0] - math.floor(self.mark.width() / 2) #+ math.floor((window_width - canvas_width) / 2)
        y = mouse_loc[1] - math.floor(self.mark.height() / 2)
        print(f"placed mark at x:{x}, y:{y}")
        self.watermark_lbl.place(x=x, y=y)


    def hover_canvas(self, event):
        # set translucent watermark at hover location
        x, y = event.x, event.y
        msg = f"hover over: x:{x}, y:{y} in canvas."
        print(msg, end='')
        print('\b' * len(msg), end='', flush=True)

    # temp functions
    def mouse_loc_calibrate(self, x:int, y:int):
        x_min = self.image_datum_x + self.mark.width() / 2
        y_min = self.image_datum_y + self.mark.height() / 2
        x_max = self.image_datum_x + self.image.width() - self.mark.width() / 2
        y_max = self.image_datum_y + self.image.height() - self.mark.height() / 2
        if x_max >= x >= x_min and y_max >= y >= y_min: # in image
            mouse_loc = x, y
        elif x <= x_min and y <= y_min: # top left corner
            mouse_loc = x_min, y_min
        elif x >= x_max and y <= y_min: # top right corner
            mouse_loc = x_max, y_min
        elif x <= x_min and y >= y_max: # btm left corner
            mouse_loc = x_min, y_max
        elif x >= x_max and y >= y_max: # btm right corner
            mouse_loc = x_max, y_max
        elif x_max >= x >= x_min and y <= y_min: # top border
            mouse_loc = x, y_min
        elif x_max >= x >= x_min and y >= y_max: # btm border
            mouse_loc = x, y_max
        elif x <= x_min and y_max >= y >= y_min: # left border
            mouse_loc = x_min, y
        elif x >= x_max and y_max >= y >= y_min: # right border
            mouse_loc = x_max, y
        else:
            raise ValueError(f"mind blown, clicked at (x:{x}, y:{y}), not in elif tree?\n\
                image size: ({self.image.width()}x{self.image.height()})\n\
                datum at (x:{self.image_datum_x}, y:{self.image_datum_y})\n\
                x min max: {x_min}, {x_max}\n\
                y min max: {y_min}, {y_max}\n\
                never thought this will occur, add any missed info to mouse_loc_calibrate().")
        return mouse_loc

        
    def cal_mark_loc(self, mark_size:tuple[int, int], image_size:tuple[int, int], mouse_loc:tuple[int, int]):
        mark_width, mark_height = mark_size
        image_width, image_height = image_size
        x, y = mouse_loc
    
wm = WaterMarker()
wm.operate()