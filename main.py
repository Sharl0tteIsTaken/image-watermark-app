import tkinter as tk
import numpy as np
import math

import support_func

from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter
from string import ascii_letters
from tkinter import colorchooser, filedialog, font, messagebox, ttk

from typing import Literal
from typing_extensions import TypeAlias

# default key dimensions
window_width = 1400
window_height = 720

canvas_width = 860
canvas_height = 560
canvas_padx = 30
canvas_pady = 30

mark_width = 50
mark_height = 50

text_watermark_max_size = (2000, 2000)

default_font_fmt = ("Arial", 16, "normal")
default_font = 'Arial'
style = ['Regular', 'Narrow Bold Italic', 'Bold', 'Narrow Bold', 'Narrow Italic', 'Narrow', 'Bold Italic', 'Black', 'Italic'] 
default_style = sorted(style)

_state: TypeAlias = Literal["image", "text"]
_color: TypeAlias = Literal["mark bg", "text", "canvas"]
_img: TypeAlias = Literal["image", "mark", "text"]
_loc: TypeAlias = Literal["image", "canvas"]

grey = (128, 128, 128)

# border and offsets by eyeballing it
default_border_w = 7
default_border_h = 5
default_offset_w = 3
default_offset_h = -3

# TODO: make sure all docstring is updated, and if event have type
# TODO: add tooltip to everywhere nessary

watermark_fp = "custom_watermark.png" # TODO: [later] get these a location to stay
grid_fp = "watermark_grid.png"

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
        self.window.title("💧MarkIt.") # TODO: set color of 💧 to blue
        self.window.geometry(f"{window_width}x{window_height}")
        # self.window.resizable(width=False, height=False)
        self.window.option_add("*Font", default_font_fmt)
        self.window.config(background="white")
        
        self.setup_attribute()
        self.setup_variable()
        self.setup_labelframe()
        self.setup_widget()
        
        self.update_switch_button()
        self.load_default_image()
        self.text_mark_maker()
        
        self.window.option_add("*Dialog.msg.font", "Arial -16")
        
        
    def setup_attribute(self) -> None:
        """
        create every attribute for other functions.
        
        Include:
        - switch_state
        - text_calibrate
        """
        self.is_image = False
        self.is_mark = False
        
        self.switch_state:_state = "text" # TODO: [last] see how effective is this TypeAlias thing
        self.filepath_image:str = 'assets/img/default_image.png'
        self.filepath_mark:str|None = None
        
        self.mark_bg = grey
        self.canvas_bg = "grey"
        self.current_font_hexcolor = "black"
        self.current_font_rgb:tuple[int,int,int] = (0, 0, 0)
        
        self.fonts_dict:dict[str, dict[str, str]] = support_func.get_sysfont_sorted()
        self.font_names:list[str] = sorted(list(self.fonts_dict.keys()))
        
        self.grid_watermark:list[int] = []
        self.grid_watermark_preview:list[int] = []
        
    def setup_variable(self) -> None:
        """
        create every variable for widgets.
        
        Include:
        - user_enter_text
        """
        # usrntr = user enter
        self.usrntr_text = tk.StringVar() # TODO: order this
        self.usrntr_text.set("enter text as watermark")
        
        self.usrntr_fontsize = tk.IntVar()
        self.usrntr_fontsize.set(default_font_fmt[1])
        
        self.usrntr_border_w = tk.IntVar()
        self.usrntr_border_w.set(default_border_w)
        self.usrntr_border_h = tk.IntVar()
        self.usrntr_border_h.set(default_border_h)
        
        self.usrntr_offset_w = tk.IntVar()
        self.usrntr_offset_w.set(default_offset_w)
        self.usrntr_offset_h = tk.IntVar()
        self.usrntr_offset_h.set(default_offset_h)
        
        self.usrntr_rotate = tk.IntVar()
        self.usrntr_rotate.set(0)
        
        self.usrntr_scale = tk.IntVar()
        self.usrntr_scale.set(100)
        
        self.usrntr_opaque = tk.IntVar()
        self.usrntr_opaque.set(100)
        
        self.usrntr_grid = tk.IntVar()
        self.usrntr_grid.set(100)
        
        # checkbutton variables, set value after checkbutton is created
        self.show_mark_bg = tk.BooleanVar()
        self.show_preview = tk.BooleanVar()
        self.snap = tk.BooleanVar()
        self.show_cnvs_bg = tk.BooleanVar()
        self.grid = tk.BooleanVar()
        
        
        

    def setup_labelframe(self) -> None:
        """
        create and place every labelframe.
        
        Include:
        - block_image
        - block_panel
        """
        self.block_open = tk.LabelFrame(self.window, text="open file", bg="white",)
        self.block_open.grid(column=0, row=0, padx=10, pady=5, sticky='w')
        
        self.block_cnvs_lbl = tk.LabelFrame(self.window, bg="white", borderwidth=0)
        self.block_cnvs_lbl.grid(column=0, row=0, pady=(47, 0), rowspan=2, sticky='n')
        
        self.block_clear = tk.LabelFrame(self.window, text="remove in canvas", bg="white")
        self.block_clear.grid(column=0, row=0, padx=(0, 10), sticky='e')
        
        self.block_image = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_image.grid(column=0, row=1, padx=10, pady=(11, 0), rowspan=3, sticky='n')
        
        self.block_cnvs_ctrl = tk.LabelFrame(self.window, bg="white", borderwidth=0, pady=0, border=0, highlightthickness=0)
        self.block_cnvs_ctrl.grid(column=0, row=4, padx=(0, 10), sticky='ne')
        
        self.block_switch = tk.LabelFrame(self.window, text="💧mark with", bg="white")
        self.block_switch.grid(column=1, row=0, sticky='w')
        
        self.block_save = tk.LabelFrame(self.window, bg="white",)
        self.block_save.grid(column=1, row=0, pady=(0, 5), padx=(321, 0), sticky='sw')
        
        self.block_text = tk.LabelFrame(self.window, text="font of text", bg="white", padx=11, pady=2)
        self.block_text.grid(column=1, row=1, sticky='w')
        

        
        self.block_panel = tk.LabelFrame(self.window, text="watermark edit", bg="white", pady=2)
        self.block_panel.grid(column=1, row=2, sticky='nwe')
        
        self.block_mark_preview = tk.LabelFrame(self.window, text="watermark preview", bg="white", padx=10, pady=10)
        self.block_mark_preview.grid(column=1, row=3, pady=0, columnspan=2, sticky='nsew')
        self.window.rowconfigure(index=3, weight=1)
        # cite: https://stackoverflow.com/questions/45847313/what-does-weight-do-in-tkinter

    def load_default_image(self):
        # TODO: [later] move to load_asset() load asset for UI
        self.load_image()
        self.default_image_example = self.proper_load(filepath='assets/img/advanced_settings_example.png', type_='image', max_size=(400, 200))

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
        
        # block open
        self.btn_open_image = tk.Button(self.block_open, text="image", command=self.ask_image_path)
        self.btn_open_image.grid(column=0, row=0, padx=2, pady=2)
        
        self.btn_open_mark = tk.Button(self.block_open, text="watermark", command=self.ask_mark_path)
        self.btn_open_mark.grid(column=1, row=0, padx=2, pady=2)
        
        # block canvas label
        self.lbl_canvas = tk.Label(
            self.block_cnvs_lbl, 
            text="Canvas", font=("Segoe Print", 24, "normal"), 
            bg="white", borderwidth=0
            )
        self.lbl_canvas.pack()
        
        # block clear
        self.btn_clear_preview = tk.Button(
            self.block_clear, text="preview", 
            command= lambda: self.remove_exist_watermark(method='motion')
            )
        self.btn_clear_preview.grid(column=2, row=0, padx=2, pady=2)
        
        self.btn_clear_mark = tk.Button(
            self.block_clear, text="watermark", 
            command= lambda: self.remove_exist_watermark(method='clicked')
            )
        self.btn_clear_mark.grid(column=3, row=0, padx=2, pady=2)
        
        # block image
        self.canvas = tk.Canvas(self.block_image, bg='white', width=canvas_width, height=canvas_height)
        self.canvas.pack()
        
        # block canvas control
        self.ckbtn_preview = tk.Checkbutton(
            self.block_cnvs_ctrl, 
            text="show watermark preview", 
            variable=self.show_preview,
            command=self.update_canvas_bind,  
            bg='white', 
            )
        self.ckbtn_preview.select()
        self.ckbtn_preview.grid(column=0, row=0)
        
        self.ckbtn_snap = tk.Checkbutton(
            self.block_cnvs_ctrl, 
            text="snap watermark to border", 
            variable=self.snap,
            bg='white', 
            )
        self.ckbtn_snap.select()
        self.ckbtn_snap.grid(column=1, row=0)
        
        self.ckbtn_canvasbg = tk.Checkbutton(
            self.block_cnvs_ctrl, 
            text="show canvas background", 
            variable=self.show_cnvs_bg,
            command=self.update_canvas_bg,
            bg='white', 
            )
        self.ckbtn_canvasbg.deselect()
        self.ckbtn_canvasbg.grid(column=2, row=0)
        
        self.btn_cnvsbg_color = tk.Button(
            self.block_cnvs_ctrl, 
            text="color", 
            compound="center", padx=0, pady=0, 
            command=lambda: self.choose_color(tg="canvas"), 
            )
        self.btn_cnvsbg_color.grid(column=3, row=0)
        
        # block switch
        self.btn_switch_image = tk.Button(self.block_switch, text="image", command=self.image_mode)
        self.btn_switch_image.grid(column=0, row=0, padx=2, pady=2)
        
        self.btn_switch_text = tk.Button(self.block_switch, text="text", command=self.text_mode)
        self.btn_switch_text.grid(column=1, row=0, padx=2, pady=2)
        
        # block save
        self.btn_save = tk.Button(self.block_save, text='save', command=self.save_image)
        self.btn_save.grid(column=0, row=0, padx=2, pady=2)
        
        self.btn_apply = tk.Button(self.block_save, text='apply', command=self.save_image)
        self.btn_apply.grid(column=1, row=0, padx=2, pady=2)
        
        # block text
        row = 0
        self.lbl_text = tk.Label(self.block_text, text="text", bg='white')
        self.lbl_text.grid(column=0, row=row, pady=(0, 2), sticky='w')
        
        self.entry_text = tk.Entry(self.block_text, textvariable=self.usrntr_text, cursor='xterm', width=32) # TODO: add new line function
        self.entry_text.bind("<Button-1>", self.clear_tkentry_text)        
        self.entry_text.grid(column=1, row=row, sticky='w')
        
        # cite: https://stackoverflow.com/questions/66391266/is-it-possible-to-reduce-a-button-size-in-tkinter
        self.pixel = tk.PhotoImage(width=1, height=1)
        self.btn_clear_entry = tk.Button(
            self.block_text, 
            text="X", 
            bg="white", 
            border=0, 
            cursor="hand2", # TODO: change every button and checkbutton's cursor to hand2
            image=self.pixel, # add a transparent image to force tk.Button use pixels
            width=22, 
            height=22, 
            compound="center", 
            padx=0, pady=0, 
            command=lambda: self.usrntr_text.set(""),  
            )
        px = self.entry_text.winfo_reqwidth() - self.btn_clear_entry.winfo_reqwidth() - 1
        self.btn_clear_entry.grid(column=1, row=row, padx=(px, 0), sticky='w')
        
        row = 1
        self.lbl_font = tk.Label(self.block_text, text="font", bg='white')
        self.lbl_font.grid(column=0, row=row, pady=(0, 2),sticky='w')
        
        self.selector_font = ttk.Combobox(self.block_text, values=self.font_names, width=28)
        self.selector_font.set(default_font)
        self.selector_font.bind("<<ComboboxSelected>>", self.font_selected)
        self.selector_font.grid(column=1, row=row, sticky='w')
        
        row = 2
        self.lbl_fontstyle = tk.Label(self.block_text, text="style", bg='white')
        self.lbl_fontstyle.grid(column=0, row=row, pady=(0, 2), sticky='w')
        
        self.selector_fstyle = ttk.Combobox(self.block_text, values=default_style, width=11)
        self.selector_fstyle.set('Regular')
        self.selector_fstyle.bind("<<ComboboxSelected>>", self.text_mark_maker)
        self.selector_fstyle.grid(column=1, row=row, sticky='w')
        
        self.lbl_fontsize = tk.Label(self.block_text, text="size", bg='white')
        self.lbl_fontsize.grid(column=1, row=row, padx=(161, 0), sticky='w')
        
        self.spnbx_fontsize = tk.Spinbox(
            self.block_text, 
            from_=3, to=216, 
            command=self.text_mark_maker, 
            textvariable=self.usrntr_fontsize, 
            width=4)
        self.spnbx_fontsize.bind("<KeyRelease>", self.text_mark_maker)
        self.spnbx_fontsize.grid(column=1, row=row, padx=(210, 0), sticky='w')
        
        self.btn_color = tk.Button(
            self.block_text, 
            text="color", 
            width=55, height=23, 
            image=self.pixel, 
            compound="center", padx=0, pady=0, 
            command=lambda: self.choose_color(tg="text"), 
            )
        self.btn_color.grid(column=1, row=row, padx=(0, 30), pady=(2, 0), sticky='e')
        
        # block panel
        row = 0
        self.lbl_rotate = tk.Label(self.block_panel, text="rotate", bg='white')
        self.lbl_rotate.grid(column=0, row=row, padx=5, sticky='w')

         # FIXME: FormattedSpinbox() cause button of spinbox to shrink and detach
        self.spnbx_rotate = tk.Spinbox(
            self.block_panel, 
            from_=0, to=360, 
            wrap=True, 
            increment=45,
            textvariable=self.usrntr_rotate, 
            command=self.update_userequest, 
            width=8, 
            # symbol="°", 
            )
        self.spnbx_rotate.grid(column=1, row=row, sticky='w')
        
        self.lbl_scale = tk.Label(self.block_panel, text="scale", bg='white')
        self.lbl_scale.grid(column=2, row=row, padx=5, sticky='e')
 
        self.spnbx_scale = tk.Spinbox( # TODO: add tooltip: will cause text watermark to blurr.
            self.block_panel, 
            from_=10, to=1000, 
            increment=10,
            textvariable=self.usrntr_scale, 
            command=self.update_userequest,
            width=8, 
            # symbol="%"
            )
        self.spnbx_scale.bind("<KeyRelease>", self.update_userequest) # type: ignore
        self.spnbx_scale.grid(column=3, row=row, padx=4, sticky='e')
        
        row = 1
        self.lbl_opaque = tk.Label(self.block_panel, text="opaque", bg='white')
        self.lbl_opaque.grid(column=0, row=row, padx=0, sticky='w')
 
        self.scale_opaque = tk.Scale(
            self.block_panel, 
            from_=0, to=100, 
            orient='horizontal', 
            variable=self.usrntr_opaque, 
            command=self.update_userequest,  # type: ignore
            length=120, width=10, bg='white', 
            )
        self.scale_opaque.grid(column=1, row=row, sticky='w')
        
        # self.lbl_grid = tk.Label(self.block_panel, text="grid", bg='white')
        # self.lbl_grid.grid(column=2, row=row, padx=0, sticky='e')
        
        self.ckbtn_grid = tk.Checkbutton(
            self.block_panel, 
            text="grid", 
            variable=self.grid, 
            command=self.update_userequest,  # type: ignore
            bg='white')
        self.ckbtn_grid.grid(column=2, row=row, padx=0, sticky='e')
 
        self.scale_grid = tk.Scale(
            self.block_panel, 
            from_=0, to=1000, 
            orient='horizontal', 
            variable=self.usrntr_grid, 
            command=self.update_userequest, 
            length=120, width=10, bg='white', 
            )
        self.scale_grid.grid(column=3, row=row, sticky='e')
        
        # block preview
        self.lbl_watermark_preview = tk.Label(self.block_mark_preview, bg='white')
        self.lbl_watermark_preview.grid(column=0, row=0, sticky='w')
    
        # advanced settings button
        self.btn_adv_sets = tk.Button(self.window, text='advanced settings', width=17, command=self.adv_sets)
        self.btn_adv_sets.grid(column=1, row=4, padx=(249, 0), pady=(0, 20), sticky='w')
        # support_func.add_tool_tip(self.btn_confirm, ) # TODO: add show/unshow block_more and relief
    
    def adv_sets(self) -> None:
        # FIXME: when clickes button multiple time will generate multiple new window
        # FIXME: setting(s) will stay at default when reopened.
        self.window_tplvl = tk.Toplevel()
        self.window_tplvl.config(bg="light grey")
        
        # self.block_more = tk.LabelFrame(self.window_tplvl, bg="light grey", pady=2)
        # self.block_more.grid(column=1, row=3, padx=(165, 0), pady=(8, 0), sticky='nsew', rowspan=3)
        
        self.ckbtn_mark_bg = tk.Checkbutton(
            self.window_tplvl, 
            text="watermark background", 
            variable=self.show_mark_bg,
            command=self.text_mark_maker, 
            bg='light grey', 
            )
        self.ckbtn_mark_bg.deselect()
        self.ckbtn_mark_bg.grid(column=0, row=0, padx=(0, 15), sticky='w')
        
        self.btn_cnvsbg_color = tk.Button(
            self.window_tplvl, text="color", 
            command=lambda: self.choose_color(tg="mark bg"))
        self.btn_cnvsbg_color.grid(column=1, row=0, padx=(0, 7), sticky='e')
        
        # block more(advanced settings) 
        row = 2
        self.lbl_border_w = tk.Label(self.window_tplvl, text="adjust watermark  width (ΔW)", bg='light grey')
        self.lbl_border_w.grid(column=0, row=row, padx=(2, 0), sticky='w')
        
        self.spnbx_mark_w = tk.Spinbox(
            self.window_tplvl, 
            from_=-200, to=200, 
            command=self.text_mark_maker, 
            textvariable=self.usrntr_border_w, 
            width=5)
        self.spnbx_mark_w.bind("KeyRelease", self.text_mark_maker)
        self.spnbx_mark_w.grid(column=1, row=row, sticky='e')

        row = 3
        self.lbl_border_h = tk.Label(self.window_tplvl, text="adjust watermark height (ΔH)", bg='light grey')
        self.lbl_border_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        
        self.spnbx_mark_h = tk.Spinbox(
            self.window_tplvl, 
            from_=-200, to=200, 
            command=self.text_mark_maker, 
            textvariable=self.usrntr_border_h, 
            width=5)
        self.spnbx_mark_h.bind("KeyRelease", self.text_mark_maker)
        self.spnbx_mark_h.grid(column=1, row=row, sticky='e')
        
        row = 4
        self.lbl_offset_h = tk.Label(self.window_tplvl, text="adjust text position horizontal(Δh)", bg='light grey')
        self.lbl_offset_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        
        self.spnbx_offset_w = tk.Spinbox(
            self.window_tplvl, 
            from_=-200, to=200, 
            command=self.text_mark_maker, 
            textvariable=self.usrntr_offset_w, 
            width=5)
        self.spnbx_offset_w.bind("KeyRelease", self.text_mark_maker)
        self.spnbx_offset_w.grid(column=1, row=row, sticky='e')
        
        row = 5
        self.lbl_offset_v = tk.Label(self.window_tplvl, text="adjust text position vertical(Δv)", bg='light grey')
        self.lbl_offset_v.grid(column=0, row=row, padx=(2, 0), sticky='w')
        
        self.spnbx_offest_h = tk.Spinbox(
            self.window_tplvl, 
            from_=-200, to=200, 
            command=self.text_mark_maker, 
            textvariable=self.usrntr_offset_h, 
            width=5)
        self.spnbx_offest_h.bind("KeyRelease", self.text_mark_maker)
        self.spnbx_offest_h.grid(column=1, row=row, sticky='e')
        
        row = 6
        self.lbl_offset_example = tk.Label(self.window_tplvl, image=self.default_image_example) # type: ignore
        self.lbl_offset_example.grid(column=0, row=row, columnspan=2)
    
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
        type_:_img, 
        max_size:tuple[int,int]|None=None, 
        alpha:int|None=None, 
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
        
        self.watermark_type = type_
        if type_ == 'image':
            self.image_pil = image_pil
        elif type_ == 'mark':
            self.mark_pil = image_pil
        elif type_ == "text":
            self.mark_pil = image_pil
            width = np.round(image_pil.width / self.image_width_scale)
            height = np.round(image_pil.height / self.image_height_scale)
            size = (round(width), round(height))
        if type_ == "text":
            image_resize = image_pil.resize(size)
        else:
            image_resize = image_pil.resize(
                self.image_size_calculate(image_pil.width, image_pil.height, type_=type_, max_size=max_size)
                )
        img = image_resize.copy()
        
        # if user set the scale of watermark
        rq_scale = self.usrntr_scale.get() / 100
        if rq_scale != float(1):
            rq_width = np.round(image_resize.width * rq_scale)
            rq_height = np.round(image_resize.height * rq_scale)
            rq_size = (round(rq_width), round(rq_height))
            image_rqsize = image_resize.resize(rq_size)
            img = image_rqsize.copy()
        
        # if user set the opaqueness of watermark
        if alpha is not None:
            img.putalpha(alpha)
            if alpha == 0:
                img = Image.new("RGBA", (10, 10))
        
        return ImageTk.PhotoImage(img)
    
    def ask_image_path(self):
        self.filepath_image = "assets/img/200x200.png"
        # self.filepath_image = filedialog.askopenfilename()
        self.load_image()
        
    def load_image(self) -> None:
        """
        ask user filepath to load image,
        create the image on canvas and remove default(place holder) image.
        """
        # remove previous image
        if self.is_image:
            self.canvas.delete(self.canvas_image)
        
        self.image = self.proper_load(filepath=self.filepath_image, type_='image')
        self.image_width_scale = self.image_pil.width / self.image.width()
        self.image_height_scale = self.image_pil.height / self.image.height()
        
        # calculate where datum's(top left corner of image) position will be in the canvas.
        self.image_datum_x = math.floor((self.canvas.winfo_reqwidth() - self.image.width()) / 2)
        self.image_datum_y = math.floor((self.canvas.winfo_reqheight() - self.image.height()) / 2)
        
        # create image in canvas position at datum.
        self.canvas_image = self.canvas.create_image(self.image_datum_x, self.image_datum_y, image=self.image, anchor='nw')
        
        self.is_image = True
        
        if self.is_mark:
            self.update_mark_size()
            self.update_canvas_bind()
        
    def ask_mark_path(self) -> None:
        self.filepath_mark = 'assets/img/watermark.png'
        # self.filepath_mark = filedialog.askopenfilename()
        self.load_mark()
        
    def load_mark(self) -> None:
        """
        ask user filepath to load watermark,
        bind canvas with user action,
        calls to update watermark offset.
        """
        opaque = self.usrntr_opaque.get()
        alpha = round(np.round((opaque/100) * 255))
        
        angle = self.usrntr_rotate.get()
        if angle == 0:
            
            self.ghost = self.mark = self.proper_load(filepath=self.filepath_mark, type_='mark', alpha=alpha) # type: ignore
        else:
            img = Image.open(self.filepath_mark) # type: ignore
            img_rotate = img.rotate(angle=angle, expand=1)

            width = img.width
            height = img.height
            
            w, h = self.get_rotated_size(width, height, angle)
            base = Image.new("RGBA", (w, h))
            base.paste(img_rotate)
            base.save(watermark_fp)
            
            self.ghost = self.mark = self.proper_load(filepath=watermark_fp, type_='mark', alpha=alpha) # type: ignore
        self.update_mark_offset(type='image')
        self.update_canvas_bind()
        
        # update to image mode
        if self.switch_state == "text":
            self.image_mode()
        
        # update preview
        self.lbl_watermark_preview.config(image=self.mark) # type: ignore
        
    def update_canvas_bg(self) -> None:
        if self.show_cnvs_bg.get():
            self.canvas.config(bg=self.canvas_bg)
        else:
            self.canvas.config(bg="white")
        
                
    def update_canvas_bind(self) -> None:
        """
        if both watermark and image exist,
        bind M1 and mouse motion with function:self.canvas_action,
        set focus to canvas.
        """
        if self.is_mark and self.is_image:
            self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
            if self.show_preview.get():
                self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
            else:
                self.canvas.unbind("<Motion>")
            self.canvas.focus_set()
            self.remove_exist_watermark(method="motion")
            # ? UNKNOWN: will kept clicked watermark cause trouble when user load another image?
        
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
        
    def font_selected(self, event=None) -> None:
        rq_font = self.selector_font.get()
        
        self.selector_fstyle.config(background="white")
        style = sorted(list(self.fonts_dict[rq_font].keys()))
        priori = ["Regular", "regular"]
        for item in priori:
            if item in style:
                self.selector_fstyle['values'] = style
                self.selector_fstyle.set(item)
                self.text_mark_maker()
                break
        else:
            if len(style) == 1:
                self.selector_fstyle['values'] = style
                self.selector_fstyle.current(0)
                self.text_mark_maker()
            else:
                # font without "Regular" and "regular", and have more than one style,
                # use "Sitka" and "Perpetua Titling MT" to test
                # generate by __prnt_style_without_regular_()
                self.selector_fstyle['values'] = ['select a style']
                self.selector_fstyle.config(background="red")
                self.selector_fstyle.current(0)
                self.selector_fstyle['values'] = style
                messagebox.showinfo(
                    title="Wait a sec.", 
                    message="the font selected has more than one style, and no default value, please select one."
                    )
                
    def __prnt_style_without_regular_(self):
        font_dict = support_func.get_sysfont_sorted()
        for name in font_dict:
            all_style = []
            for style in font_dict[name]:
                all_style.append(style)
            if len(all_style) > 1:
                if "Regular" not in all_style and "regular" not in all_style:
                    print(name, font_dict[name])
        
    def update_userequest(self, event=None) -> None:
        print(self.switch_state)
        if self.switch_state == "image":
            self.load_mark()
        elif self.switch_state == "text":
            self.text_mark_maker()
        self.remove_exist_watermark(method="motion")
        
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
        name = self.selector_font.get()
        style = self.selector_fstyle.get()
        rq_font = self.fonts_dict[name][style] # rq: requested
        pixel_size = self.usrntr_fontsize.get() / 0.75

        fnt = ImageFont.truetype(font=rq_font, size=pixel_size) 
        
        # to get border of the text from PIL
        _ = Image.new("RGBA", text_watermark_max_size, (255, 255, 255, 0))
        f = ImageDraw.Draw(_)
        f_bbox = f.textbbox((0, 0), self.usrntr_text.get(), font=fnt)
        
        # get text border sizes of the text with font
        width = f_bbox[2] - f_bbox[0] + self.usrntr_border_w.get()
        height = f_bbox[3] - f_bbox[1] + self.usrntr_border_h.get()
        
        # get sizes of the text border when rotated
        angle = self.usrntr_rotate.get()
        w, h = self.get_rotated_size(width, height, angle)

        # create the watermark from text
        with Image.new("RGBA", (w, h)) as base: # use rotated size as base image
            # use original text border as container of text
            if self.show_mark_bg.get():
                txt = Image.new("RGBA", (width, height), (*self.mark_bg, 255))
            else:
                txt = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            d = ImageDraw.Draw(txt) # plain color image
            
            # user entered numbers
            offset = (self.usrntr_offset_w.get(), self.usrntr_offset_h.get())
            alpha:int = round(np.round(255 * (self.usrntr_opaque.get() / 100)))
            text_color = *self.current_font_rgb, alpha
            
            # draw text at offset in plain color image
            d.text(offset, self.usrntr_text.get(), font=fnt, fill=text_color)
            
            # rotate plain color image
            w = txt.rotate(angle,  expand=1)
            
            # paste plain color image onto base image
            base.paste(w)
            base.save(watermark_fp)

        # grid_space = self.usrntr_grid.get()
        # if grid_space == 100:
            # update watermarks
        self.ghost = self.mark = self.proper_load(filepath=watermark_fp, type_="text")
        # else:
            # self.grid_mark_maker(grid_space=grid_space)
            # self.ghost = self.mark = self.proper_load(filepath="watermark_grid.png", type_="text")
        
        # update wartermark offset
        x, y = round(self.canvas.winfo_reqwidth() / 2), round(self.canvas.winfo_reqheight() / 2)
        temp = self.canvas.create_image(x, y, image=self.mark, anchor='center')
        bbox = self.canvas.bbox(temp)
        self.update_mark_offset(type='text', bbox=bbox)
        self.canvas.delete(temp)
        
        # update to text mode
        if self.switch_state == 'image':
            self.text_mode()
        
        self.is_mark = True
        
        # update preview
        self.lbl_watermark_preview.config(image=self.mark) # type: ignore
    
    def grid_mark_maker(self, x:int, y:int, grid_space:int, mark:Image.Image) -> Image.Image:
        
        width = self.image_pil.width
        height = self.image_pil.height
        
        with Image.new("RGBA", (width, height)) as base:
            locs = self.grid_calculate(x, y, grid_space, on="image")
            base.paste(im=(255, 0, 0, 255), box=(x-2,y-2, x+2, y+2))
            print("locs", locs)
            for x in locs['x']:
                for y in locs['y']:
                    base.paste(im=self.mark_pil, box=(x,y))
            return base.copy()
    
    def grid_calculate(self, x:int, y:int, grid_space:int, on:_loc) -> dict[str, list[int]]:
        if on == "canvas":
            width = self.image.width() + self.mark.width()
            height = self.image.height() + self.mark.height()
            step = max(self.mark.width(), self.mark.height()) + grid_space
            x_max = self.canvas.winfo_reqwidth()
            y_max = self.canvas.winfo_reqheight()
        elif on == "image":
            width = self.image_pil.width + self.mark_pil.width
            height = self.image_pil.height + self.mark_pil.height
            scale = min(self.image_width_scale, self.image_height_scale)
            step = max(self.mark_pil.width, self.mark_pil.height) + round(grid_space * scale)
            x_max = width + step
            y_max = height + step
            
        if x != 0:
            x_min = x - (x // step + 1) * step
        else:
            x_min = 0
        if y != 0:
            y_min = y - (y // step + 1) * step
        else:
            y_min = 0
        x_locs = [x_loc for x_loc in range(x_min, x_max, step)]
        y_locs = [y_loc for y_loc in range(y_min, y_max, step)]
        
        return {
            "x": x_locs, 
            "y": y_locs, 
        }
        
    def get_rotated_size(self, width, height, angle):
        adj = width / 2
        opp = height / 2
        hyp = math.sqrt(adj**2 + opp**2)
        
        if angle in [0, 180, 360]:
            return width, height
        elif angle in [90, 270]:
            return height, width
        
        angle = angle % 180
        if angle > 90:
            angle = 90 - (angle - 90)
        
        hyp = math.sqrt(adj**2 + opp**2)
        equa = (adj**2 + hyp**2 - opp**2) / (2*adj*hyp)
        
        deg_a = math.degrees(math.acos(equa))
        deg_b = np.absolute(angle - deg_a)
        
        deg_c = (90 - angle) - deg_a
        deg_d = 90- deg_c
        
        width = round(math.ceil(math.cos(deg_b * (math.pi / 180)) * hyp * 2))
        height = round(math.ceil(math.sin(deg_d * (math.pi / 180)) * hyp * 2))
        return width, height
    
    def save_image(self) -> None:
        """
        save image with watermark, where the location of watermark is set by user,
        snap to border if watermark will be outside of image,
        image will be saved at root folder in project.
        """
        if self.show_mark_bg.get():
            save = messagebox.askyesno(
                title="Hold up.", 
                message="the background of watermark preview will also appear in the result image, still want to save the image?", 
                )
            if not save:
                return
        
        x_offset = self.mark_pil.width
        y_offset = self.mark_pil.height
        
        if self.snap and self.snap_position:
            x, y = self.snap_position
            if self.snap_position[0] == self.image_pil.width:
                x -= x_offset
            if self.snap_position[1] == self.image_pil.height:
                y -= y_offset
        else:
            true_x = self.true_position[0] - self.mark_offset_x_min - self.image_datum_x
            true_y = self.true_position[1] - self.mark_offset_y_min - self.image_datum_y
            
            x = np.round(true_x * self.image_width_scale)
            y = np.round(true_y * self.image_height_scale)
        offset = (round(x), round(y))
        
        mark = self.mark_pil.copy()
        width = np.round(self.mark.width() * self.image_width_scale)
        height = np.round(self.mark.height() * self.image_height_scale)
        size = (round(width), round(height))
        resized_mark = mark.resize(size)
        
        if self.grid.get():
            grid_space = self.usrntr_grid.get()
            mark = self.grid_mark_maker(round(x), round(y), grid_space, resized_mark)
            result_mark = mark.copy()
            offset = 0, 0
        else:
            result_mark = resized_mark.copy()
            
        result_image = self.image_pil.copy()
        result_image.alpha_composite(result_mark, offset)
        result_image.save("result.png")
        
    # functions bind with command/action # TODO: [last] sort this
    def image_mode(self) -> None:
        self.switch_state = 'image'
        if self.filepath_mark is None:
            self.btn_switch_text.config(relief='sunken')
            messagebox.showwarning(title="Missing something", message="open a image file for watermark first!")
        else:
            self.load_mark()
            self.update_switch_button()
        
    def text_mode(self) -> None:
        self.switch_state = 'text'
        self.update_switch_button()
        self.text_mark_maker()
        
    def update_switch_button(self) -> None:
        """
        switch watermark to image or text, not-the-current one,
        remove previous created watermark and preview.
        """
        if self.switch_state == 'image':
            self.btn_switch_image.config(relief='sunken')
            self.btn_switch_text.config(relief='raised')
        elif self.switch_state == 'text':
            self.btn_switch_image.config(relief='raised')
            self.btn_switch_text.config(relief='sunken')
        try:
            self.canvas.delete(self.canvas_mark_preview)
            self.canvas.delete(self.canvas_mark)
        except AttributeError:
            print("making sure to remove unwanted watermarks")
    
    def clear_tkentry_text(self, event=None) -> None:
        """
        remove default text in tk.Entry, when user click in tk.Entry
        and bind M1 to function:self.entry_action.

        Args:
            event (_type_): _description_ 
        """
        self.usrntr_text.set("")
        self.entry_text.unbind("<Button-1>")
        self.entry_text.bind("<KeyRelease>", self.text_mark_maker)

    def canvas_action(self, event, *, method:str) -> None:
        """
        main function in responce for user action in canvas,
        manage everything after click and mouse movement.

        Args:
            event (_type_): _description_ 
            method (str): user action on canvas, 'clicked' or 'motion'.
        """
        try:
            self.remove_exist_watermark(method=method)
        except AttributeError:
            print("first time only AttributeError, no worries.")
            
        x0, y0 = event.x, event.y
        x, y, snap_position = self.mouse_loc_calibrate(x0, y0) 
        
        if method == 'clicked' and self.snap:
            self.snap_position:tuple[int,int]|None = snap_position
            self.true_position:tuple[int, int] = x0, y0
            
        if self.grid.get():
            grid_space = self.usrntr_grid.get()
            locs = self.grid_calculate(x, y, grid_space, on="canvas")
            for x_loc in locs["x"]:
                for y_loc in locs["y"]:
                    self.draw_watermark(x_loc, y_loc, method=method, grid=True)
        else:
            self.draw_watermark(x, y, method=method)
        
    
    # support functions
    def image_size_calculate(self, width:int, height:int, *, type_:_img, max_size:tuple[int,int]|None=None) -> tuple[int, int]:
        """
        calculate size of image to have a set blank border in canvas, which will use later to resize image. 

        Args:
            width (int): original width of the image.
            height (int): original height of the image.
            type (str): type of the image, 'image' or 'mark'.

        Returns:
            tuple[int, int]: calculated width and height to meet one and/or both of the requirement of the canvas(to have a set blank border).
        """
        if max_size:
            wid, hei = max_size
            w = wid / width
            h = hei / height
        elif type_ == 'image':
            w = (self.canvas.winfo_reqwidth() - canvas_padx * 2) / width
            h = (self.canvas.winfo_reqheight() - canvas_pady * 2) / height
        elif type_ == 'mark':
            w = mark_width / width
            h = mark_height / height
        elif type_ == 'text':
            w = self.image_width_scale
            h = self.image_height_scale
        ratio:float = min(w, h) 
        size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        return size
    
    def choose_color(self, tg:_color) -> None:
        color_code = colorchooser.askcolor(title ="Choose a color")
        if tg == "text":
            if color_code[1] is not None:
                self.current_font_rgb, self.current_font_hexcolor = color_code
                self.lbl_watermark_preview.config(fg=self.current_font_hexcolor)
                self.text_mark_maker()
        elif tg == "mark bg":
            if color_code[0] is not None:
                self.mark_bg, _ = color_code
            else:
                self.mark_bg = grey
            self.text_mark_maker()
        elif tg == "canvas":
            if color_code[1] is not None:
                _, self.canvas_bg = color_code
                self.update_canvas_bg()
            
    def remove_exist_watermark(self, method:str) -> None:
        """
        remove watermark on canvas by following:
        1. remove previous previews
        2. remove previous watermark when user clicked on canvas
        3. remove all not-the-current watermark and preview
        

        Args:
            method (str): user action, 'clicked' or 'motion'.
        """
        try:
            if method == 'clicked':
                self.canvas.delete(self.canvas_mark)
            elif method == 'motion':
                self.canvas.delete(self.canvas_mark_preview)
        except AttributeError:
            print("making sure to remove unwanted watermarks")
        
        if self.grid.get() and method == 'clicked':
            for item in self.grid_watermark:
                self.canvas.delete(item)
        elif self.grid.get() and method == 'motion':
            for item in self.grid_watermark_preview:
                self.canvas.delete(item)
    
    def draw_watermark(self, x:int, y:int, method:str, grid:bool=False) -> None:
        """
        draw watermark on (x, y) in canvas, watermark type is determined by args:method.

        Args:
            x (int): x location to draw on the canvas.
            y (int): y location to draw on the canvas.
            method (str): user action, 'clicked' or 'motion'.
        """
        if method == 'clicked':
            self.canvas_mark = self.canvas.create_image(x, y, image=self.mark, anchor='nw')
            if grid:
                self.grid_watermark.append(self.canvas_mark)
        elif method == 'motion':
            self.canvas_mark_preview = self.canvas.create_image(x, y, image=self.ghost, anchor='nw')
            if grid:
                self.grid_watermark_preview.append(self.canvas_mark_preview)

       
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
        x_min = self.image_datum_x + self.mark_offset_x_min
        y_min = self.image_datum_y + self.mark_offset_y_min
        x_max = self.image_datum_x + self.image.width() - self.mark_offset_x_max
        y_max = self.image_datum_y + self.image.height() - self.mark_offset_y_max
        snap_position = None
        print(x, y)
        if x_max >= x >= x_min and y_max >= y >= y_min or not self.snap.get(): # in image
            mouse_loc = x, y
        elif x <= x_min and y <= y_min: # top left corner
            mouse_loc = x_min, y_min
            snap_position = (0, 0)
        elif x >= x_max and y <= y_min: # top right corner
            mouse_loc = x_max, y_min
            snap_position = (self.image_pil.width, 0)
        elif x <= x_min and y >= y_max: # btm left corner
            mouse_loc = x_min, y_max
            snap_position = (0, self.image_pil.height)
        elif x >= x_max and y >= y_max: # btm right corner
            mouse_loc = x_max, y_max
            snap_position = (self.image_pil.width, self.image_pil.height)
        elif x_max >= x >= x_min and y <= y_min: # top border
            mouse_loc = x, y_min
            x_loc = np.round((x - self.mark_offset_x_min - self.image_datum_x) * self.image_width_scale)
            snap_position = round(x_loc), 0
        elif x_max >= x >= x_min and y >= y_max: # btm border
            mouse_loc = x, y_max
            x_loc = np.round((x - self.mark_offset_x_min - self.image_datum_x) * self.image_width_scale)
            snap_position = round(x_loc), self.image_pil.height
        elif x <= x_min and y_max >= y >= y_min: # left border
            mouse_loc = x_min, y
            y_loc = np.round((y - self.mark_offset_y_min - self.image_datum_y) * self.image_height_scale)
            snap_position = 0, round(y_loc)
        elif x >= x_max and y_max >= y >= y_min: # right border
            mouse_loc = x_max, y
            y_loc = np.round((y - self.mark_offset_y_min - self.image_datum_y) * self.image_height_scale)
            snap_position = self.image_pil.width, round(y_loc)
        else:
            raise ValueError(f"\
                mind blown, clicked at (x:{x}, y:{y}), not in elif tree?\n\
                image size: ({self.image.width()}x{self.image.height()})\n\
                datum at (x:{self.image_datum_x}, y:{self.image_datum_y})\n\
                x min max: {x_min}, {x_max}\n\
                y min max: {y_min}, {y_max}\n\
                never thought this will occur, add any missed info to mouse_loc_calibrate().")
        print(snap_position)
        x_calibrate = mouse_loc[0] - self.mark_offset_x_min
        y_calibrate = mouse_loc[1] - self.mark_offset_y_min
        return x_calibrate, y_calibrate, snap_position
    

wm = WaterMarker()
wm.operate()