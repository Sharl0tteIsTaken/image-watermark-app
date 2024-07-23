import tkinter as tk
import numpy as np
import math

import support_func

from tkinter import filedialog, font, ttk, messagebox
from PIL import ImageTk, Image, ImageDraw


# default key dimensions
window_width = 1400
window_height = 700
canvas_width = 860
canvas_height = 560
canvas_padx = 30
canvas_pady = 30
mark_width = 50
mark_height = 50
default_font = ("Ariel", 16, "normal") #

font_info = "\
rule of font:                                    \n\
1. will prioritise font selected than entered.   \n\
2. entered font will be ignored if not found.    \n\
3. if didn't select a font or not entered/found, \n\
   default font is selected.                     "
# FIXME:  typeset font_info.

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
        
        self.block_edit = tk.LabelFrame(self.window, bg="white", text="font of text", padx=10, pady=10)
        self.block_edit.grid(column=1, row=1)
    
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
        # block image
        self.canvas = tk.Canvas(self.block_image, bg='white', width=canvas_width, height=canvas_height)
        self.canvas.pack()
        
        # block panel
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
        
        self.btn_save = tk.Button(self.block_panel, text='Save', command=self.save_image)
        self.btn_save.grid(column=3, row=0)
        
        # block edit
        self.lbl_text = tk.Label(self.block_edit, text="text", bg='white')
        self.lbl_text.grid(column=0, row=0)
        
        self.entry_text = tk.Entry(self.block_edit, textvariable=self.user_enter_text, cursor='xterm', width=30)
        self.entry_text.bind("<Button-1>", lambda event: self.clear_tkentry_text(event, tag='text'))
        self.entry_text.grid(column=1, row=0)
        
        
        self.lbl_font = tk.Label(self.block_edit, text="fontⓘ", bg='white')
        support_func.add_tool_tip(self.lbl_font, font_info)
        self.lbl_font.grid(column=0, row=1, rowspan=2)
        
        self.entry_font = tk.Entry(self.block_edit, textvariable=self.user_enter_font, width=30)
        self.entry_font.bind("<Button-1>", lambda event: self.clear_tkentry_text(event, tag='font'))
        self.entry_font.bind("<Return>", self.validate_font) # type: ignore
        self.entry_font.grid(column=1, row=1)
        
        self.lbl_font = tk.Label(self.block_edit, text="or", width=3, bg='white')
        self.lbl_font.grid(column=2, row=1)
        
        self.selector_font = ttk.Combobox(self.block_edit, values=('select a font',), width=32)
        self.selector_font.current(0)
        self.selector_font['values'] = font.families()
        self.selector_font.bind(
            "<<ComboboxSelected>>", 
            lambda event: 
                self.user_enter_font.set(self.selector_font.get()), 
                self.text_size_calculate) # type: ignore
        self.selector_font.grid(column=1, row=2, columnspan=2)
        
        
        self.lbl_fontsize = tk.Label(self.block_edit, text="size", bg='white')
        self.lbl_fontsize.grid(column=0, row=3)
        
        self.entry_fontsize = tk.Spinbox(
            self.block_edit, 
            from_=8, to=108, 
            command=self.text_size_calculate, 
            textvariable=self.user_enter_fontsize, 
            width=4)
        self.entry_fontsize.grid(column=1, row=3, sticky='w')
        
        
        self.lbl_fontstyle = tk.Label(self.block_edit, text="style", bg='white')
        self.lbl_fontstyle.grid(column=0, row=4)
        
        self.selector_fontstyle = ttk.Combobox(self.block_edit, width=8)
        self.selector_fontstyle['values'] = ('normal', 'italic', 'bold')
        self.selector_fontstyle.current(0)
        self.selector_fontstyle.bind("<<ComboboxSelected>>", self.text_size_calculate) # type: ignore
        self.selector_fontstyle.grid(column=1, row=4, sticky='w')

        
        self.btn_confirm = tk.Button(self.block_edit, text='update', command=self.text_size_calculate)
        self.btn_confirm.grid(column=1, row=5, sticky='w')
        # TODO: [later] add QOL update so that if user forgot to confirm change it'll still update, make it a force update
        # set canvas and block edit alternating bind with function that calls text calibrate.
        
    def setup_variable(self) -> None:
        """
        create every variable for widgets.
        
        Include:
        - user_enter_text
        """
        self.user_enter_text = tk.StringVar()
        self.user_enter_text.set("enter text as watermark")
        
        self.user_enter_font = tk.StringVar()
        self.user_enter_font.set("enter font")
        
        self.user_enter_fontsize = tk.IntVar()
        self.user_enter_fontsize.set(default_font[1])
        
    def setup_attribute(self) -> None:
        """
        create every attribute for other functions.
        
        Include:
        - switch_state
        - exist_image
        - exist_mark
        - text_calibrate
        """
        self.exist_image = False
        self.exist_mark = False
        self.text_calibrate = True
        self.watermark_contain:str = "image"
        self.user_enter_font_store = "enter font"
        self.user_select_font_store = "select a font"
    
    # key functions
    def operate(self) -> None:
        """
        the power button.
        """
        self.window.mainloop()
        
    def proper_load(
        self, 
        *, 
        filepath:str, 
        type:str, 
        alpha:int|None=None, 
        max_size:tuple[int,int]|None=None
        ) -> ImageTk.PhotoImage:
        """
        load image from filepath to Image to PhotoImage, 
        adjust image alpha and image size of desired.
        stores Image in self.source_

        Args:
            filepath (str): file path of the loading image.
            type (str): type of loading image, 'image' or 'mark'.
            alpha (int | None, optional): add translucent to the image, range 0 ~ 255, translucent % = (alpha/255). Defaults to None.
            max_size (tuple[int,int] | None, optional): set max size of the image, image will be scale up to width and/or height specified. Defaults to None.

        Returns:
            ImageTk.PhotoImage: the image specified.
        """
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
    
    def load_image(self) -> None:
        """
        ask user filepath to load image,
        create the image on canvas and remove default(place holder) image.
        """
        self.image = self.proper_load(filepath='assets/img/checkboard_color.png', type='image')
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
        
    def load_mark(self) -> None:
        """
        ask user filepath to load watermark,
        bind canvas with user action,
        calls to update watermark offset.
        """
        # load watermark
        self.mark = self.proper_load(filepath='assets/img/watermark.png', type='mark')
        # self.mark = self.proper_load(filepath=filedialog.askopenfilename(), type='mark')

        # set preview of watermark
        self.ghost = self.proper_load(filepath='assets/img/watermark.png', type='mark', alpha=128)
        # self.mark = self.proper_load(filepath=filedialog.askopenfilename(), type='mark')
        
        self.exist_mark = True
        self.update_mark_offset(type='image')
        self.update_canvas_bind()
        
    def update_canvas_bind(self) -> None:
        """
        if both watermark and image exist,
        bind M1 and mouse motion with function:self.canvas_action,
        set focus to canvas.
        """
        if self.exist_mark and self.exist_image:
        # bind actions on canvas to function.
            self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
            self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
            self.canvas.focus_set()
        
    def update_mark_offset(self, type:str, bbox:tuple[int,int,int,int]|None=None) -> None:
        """
        update watermark offset from user click position to top left corner of the watermark.

        Args:
            type (str): type of watermark, 'image' or 'text'.
            bbox (tuple[int,int,int,int] | None, optional): the border box of the watermark(text) on canvas. Defaults to None.
        """
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
        
    def text_size_calculate(self, event=None) -> None:
        """
        calculate text size by create a temporary text on canvas
        to get width, height, and calculate offset of the watermark,
        delete temporary text on canvas afterwards.
        
        bind('<ComboboxSelected>') somehow cause TypeError: 
        1. missing 1 required positional argument: 'event'
        2. takes 1 positional argument but 2 were given
        either 1. or 2. will be raised, so added event=None in args, but that has no effect(fingers crossed).
        """
        self.validate_font()
        if self.selector_font.get() == 'select a font' and self.entry_font.get() == 'enter font':
            request_font = default_font[0]
        elif self.selector_font.get() != 'select a font':
            request_font = self.selector_font.get()
        elif self.entry_font.get() != 'enter font':
            if self.entry_font.get() in font.families():
                request_font = self.entry_font.get()
            else:
                request_font = default_font[0]
            
        format_ = (request_font, self.user_enter_fontsize.get(), self.selector_fontstyle.get())
        
        
        
        
        calibrate_text = self.canvas.create_text(canvas_width/2, canvas_height/2, text=self.entry_text.get(), font=format_, anchor='nw') # TODO: get font from UI
        bbox = self.canvas.bbox(calibrate_text)
        
        self.text_width = bbox[2] - bbox[0] # type: ignore
        self.text_height = bbox[3] - bbox[1] # type: ignore

        self.update_mark_offset(type='text', bbox=bbox)
        self.canvas.delete(calibrate_text)
        self.exist_mark = True
    
    def save_image(self) -> None:
        """
        save image with watermark, where the location of watermark is set by user,
        snap to border if watermark will be outside of image,
        image will be saved at root folder in project.
        """
        width_scale = self.source_image.width / self.image.width()
        height_scale = self.source_image.height / self.image.height()
        
        if self.snap:
            x = np.round(self.snap[0] * width_scale)
            y = np.round(self.snap[1] * height_scale)

            if self.snap[0] == self.image.width():
                x -= self.mark.width()
            if self.snap[1] == self.image.height():
                y -= self.mark.height()
        else:
            self.canvas.create_oval(self.true_position[0], self.true_position[1], self.true_position[0], self.true_position[1], fill='red', width=5)
            self.canvas.create_oval(self.image_datum_x, self.image_datum_y, self.image_datum_x, self.image_datum_y, fill='blue', width=5)
            true_x = self.true_position[0] - self.mark_offset_x_min - self.image_datum_x
            true_y = self.true_position[1] - self.mark_offset_y_min - self.image_datum_y
            
            x = np.round(true_x * width_scale)
            y = np.round(true_y * height_scale)

        mark_true_width = np.round(self.mark.width() * height_scale)
        mark_true_height = np.round(self.mark.height() * width_scale)
        
        mark_true_size = (round(mark_true_width), round(mark_true_height))
        offset = (round(x), round(y))

        resized_mark = self.source_mark.resize(mark_true_size)
        result_image = self.source_image.copy()
        result_image.paste(resized_mark, offset)
        result_image.save("result.png")
        
        
        
        # TODO: text part
        # self.source_mark = image_pil 
    
    # functions bind with command/action
    def switch_button(self) -> None:
        """
        switch watermark to image or text, not-the-current one,
        remove previous created watermark and preview.
        """
        if self.watermark_contain == 'image':
            self.btn_switch.config(image=self.switch_l) # type: ignore
            self.watermark_contain = 'text'
            try:
                self.canvas.delete(self.watermark_image_preview)
                self.canvas.delete(self.watermark_image)
            except AttributeError:
                print("making sure to remove unwanted watermarks")
        elif self.watermark_contain == 'text':
            self.btn_switch.config(image=self.switch_r) # type: ignore
            self.watermark_contain = 'image'
            try:
                self.canvas.delete(self.watermark_text_preview)
                self.canvas.delete(self.watermark_text)
            except AttributeError:
                print("making sure to remove unwanted watermarks")
        
    def clear_tkentry_text(self, event, tag:str) -> None:
        """
        remove default text in tk.Entry, when user click in tk.Entry
        and bind M1 to function:self.entry_action.

        Args:
            event (_type_): _description_ #TODO: [last] check if anything need to be here
        """
        if tag == 'text':
            self.user_enter_text.set("")
        elif tag == 'font':
            self.user_enter_font.set("")
        self.entry_text.bind("<Button-1>", self.entry_action)
        self.entry_action(event) # make sure first click also force calibrate
        
    def entry_action(self, event) -> None:
        """
        self self.text_calibrate and self.exist_mark to False,
        this will mark watermark(text) to calibrate when user click on canvas.

        Args:
            event (_type_): _description_ #TODO: [last] check if anything need to be here
        """
        self.text_calibrate = False
        self.exist_mark = False
    
    def canvas_action(self, event, *, method:str) -> None:
        """
        main function in responce for user action in canvas,
        manage everything after click and mouse movement.

        Args:
            event (_type_): _description_ #TODO: [last] check if anything need to be here
            method (str): user action on canvas, 'clicked' or 'motion'.
        """
        try:
            self.remove_exist_watermark(method=method)
        except AttributeError:
            print("first time only AttributeError, no worries.")
            
        x0, y0 = event.x, event.y
        x, y, snap_position = self.mouse_loc_calibrate(x0, y0) 
        
        if method == 'clicked':
            self.snap:tuple[int,int]|None = snap_position
            self.true_position:tuple[int, int] = x0, y0
        self.draw_watermark(x, y, method=method)
        
    
    # support functions
    def image_size_calculate(self, width:int, height:int, *, type:str) -> tuple[int, int]:
        """
        calculate size of image to have a set blank border in canvas, which will use later to resize image. 

        Args:
            width (int): original width of the image.
            height (int): original height of the image.
            type (str): type of the image, 'image' or 'mark'.

        Returns:
            tuple[int, int]: calculated width and height to meet one and/or both of the requirement of the canvas(to have a set blank border).
        """
        if type == 'image':
            ratio:float =  min((canvas_width - canvas_padx * 2) / width, (canvas_height - canvas_pady * 2) / height) 
        elif type == 'mark':
            ratio:float =  min(mark_width/width, mark_height/height) 
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def validate_font(self, event=None) -> None:
        """
        validate font from user, show messagebox when font not exist.
        
        Args:
            event (_type_): see text_size_calculate()
        """
        user_enter = self.entry_font.get()
        if self.font_changed():
            if user_enter not in font.families():
                messagebox.showerror(
                    title="font not found.", 
                    message=f"font entered: '{user_enter}',\nmake sure everything was correct, or select one instead.")
            
    def font_changed(self) -> bool:
        if self.entry_font.get() == self.user_enter_font_store and self.selector_font.get() == self.user_select_font_store:
            return False
        self.user_enter_font_store = self.entry_font.get()
        self.user_select_font_store = self.selector_font.get()
        return True
            
    def remove_exist_watermark(self, method:str) -> None:
        """
        remove watermark on canvas by following:
        1. remove previous previews
        2. remove previous watermark when user clicked on canvas
        3. remove all not-the-current watermark and preview
        

        Args:
            method (str): user action, 'clicked' or 'motion'.
        """
        if method == 'clicked':
            if self.watermark_contain == 'image':
                self.canvas.delete(self.watermark_image)
            elif self.watermark_contain == 'text':
                self.canvas.delete(self.watermark_text)
        elif method == 'motion':
            if self.watermark_contain == 'image':
                self.canvas.delete(self.watermark_image_preview)
            elif self.watermark_contain == 'text':
                self.canvas.delete(self.watermark_text_preview)
    
    def draw_watermark(self, x:int, y:int, method:str) -> None:
        """
        draw watermark on (x, y) in canvas, watermark type is determined by args:method.

        Args:
            x (int): x location to draw on the canvas.
            y (int): y location to draw on the canvas.
            method (str): user action, 'clicked' or 'motion'.
        """
        if self.watermark_contain == 'image':
            if method == 'clicked':
                self.watermark_image = self.canvas.create_image(x, y, image=self.mark, anchor='nw')
            elif method == 'motion':
                self.watermark_image_preview = self.canvas.create_image(x, y, image=self.ghost, anchor='nw')
        elif self.watermark_contain == 'text':
            if not self.text_calibrate:
                # TODO: make sure to clibrate here?
                self.text_size_calculate()
            if method == 'clicked':
                self.watermark_text = self.canvas.create_text(x, y, text=self.entry_text.get(), font=default_font, anchor='nw')
            elif method == 'motion':
                self.watermark_text_preview = self.canvas.create_text(x, y, text=self.entry_text.get(), font=default_font, anchor='nw')
    
    def mouse_loc_calibrate(self, x:int, y:int) -> tuple[int, int, tuple[int,int]|None]:
        """
        make sure wherever user's mouse is in canvas, 
        watermark and preview will appear on image.
        
        Args:
            x (int): x of mouse location
            y (int): y of mouse location

        Raises:
            ValueError: user click on somewhere unexpected, can't imagine how, so print everything thought be helpful.

        Returns:
            tuple[int, int, tuple[int,int]|None]: (x_calibrated, y_calibrated, (x_snap_position, y_snap_position)|None), None if watermark isn't snapped to border of image.
        """
        # TODO: add a self.current_minax: tuple[int, int, int, int] to store xyminmax to use later as snap_location ??
        if self.watermark_contain == 'image':
            x_min = self.image_datum_x + self.mark_offset_x_min
            y_min = self.image_datum_y + self.mark_offset_y_min
            x_max = self.image_datum_x + self.image.width() - self.mark_offset_x_max
            y_max = self.image_datum_y + self.image.height() - self.mark_offset_y_max
            self.current_stats:tuple[str,int,int,int,int] = 'image', x_min, y_min, x_max, y_max # TODO: del this if not used
        elif self.watermark_contain == 'text':
            x_min = self.image_datum_x + self.text_offset_x_min
            y_min = self.image_datum_y + self.text_offset_y_min
            x_max = self.image_datum_x + self.image.width() - self.text_offset_x_max
            y_max = self.image_datum_y + self.image.height() - self.text_offset_y_max
            self.current_stats:tuple[str,int,int,int,int] = 'text', x_min, y_min, x_max, y_max

        
        snap_position = None
        if x_max >= x >= x_min and y_max >= y >= y_min: # in image
            mouse_loc = x, y
        elif x <= x_min and y <= y_min: # top left corner
            mouse_loc = x_min, y_min
            snap_position = (0, 0)
        elif x >= x_max and y <= y_min: # top right corner
            mouse_loc = x_max, y_min
            snap_position = (self.image.width(), 0)
        elif x <= x_min and y >= y_max: # btm left corner
            mouse_loc = x_min, y_max
            snap_position = (0, self.image.height())
        elif x >= x_max and y >= y_max: # btm right corner
            mouse_loc = x_max, y_max
            snap_position = (self.image.width(), self.image.height())
        elif x_max >= x >= x_min and y <= y_min: # top border
            mouse_loc = x, y_min
            snap_position = (x, 0)
        elif x_max >= x >= x_min and y >= y_max: # btm border
            mouse_loc = x, y_max
            snap_position = (x, self.image.height())
        elif x <= x_min and y_max >= y >= y_min: # left border
            mouse_loc = x_min, y
            snap_position = (0, y)
        elif x >= x_max and y_max >= y >= y_min: # right border
            mouse_loc = x_max, y
            snap_position = (self.image.width(), y)
        else:
            raise ValueError(f"mind blown, clicked at (x:{x}, y:{y}), not in elif tree?\n\
                image size: ({self.image.width()}x{self.image.height()})\n\
                datum at (x:{self.image_datum_x}, y:{self.image_datum_y})\n\
                x min max: {x_min}, {x_max}\n\
                y min max: {y_min}, {y_max}\n\
                never thought this will occur, add any missed info to mouse_loc_calibrate().")
        if self.watermark_contain == 'image':
            x_calibrate = mouse_loc[0] - self.mark_offset_x_min
            y_calibrate = mouse_loc[1] - self.mark_offset_y_min
        elif self.watermark_contain == 'text':
            x_calibrate = mouse_loc[0] - self.text_offset_x_min
            y_calibrate = mouse_loc[1] - self.text_offset_y_min
        return x_calibrate, y_calibrate, snap_position
    

wm = WaterMarker()
wm.operate()