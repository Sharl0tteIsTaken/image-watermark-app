import tkinter as tk
import numpy as np
import math

import support_func

from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter
from string import ascii_letters
from tkinter import colorchooser, filedialog, font, messagebox, ttk

# default key dimensions
window_width = 1400
window_height = 700
canvas_width = 860
canvas_height = 560
canvas_padx = 30
canvas_pady = 30
mark_width = 50
mark_height = 50
default_font = ("Arial", 16, "normal") #
text_watermark_max_size = (2000, 2000)

# TODO: make sure all docstring is updated

font_info = "\
rule of font:\n\
1. will prioritise font selected than entered.\n\
2. entered font will be ignored if not found.\n\
3. if didn't select a font or not entered/found\n\
   default font is selected."
# FIXME:  typeset font_info. guess it will be at tooltip.py

watermark_fp = "watermark_text.png" # TODO: [later] get this a location to stay

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
        self.load_setup_default_()
        self.setup_widget()
        
        self.text_mark_maker()
        
        
        
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
        self.mark_pending = False
        self.text_calibrate = False
        self.current_font_hexcolor = "black"
        self.user_select_font_store = 'select a font'
        self.current_font_rgb:tuple[int,int,int] = (0, 0, 0)
        
        fonts:list[str] = list(font.families())
        mixed:list[str] = [font for font in fonts[:] if font[0] != "@"]
        chinese:list[str] = [font for font in mixed[:] if font[0] not in ascii_letters]
        self.include_fonts:list[str] = sorted(mixed) + sorted(chinese)
        
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
        self.user_enter_font_store = self.user_enter_font.get()
        
        self.user_enter_fontsize = tk.IntVar()
        self.user_enter_fontsize.set(default_font[1])

    def setup_labelframe(self) -> None:
        """
        create and place every labelframe.
        
        Include:
        - block_image
        - block_panel
        """
        self.block_panel = tk.LabelFrame(self.window, text="open file", bg="white")
        self.block_panel.grid(column=0, row=0, columnspan=1) # TODO: why colspan 1?
        
        self.block_image = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_image.grid(column=0, row=1, ipadx=10, ipady=10)
        
        self.block_edit = tk.LabelFrame(self.window, text="font of text", bg="white", padx=10, pady=10)
        self.block_edit.grid(column=1, row=1, sticky='nw')
        
        self.block_text_preview = tk.LabelFrame(self.window, text="text watermark preview", bg="white", padx=10, pady=10)
        self.block_text_preview.grid(column=1, row=1, sticky='s')
    
    def load_setup_default_(self):
        # TODO: [later] move to load_asset() load asset for UI
        self.default_image = self.proper_load(filepath='assets/img/default_image.png', type='image')
        self.image_width_scale = self.image_pil.width / self.default_image.width()
        self.image_height_scale = self.image_pil.height / self.default_image.height()
        
        self.switch_r = self.proper_load(filepath="assets/img/switch-right.png", type='image', max_size=(100,50))
        self.switch_l = self.proper_load(filepath="assets/img/switch-left.png", type='image', max_size=(100,50))
    
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
        
        self.canvas_image_default = self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.default_image, anchor='center')
        
        # block panel
        self.btn_open_image = tk.Button(self.block_panel, text="image", command=self.load_image)
        self.btn_open_image.grid(column=0, row=0)
        
        self.btn_open_mark = tk.Button(self.block_panel, text="watermark", command=self.load_mark)
        self.btn_open_mark.grid(column=1, row=0)
        
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
        self.selector_font['values'] = self.include_fonts
        self.selector_font.bind(
            "<<ComboboxSelected>>", 
            lambda event: 
                self.user_enter_font.set(self.selector_font.get()), 
                self.text_mark_maker) # type: ignore
        self.selector_font.grid(column=1, row=2, columnspan=2)
        
        
        self.lbl_fontsize = tk.Label(self.block_edit, text="size", bg='white')
        self.lbl_fontsize.grid(column=0, row=3)
        
        self.spnbx_fontsize = tk.Spinbox(
            self.block_edit, 
            from_=8, to=108, 
            command=self.text_mark_maker, 
            textvariable=self.user_enter_fontsize, 
            width=4)
        self.spnbx_fontsize.grid(column=1, row=3, sticky='w')
        
        
        self.lbl_fontstyle = tk.Label(self.block_edit, text="style", bg='white')
        self.lbl_fontstyle.grid(column=0, row=4)
        
        self.selector_fontstyle = ttk.Combobox(self.block_edit, width=8)
        self.selector_fontstyle['values'] = ('normal', 'bold', 'italic', 'bold and italic')
        self.selector_fontstyle.current(0)
        self.selector_fontstyle.bind("<<ComboboxSelected>>", self.text_mark_maker) # type: ignore
        self.selector_fontstyle.grid(column=1, row=4, sticky='w')

        
        self.lbl_color = tk.Label(self.block_edit, text="color", bg='white')
        self.lbl_color.grid(column=0, row=5)
        
        self.btn_color_chooser = tk.Button(self.block_edit, text="select a color", command=self.choose_color)
        self.btn_color_chooser.grid(column=1, row=5, sticky='w')
        
        # TODO: add transparency % bar to self.block_edit
        # TODO: add checkbox of preview watermark
        self.lbl_opaque = tk.Label(self.block_edit, text="opaque", bg='white') # TODO: change to alpha(saturation)
        self.lbl_opaque.grid(column=0, row=6) # TODO: add tool tip: no preview for alpha
        
        self.scale_opaque = tk.Scale(
            self.block_edit, 
            from_=0, to=100, 
            command=self.text_mark_maker, 
            orient='horizontal', 
            bg='white', 
            width=10)
        self.scale_opaque.set(100)
        self.scale_opaque.grid(column=1, row=6, sticky='w')
        
        
        self.btn_confirm = tk.Button(self.block_edit, text='update', command=self.text_mark_maker)
        self.btn_confirm.grid(column=1, row=7, sticky='w')
        
        
        
        
        # TODO: add QOL update so that if user forgot to confirm change it'll still update, make it a force update
        # set canvas and block edit alternating bind with motion to function that calls text calibrate.
    
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
        max_size:tuple[int,int]|None=None
        ) -> ImageTk.PhotoImage:
        """
        load image from filepath to Image to PhotoImage, 
        adjust image alpha and image size of desired.
        stores Image in self.source_

        Args:
            filepath (str): file path of the loading image.
            type (str): type of loading image, 'image' or 'mark'.
            alpha (int | None, optional): add translucent to the image, 
                range 0 ~ 255, translucent % = (alpha/255). Defaults to None.
            max_size (tuple[int,int] | None, optional): set max size of the image, 
                image will be scale up to width and/or height specified. Defaults to None.

        Returns:
            ImageTk.PhotoImage: the image specified.
        """
        image_pil = Image.open(filepath)
        
        self.watermark_type = type
        if type == 'image':
            self.image_pil = image_pil
        elif type == 'mark':
            self.mark_pil = image_pil
        elif type == "text":
            self.mark_pil = image_pil
            width = np.round(image_pil.width / self.image_width_scale)
            height = np.round(image_pil.height / self.image_height_scale)
            size = (round(width), round(height))
        if max_size:
            image_resize = image_pil.resize((max_size[0], max_size[1]))
        elif type == "text":
            image_resize = image_pil.resize(size)
        else:
            image_resize = image_pil.resize(
                self.image_size_calculate(image_pil.width, image_pil.height, type=type)
                )
        self.exist_mark = True
        return ImageTk.PhotoImage(image_resize)
    
    def load_image(self) -> None:
        """
        ask user filepath to load image,
        create the image on canvas and remove default(place holder) image.
        """
        self.filepath_image = 'assets/img/200x200.png'
        self.image = self.proper_load(filepath=self.filepath_image, type='image')
        # self.image = self.proper_load(filepath=filedialog.askopenfilename(), type='image')
        self.image_width_scale = self.image_pil.width / self.image.width()
        self.image_height_scale = self.image_pil.height / self.image.height()
        
        # calculate where datum's(top left corner of image) position will be in the canvas.
        self.image_datum_x = math.floor((canvas_width - self.image.width()) / 2)
        self.image_datum_y = math.floor((canvas_height - self.image.height()) / 2)
        
        # create image in canvas position at datum.
        self.canvas.create_image(self.image_datum_x, self.image_datum_y, image=self.image, anchor='nw')
        self.exist_image = True
        
        # remove default image
        self.canvas.delete(self.canvas_image_default)
        
        self.update_mark_size()
        self.update_canvas_bind()
        
    def load_mark(self) -> None:
        """
        ask user filepath to load watermark,
        bind canvas with user action,
        calls to update watermark offset.
        """
        self.ghost = self.mark = self.proper_load(filepath='assets/img/watermark.png', type='mark')
        #self.ghost = self.mark = self.proper_load(filepath=filedialog.askopenfilename(), type='mark')
        
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
            self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
            self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
            self.canvas.focus_set()
        
    def update_mark_size(self):
        width = np.round(self.mark_pil.width / self.image_width_scale)
        height = np.round(self.mark_pil.height / self.image_height_scale)
        size = (round(width), round(height))
        
        image_resize = self.mark_pil.resize(size)
        
        self.mark = ImageTk.PhotoImage(image_resize)
        
    def update_mark_offset(self, type:str, bbox:tuple[int,int,int,int]|None=None) -> None:
        """
        update watermark offset from user click position to top left corner of the watermark.

        Args:
            type (str): type of watermark, 'image' or 'text'.
            bbox (tuple[int,int,int,int] | None, optional): the border box of the watermark(text) on canvas. Defaults to None.
        """
        self.mark_offset_x_min = math.floor(self.mark.width() / 2)
        self.mark_offset_y_min = math.floor(self.mark.height() / 2)
        self.mark_offset_x_max = self.mark.width() - self.mark_offset_x_min
        self.mark_offset_y_max = self.mark.height() - self.mark_offset_y_min
        
    def text_mark_maker(self, event=None) -> None:
        """
        calculate text size by create a temporary text on canvas
        to get width, height, and calculate offset of the watermark,
        delete temporary text on canvas afterwards.
        
        bind('<ComboboxSelected>') somehow cause TypeError: 
        1. missing 1 required positional argument: 'event'
        2. takes 1 positional argument but 2 were given
        one will be raised, so added event=None in args, but that has no effect(fingers crossed).
        """
        self.validate_font()
        if self.selector_font.get() == 'select a font' and self.entry_font.get() == 'enter font':
            request_font = default_font[0]
        elif self.selector_font.get() != 'select a font':
            request_font = self.selector_font.get()
        elif self.entry_font.get() != 'enter font':
            if self.entry_font.get() in self.include_fonts:
                request_font = self.entry_font.get()
            else:
                request_font = default_font[0]

        self.current_font = (
            request_font, 
            self.user_enter_fontsize.get(), 
            self.selector_fontstyle.get())

        pixel_size = (self.current_font[1] / 0.75)
        fnt = ImageFont.truetype("arial.ttf", size=pixel_size) # TODO: get foo += ".ttf" & foo += "bi" / "bl" / "i" before this line
        
        # to get border of the text from PIL
        _ = Image.new("RGBA", text_watermark_max_size, (255, 255, 255, 0))
        f = ImageDraw.Draw(_)
        f_bbox = f.textbbox((0, 0), self.user_enter_text.get(), font=fnt)
        
        width = f_bbox[2] - f_bbox[0] + 2 + 5 # // offsets by eyeballing it. see source in root/test.py
        height = f_bbox[3] - f_bbox[1] + 5 # // offsets by eyeballing it
        
        # create the watermark from text
        with Image.new("RGBA", (width, height)).convert("RGBA") as base:
            txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(txt)
            
            offset = (3, -3) # // offsets by eyeballing it. see source in root/test.py
            alpha:int = round(np.round(255 * (self.scale_opaque.get() / 100)))
            text_color = 255, 0, 0, alpha # *self.current_font_rgb
            
            d.text(offset, self.user_enter_text.get(), font=fnt, fill=text_color)
            out = Image.alpha_composite(base, txt)
            out.save(watermark_fp)
        
        self.ghost = self.mark = self.proper_load(filepath=watermark_fp, type="text")
        
        x, y = round(self.canvas.winfo_width() / 2), round(self.canvas.winfo_height() / 2)
        temp = self.canvas.create_image(x, y, image=self.mark, anchor='center')
        bbox = self.canvas.bbox(temp)
        self.update_mark_offset(type='text', bbox=bbox)
        self.canvas.delete(temp)
        
        # TODO: change this to image
        self.lbl_watermark_text_preview = tk.Label(self.block_text_preview, image=self.mark, bg='white') # type: ignore
        self.lbl_watermark_text_preview.grid(column=1, row=5, sticky='w')
    
    def save_image(self) -> None:
        """
        save image with watermark, where the location of watermark is set by user,
        snap to border if watermark will be outside of image,
        image will be saved at root folder in project.
        """
        x_offset = self.mark_pil.width
        y_offset = self.mark_pil.height
        
        if self.snap:
            x = np.round(self.snap[0] * self.image_width_scale)
            y = np.round(self.snap[1] * self.image_height_scale)

            if self.snap[0] == self.image.width():
                x -= x_offset
            if self.snap[1] == self.image.height():
                y -= y_offset
        else:
            true_x = self.true_position[0] - self.mark_offset_x_min - self.image_datum_x
            true_y = self.true_position[1] - self.mark_offset_y_min - self.image_datum_y
            
            x = np.round(true_x * self.image_width_scale)
            y = np.round(true_y * self.image_height_scale)
        offset = (round(x), round(y))

        # width = np.round(self.mark.width() * self.image_height_scale)
        # height = np.round(self.mark.height() * self.image_width_scale)
        # size = (round(width), round(height))

        # resized_mark = self.mark_pil.resize(size)
        mark = self.mark_pil.copy()
        
        result_image = self.image_pil.copy()
        # result_image.paste(resized_mark, offset)
        result_image.alpha_composite(mark, offset)
        result_image.save("result.png", quality=100)
        
        # elif self.watermark_contain == 'text':
        #     if self.snap:
        #         x = np.round(self.snap[0] * self.image_width_scale)
        #         y = np.round(self.snap[1] * self.image_height_scale)
                
        #         if self.snap[0] == self.image.width():
        #             x -= self.text_width / 0.75
        #         if self.snap[1] == self.image.height():
        #             y -= self.text_height / 0.75
        #         print("save, position", (x, y))
        #         print(F"fomula = ({x} + {self.text_width}) / {self.image_width_scale}, ({y} + {self.text_height}) / {self.image_height_scale}")
        #         print(f"{(x + self.text_width) / self.image_width_scale, (y + self.text_height)/self.image_height_scale}")

        #     else:
        #         true_x = self.true_position[0] - self.text_offset_x_min - self.image_datum_x
        #         true_y = self.true_position[1] - self.text_offset_y_min - self.image_datum_y
                
        #         x = np.round(true_x * self.image_width_scale)
        #         y = np.round(true_y * self.image_height_scale)
                
        #     offset = (round(x), round(y))
            
        #     scale = (self.image_width_scale + self.image_height_scale) / 2
            
        #     text = self.user_enter_text.get()
        #     r, g, b = self.current_font_rgb
        #     alpha = round(np.round(255 * (self.scale_opaque.get() / 100)))
            
        #     rq_font, rq_fontsize, request_style = self.current_font # rq: requested
            
        #     size = (rq_fontsize * scale) / 0.75 # font size * 0.75 = pixel, ImageFont.truetype uses pixel
            
        #     # cite: https://stackoverflow.com/questions/1815165/draw-bold-italic-text-with-pil#comment136704224_1815170
        #     if request_style == "bold":
        #         rq_font += 'bd'
        #     elif request_style == "italic":
        #         rq_font += 'i'
        #     elif request_style == "bold and italic":
        #         rq_font += 'bi'
        #     rq_font += '.ttf'
        #     # print(rq_font.lower(), fontsize, alpha, self.scale_opaque.get())
        #     fnt = ImageFont.truetype(rq_font.lower(), size) 
            
        #     # cite: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#example-draw-partial-opacity-text
        #     with Image.open(self.filepath_image).convert("RGBA") as image:
        #         watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))

        #         d = ImageDraw.Draw(watermark)
        #         d.text(offset, text, font=fnt, fill=(r, g, b, alpha))
        #         d.circle(offset, radius=1, fill='red')
                
        #         result = Image.alpha_composite(image, watermark)
        #         result.save("result.png")
    
    # functions bind with command/action
    def switch_button(self) -> None:
        """
        switch watermark to image or text, not-the-current one,
        remove previous created watermark and preview.
        """
        self.btn_switch.config(image=self.switch_l) # type: ignore
        try:
            self.canvas.delete(self.canvas_mark_preview)
            self.canvas.delete(self.canvas_mark)
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
        elif type == 'text':
            ratio = min(self.image_width_scale, self.image_height_scale)
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def validate_font(self, event=None) -> None:
        """
        validate font from user, use messagebox to show error when font not exist.
        
        Args:
            event (_type_): see text_size_calculate()
        """
        user_enter = self.user_enter_font.get()
        if self.font_changed():
            if user_enter not in self.include_fonts:
                messagebox.showerror(
                    title="font not found.", 
                    message=f"font entered: '{user_enter}',\nmake sure everything was correct, or select one instead.")
            
    def font_changed(self) -> bool:
        if self.user_enter_font == self.user_enter_font_store and self.selector_font.get() == self.user_select_font_store:
            return False
        self.user_enter_font_store = self.user_enter_font
        self.user_select_font_store = self.selector_font.get()
        return True
    
    def choose_color(self) -> None:
        color_code = colorchooser.askcolor(title ="Choose a color") 
        if color_code[1] is not None:
            self.current_font_rgb, self.current_font_hexcolor = color_code
            self.lbl_watermark_text_preview.config(fg=self.current_font_hexcolor)
        else:
            self.current_font_hexcolor = 'black'
            
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
            self.canvas.delete(self.canvas_mark)
        elif method == 'motion':
            self.canvas.delete(self.canvas_mark_preview)
    
    def draw_watermark(self, x:int, y:int, method:str) -> None:
        """
        draw watermark on (x, y) in canvas, watermark type is determined by args:method.

        Args:
            x (int): x location to draw on the canvas.
            y (int): y location to draw on the canvas.
            method (str): user action, 'clicked' or 'motion'.
        """
        if method == 'clicked':
            self.canvas_mark = self.canvas.create_image(x, y, image=self.mark, anchor='nw')
        elif method == 'motion':
            self.canvas_mark_preview = self.canvas.create_image(x, y, image=self.ghost, anchor='nw')
       
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
        x_min = self.image_datum_x + self.mark_offset_x_min
        y_min = self.image_datum_y + self.mark_offset_y_min
        x_max = self.image_datum_x + self.image.width() - self.mark_offset_x_max
        y_max = self.image_datum_y + self.image.height() - self.mark_offset_y_max

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
        x_calibrate = mouse_loc[0] - self.mark_offset_x_min
        y_calibrate = mouse_loc[1] - self.mark_offset_y_min
        return x_calibrate, y_calibrate, snap_position
    

wm = WaterMarker()
wm.operate()