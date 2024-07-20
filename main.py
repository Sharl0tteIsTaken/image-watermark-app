import tkinter as tk
import numpy as np
import math

from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw


# default key dimensions
window_width = 1200
window_height = 700
canvas_width = 860
canvas_height = 560
canvas_padx = 30
canvas_pady = 30
mark_width = 50
mark_height = 50
default_font = ("Ariel", 20, "normal") #

class WaterMarker():
    """
    watermark picture with a image or text, watermark can be scaled proportionally,
    if watermark is placed at the border of the picture, it's snapped to that position,
    change of scale, font, fontsize or text won't effect the position.
    ---
    use .operate() to boot everything:
    
    `wm = WaterMarker()`
    
    `wm.operate()`
    """
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("💧MarkIt.")
        self.window.geometry(f"{window_width}x{window_height}")
        # self.window.resizable(width=False, height=False)
        self.window.option_add("*Font", default_font)
        self.window.config(background="white")
        
        self.setup_attribute()
        self.setup_variable()
        self.setup_labelframe()
        self.setup_widget()
        
        self.text_size_calculate()

    def setup_labelframe(self) -> None:
        """
        create and place every labelframe.
        
        Include:
        - block_image
        - block_panel
        """
        self.block_image = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_image.grid(column=0, row=1, ipadx=10, ipady=10)
        
        self.block_panel = tk.LabelFrame(self.window, bg="white", text="open file")
        self.block_panel.grid(column=0, row=0, columnspan=1)
    
    def setup_widget(self) -> None:
        """
        create and place every widget.
        
        Include:
        - canvas
        - btn_open_image
        - btn_open_mark
        - btn_switch
        - btn_save
        - entry_text
        """
        self.canvas = tk.Canvas(self.block_image, bg='white', width=canvas_width, height=canvas_height)
        self.canvas.pack()
        
        self.btn_open_image = tk.Button(self.block_panel, text="image", command=self.load_image)
        self.btn_open_image.grid(column=0, row=0)
        
        self.btn_open_mark = tk.Button(self.block_panel, text="watermark", command=self.load_mark)
        self.btn_open_mark.grid(column=1, row=0)
        
        # TODO: [later] move to load_asset() load asset for UI
        self.default_image = self.proper_load(filepath='assets/img/default_image.png', type='image')
        self.canvas_image_default = self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.default_image, anchor='center')
        
        self.switch_r = self.proper_load(filepath="assets/img/switch-right.png", type='image', max_size=(100,50))
        self.switch_l = self.proper_load(filepath="assets/img/switch-left.png", type='image', max_size=(100,50))
        
        
        self.btn_switch = tk.Button(self.block_panel, image=self.switch_r, command=self.switch_button) # type: ignore
        self.btn_switch.grid(column=2, row=0)
        
        self.entry_text = tk.Entry(self.block_panel, textvariable=self.user_enter_text)
        self.entry_text.bind("<Button-1>", self.remove_default_text)
        self.entry_text.grid(column=3, row=0)
        
        self.btn_save = tk.Button(self.block_panel, text='Save', command=self.save_image)
        self.btn_save.grid(column=4, row=0)
        
    def setup_variable(self):
        """
        create every variable for widgets.
        
        Include:
        - user_enter_text
        """
        self.user_enter_text = tk.StringVar()
        self.user_enter_text.set("enter text as watermark")
        
    def setup_attribute(self):
        """
        create every attribute for other functions.
        
        Include:
        - switch_state
        - exist_image
        - exist_mark
        - text_calibrate
        """
        self.switch_state = True # image
        self.exist_image = False
        self.exist_mark = False
        self.text_calibrate = True
    
    # key functions
    def operate(self):
        self.window.mainloop()
        
    def proper_load(self, *, filepath:str, type:str, alpha:int|None=None, max_size:tuple[int,int]|None=None):
        image_pil = Image.open(filepath)
        if type == 'image':
            self.source_image = image_pil
        elif type == 'mark':
            self.source_mark = image_pil
        if max_size:
            image_resize = image_pil.resize((max_size[0], max_size[1]))
        else:
            image_resize = image_pil.resize(self.image_size_calculate(image_pil.width, image_pil.height, type=type))
        if alpha:
            image_resize.putalpha(alpha)
        return ImageTk.PhotoImage(image_resize)
    
    def load_image(self):
        self.image = self.proper_load(filepath='assets/img/grey_box.png', type='image')
        # self.image = self.proper_load(filepath=filedialog.askopenfilename(), type='image')
        
        # calculate where datum's(top left corner of image) position will be in the canvas.
        self.image_datum_x = math.floor((canvas_width - self.image.width()) / 2)
        self.image_datum_y = math.floor((canvas_height - self.image.height()) / 2)
        
        # create image in canvas position at datum.
        self.canvas.create_image(self.image_datum_x, self.image_datum_y, image=self.image, anchor='nw')
        self.exist_image = True
        
        # remove default image
        self.canvas.delete(self.canvas_image_default)
        
        self.update_canvas_bind()
        
    def load_mark(self):
        # load watermark
        self.mark = self.proper_load(filepath='assets/img/watermark.png', type='mark')
        # self.mark = self.proper_load(filepath=filedialog.askopenfilename(), type='mark')

        # set preview of watermark
        self.ghost = self.proper_load(filepath='assets/img/watermark.png', type='mark', alpha=128)
        # self.mark = self.proper_load(filepath=filedialog.askopenfilename(), type='mark')
        
        self.exist_mark = True
        self.update_mark_offset(type='image')
        self.update_canvas_bind()
        
    def update_canvas_bind(self):
        if self.exist_mark and self.exist_image:
        # bind actions on canvas to function.
            self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
            self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
            self.canvas.focus_set()
        
    def update_mark_offset(self, type:str, bbox:tuple[int,int,int,int]|None=None):
        if type == 'image':
            self.mark_offset_x_min = math.floor(self.mark.width() / 2)
            self.mark_offset_y_min = math.floor(self.mark.height() / 2)
            self.mark_offset_x_max = self.mark.width() - self.mark_offset_x_min
            self.mark_offset_y_max = self.mark.height() - self.mark_offset_y_min
        elif type == 'text':
            assert bbox
            self.text_width = bbox[2] - bbox[0] # type: ignore
            self.text_height = bbox[3] - bbox[1] # type: ignore
            
            self.text_offset_x_min = math.floor(self.text_width / 2)
            self.text_offset_y_min = math.floor((self.text_height) / 2)
            self.text_offset_x_max = self.text_width - self.text_offset_x_min
            self.text_offset_y_max = self.text_height - self.text_offset_y_min
    
    def save_image(self):
        if self.snap:
            x = np.round(self.source_image.width * (self.snap_position[0] / self.image.width()))
            y = np.round(self.source_image.height * (self.snap_position[1] / self.image.height()))
            print(self.source_image.width, self.snap_position[0], self.image.width())
            print(self.source_image.height, self.snap_position[1], self.image.height())
            
        else:
            x = np.round(self.source_image.width * (self.mark_position[0] / self.image.width()))
            y = np.round(self.source_image.height * (self.mark_position[1] / self.image.height()))
            
            print(self.source_image.width, self.mark_position[0], self.image.width())
            print(self.source_image.height, self.mark_position[1], self.image.height())
            
        offset = (round(x), round(y))
        
        resized_mark = self.source_mark.resize((mark_width, mark_height))
        result_image = self.source_image.copy()
        result_image.paste(resized_mark, offset)
        result_image.save("result.png")
        
        
        
        # text part
        # self.source_mark = image_pil 
    
    # functions bind with command/action
    def switch_button(self):
        if self.switch_state:
            self.btn_switch.config(image=self.switch_l) # type: ignore
        else:
            self.btn_switch.config(image=self.switch_r) # type: ignore
        self.switch_state = not self.switch_state
        
    def remove_default_text(self, event):
        self.user_enter_text.set("")
        self.entry_text.bind("<Button-1>", self.entry_action)
        
    def entry_action(self, event):
        self.text_calibrate = False
        self.exist_mark = False
    
    def canvas_action(self, event, *, method:str):
        # TODO: break down this func
        x0, y0 = event.x, event.y
        if self.switch_state: # image
            x, y = self.mouse_loc_calibrate(x0, y0)
            if method == 'clicked':
                try:
                    self.canvas.delete(self.watermark_image)
                except AttributeError:
                    print("first time only AttributeError, no worries.")
                finally:
                    self.watermark_image = self.canvas.create_image(x, y, image=self.mark, anchor='nw')
                    self.mark_position:tuple[int, int] = x, y
            elif method == 'motion':
                try:
                    self.canvas.delete(self.watermark_image_preview)
                except AttributeError:
                    print("first time only AttributeError, no worries.")
                finally:
                    self.watermark_image_preview = self.canvas.create_image(x, y, image=self.ghost, anchor='nw')
        else: # text
            if not self.text_calibrate:
                self.text_size_calculate()
            x, y = self.mouse_loc_calibrate(x0, y0)
            if method == 'clicked':
                try:
                    self.canvas.delete(self.watermark_text)
                except AttributeError:
                    print("first time only AttributeError, no worries.")
                finally:
                    self.watermark_text = self.canvas.create_text(x, y, text=self.entry_text.get(), font=default_font, anchor='nw')
                    self.mark_position:tuple[int, int] = x, y
            elif method == 'motion':
                try:
                    self.canvas.delete(self.watermark_text_preview)
                except AttributeError:
                    print("first time only AttributeError, no worries.")
                finally:
                    self.watermark_text_preview = self.canvas.create_text(x, y, text=self.entry_text.get(), font=default_font, anchor='nw')
    
    # support functions
    def image_size_calculate(self, width:int, height:int, *, type:str):
        if type == 'image':
            ratio:float =  min((canvas_width - canvas_padx * 2) / width, (canvas_height - canvas_pady * 2) / height) 
        elif type == 'mark':
            ratio:float =  min(mark_width/width, mark_height/height) 
        else:
            raise NameError(f"Argument type '{type}' isn't allowed.")
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def text_size_calculate(self):
        calibrate_text = self.canvas.create_text(canvas_width/2, canvas_height/2, text=self.entry_text.get(), font=default_font, anchor='nw') # TODO: get font from UI
        bbox = self.canvas.bbox(calibrate_text)
        
        self.text_width = bbox[2] - bbox[0] # type: ignore
        self.text_height = bbox[3] - bbox[1] # type: ignore

        self.update_mark_offset(type='text', bbox=bbox)
        self.canvas.delete(calibrate_text)
        self.exist_mark = True
    
    def mouse_loc_calibrate(self, x:int, y:int):
        if self.switch_state: # image
            x_min = self.image_datum_x + self.mark_offset_x_min
            y_min = self.image_datum_y + self.mark_offset_y_min
            x_max = self.image_datum_x + self.image.width() - self.mark_offset_x_max
            y_max = self.image_datum_y + self.image.height() - self.mark_offset_y_max
        else: # text
            x_min = self.image_datum_x + self.text_offset_x_min
            y_min = self.image_datum_y + self.text_offset_y_min
            x_max = self.image_datum_x + self.image.width() - self.text_offset_x_max
            y_max = self.image_datum_y + self.image.height() - self.text_offset_y_max
        
        self.snap = True
        if x_max >= x >= x_min and y_max >= y >= y_min: # in image
            mouse_loc = x, y
            self.snap = False
        elif x <= x_min and y <= y_min: # top left corner
            mouse_loc = x_min, y_min
            self.snap_position = (0, 0)
        elif x >= x_max and y <= y_min: # top right corner
            mouse_loc = x_max, y_min
            self.snap_position = (0, self.image.height())
        elif x <= x_min and y >= y_max: # btm left corner
            mouse_loc = x_min, y_max
            self.snap_position = (self.image.width(), 0)
        elif x >= x_max and y >= y_max: # btm right corner
            mouse_loc = x_max, y_max
            self.snap_position = (self.image.width(), self.image.height())
        elif x_max >= x >= x_min and y <= y_min: # top border
            mouse_loc = x, y_min
            self.snap_position = (x, 0)
        elif x_max >= x >= x_min and y >= y_max: # btm border
            mouse_loc = x, y_max
            self.snap_position = (x, self.image.height())
        elif x <= x_min and y_max >= y >= y_min: # left border
            mouse_loc = x_min, y
            self.snap_position = (0, y)
        elif x >= x_max and y_max >= y >= y_min: # right border
            mouse_loc = x_max, y
            self.snap_position = (self.image.width(), y)
        else:
            raise ValueError(f"mind blown, clicked at (x:{x}, y:{y}), not in elif tree?\n\
                image size: ({self.image.width()}x{self.image.height()})\n\
                datum at (x:{self.image_datum_x}, y:{self.image_datum_y})\n\
                x min max: {x_min}, {x_max}\n\
                y min max: {y_min}, {y_max}\n\
                never thought this will occur, add any missed info to mouse_loc_calibrate().")
        if self.switch_state: # image
            x_calibrate = mouse_loc[0] - self.mark_offset_x_min
            y_calibrate = mouse_loc[1] - self.mark_offset_y_min
        else: # text
            x_calibrate = mouse_loc[0] - self.text_offset_x_min
            y_calibrate = mouse_loc[1] - self.text_offset_y_min
        return x_calibrate, y_calibrate
    

wm = WaterMarker()
wm.operate()