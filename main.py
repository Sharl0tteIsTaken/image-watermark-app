import tkinter as tk
import math

from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw

# default key dimensions
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
        image_resize = image_pil.resize(self.size_calculate(image_pil.width, image_pil.height, type='image'))
        self.image = ImageTk.PhotoImage(image_resize)
        
        self.image_datum_x = math.floor((canvas_width - self.image.width()) / 2)
        self.image_datum_y = math.floor((canvas_height - self.image.height()) / 2)
        
        self.canvas = tk.Canvas(block_image, bg='white', width=canvas_width, height=canvas_height, border=0)
        self.canvas.create_image(self.image_datum_x, self.image_datum_y, image=self.image, anchor='nw')
        self.canvas.pack()

        self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
        self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
        self.canvas.focus_set()
        
        # TODO: make this into a function: load_image() -> watermark_in_canvas() bind with a button
        mark_pil = Image.open('watermark.png')
        mark_resize = mark_pil.resize(self.size_calculate(mark_pil.width, mark_pil.height, type='mark'))
        self.mark = ImageTk.PhotoImage(mark_resize)
        self.mark_offset_x_min = math.floor(self.mark.width() / 2)
        self.mark_offset_y_min = math.floor(self.mark.height() / 2)
        self.mark_offset_x_max = self.mark.width() - self.mark_offset_x_min
        self.mark_offset_y_max = self.mark.height() - self.mark_offset_y_min

        # TODO: make this into a function: load_image() -> preview_in_canvas()
        ghost_pil = Image.open('watermark.png')
        ghost_resize = ghost_pil.resize(self.size_calculate(ghost_pil.width, ghost_pil.height, type='mark'))
        ghost_resize.putalpha(128)
        self.ghost = ImageTk.PhotoImage(ghost_resize)

    # key functions
    def operate(self):
        self.window.mainloop()
        
    def size_calculate(self, width:int, height:int, *, type:str):
        if type == 'image':
            ratio:float =  min((canvas_width - canvas_padx * 2) / width, (canvas_height - canvas_pady * 2) / height) 
        elif type == 'mark' or type == 'watermark':
            ratio:float =  min(mark_width/width, mark_height/height) 
        else:
            raise NameError(f"Argument type '{type}' isn't allowed.")
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def mouse_loc_calibrate(self, x:int, y:int):
        x_min = self.image_datum_x + self.mark_offset_x_min
        y_min = self.image_datum_y + self.mark_offset_y_min
        x_max = self.image_datum_x + self.image.width() - self.mark_offset_x_max
        y_max = self.image_datum_y + self.image.height() - self.mark_offset_y_max
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
        x_calibrate = mouse_loc[0] - self.mark_offset_x_min
        y_calibrate = mouse_loc[1] - self.mark_offset_y_min
        return x_calibrate, y_calibrate
    
    # mouse location
    def canvas_action(self, event, *, method:str):
        x0, y0 = event.x, event.y
        x, y = self.mouse_loc_calibrate(x0, y0)
        if method == 'clicked':
            try:
                self.canvas.delete(self.watermark)
            except AttributeError:
                print("first time only AttributeError, no worries.")
            finally:
                self.watermark = self.canvas.create_image(x, y, image=self.mark, anchor='nw')
        elif method == 'motion':
            try:
                self.canvas.delete(self.watermark_preview)
            except AttributeError:
                print("first time only AttributeError, no worries.")
            finally:
                self.watermark_preview = self.canvas.create_image(x, y, image=self.ghost, anchor='nw')
        msg = f"hover over: x:{x}, y:{y} in canvas."
        
            
wm = WaterMarker()
wm.operate()