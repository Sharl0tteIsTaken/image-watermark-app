import tkinter as tk
import math

from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw

# default key dimensions
window_width = 1200
window_height = 700
canvas_width = 860
canvas_height = 660
canvas_padx = 30
canvas_pady = 30
mark_width = 50
mark_height = 50
default_font = ("Ariel", 20, "normal") #

class WaterMarker():
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("💧MarkIt.")
        self.window.geometry(f"{window_width}x{window_height}")
        # self.window.resizable(width=False, height=False)
        self.window.option_add("*Font", default_font)
        self.window.config(background="white")
        
        self.setup_labelframe()
        self.setup_widget()

    def setup_labelframe(self):
        self.block_image = tk.LabelFrame(self.window, bg="white")
        self.block_image.config(border=0)
        self.block_image.grid(column=0, row=1, ipadx=10, ipady=10)
        
        self.block_panel = tk.LabelFrame(self.window, bg="white", text="open file")
        self.block_panel.grid(column=0, row=0, columnspan=1)
    
    def setup_widget(self):
        self.canvas = tk.Canvas(self.block_image, bg='white', width=canvas_width, height=canvas_height)
        self.canvas.pack()
        
        self.btn_open_image = tk.Button(self.block_panel, text="image", command=self.load_image)
        self.btn_open_image.grid(column=0, row=0)
        
        self.btn_open_mark = tk.Button(self.block_panel, text="watermark", command=self.load_mark)
        self.btn_open_mark.grid(column=1, row=0)

        image_pil = Image.open('assets/img/default_image.png')
        image_resize = image_pil.resize(self.size_calculate(image_pil.width, image_pil.height, type='image'))
        default_image = ImageTk.PhotoImage(image_resize)
        self.canvas.create_image(canvas_width/2, canvas_height/2, image=default_image, anchor='center')
        # self.canvas_image_default = 

    def load_image(self):
        
        image_pil = Image.open('assets/img/grey_box.png')
        # image_pil = Image.open(filedialog.askopenfilename())
        image_resize = image_pil.resize(self.size_calculate(image_pil.width, image_pil.height, type='image'))
        self.image = ImageTk.PhotoImage(image_resize)
        
        # calculate where datum's(top left corner of image) position will be in the canvas.
        self.image_datum_x = math.floor((canvas_width - self.image.width()) / 2)
        self.image_datum_y = math.floor((canvas_height - self.image.height()) / 2)
        
        # create image in canvas position at datum.
        self.canvas.create_image(self.image_datum_x, self.image_datum_y, image=self.image, anchor='nw')
                
    def load_mark(self):
        # load watermark
        mark_pil = Image.open('assets/img/watermark.png')
        # mark_pil = Image.open(filedialog.askopenfilename())
        mark_resize = mark_pil.resize(self.size_calculate(mark_pil.width, mark_pil.height, type='mark'))
        self.mark = ImageTk.PhotoImage(mark_resize)
        self.mark_offset_x_min = math.floor(self.mark.width() / 2)
        self.mark_offset_y_min = math.floor(self.mark.height() / 2)
        self.mark_offset_x_max = self.mark.width() - self.mark_offset_x_min
        self.mark_offset_y_max = self.mark.height() - self.mark_offset_y_min

        # set preview of watermark
        ghost_pil = Image.open('assets/img/watermark.png')
        ghost_resize = ghost_pil.resize(self.size_calculate(ghost_pil.width, ghost_pil.height, type='mark'))
        ghost_resize.putalpha(128)
        self.ghost = ImageTk.PhotoImage(ghost_resize)
        
        # bind actions on canvas to function.
        self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
        self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
        self.canvas.focus_set()

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
        
            
wm = WaterMarker()
wm.operate()