import tkinter as tk
import numpy as np
import math, os

import support_func as sf

from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkinter import colorchooser, filedialog, messagebox, ttk

from typing import Literal
from typing_extensions import TypeAlias
# TODO: check import orders


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
gray = (128, 128, 128)

# border and offsets by eyeballing it
default_border_w = 7
default_border_h = 5
default_offset_w = 3
default_offset_h = -3

# default font related stuff
default_font_fmt = ("Arial", 16, "normal")
default_font = 'Arial'
style = ['Regular', 'Narrow Bold Italic', 'Bold', 'Narrow Bold', 'Narrow Italic', 'Narrow', 'Bold Italic', 'Black', 'Italic'] 
default_style = sorted(style)

# file related stuff
file_type = ((".png", "*.png"), (".jpg", "*.jpg"), (".jpeg", "*.jpeg"))

_state: TypeAlias = Literal["image", "text"]
_color: TypeAlias = Literal["mark bg", "text", "canvas"]
_img: TypeAlias = Literal["image", "mark", "text", "icon"]
_loc: TypeAlias = Literal["image", "canvas"]
_rstable: TypeAlias = Literal["rotate", "scale", "opaque", "grid", "advset"]
_dft_key: TypeAlias = Literal["attr_name", "default_val"] # dft_key = default_key
_ckbtn_switch: TypeAlias = Literal["format", "rename"]
_msgbx: TypeAlias = Literal["btnf_image_mode", "btnf_save", "btnf_apply", "apply_to_folder"]

# TODO: make sure all docstring is updated, and if event have type

class WaterMarker():
    """
    watermark picture with a image or text, watermark can be scaled proportionally,
    if watermark is placed at the border of the picture, it's snapped to that position,
    change of scale, font, fontsize or text won't effect the position.
    use .operate() to boot everything:
    
    Example:
     >>> wm = WaterMarker()
     >>> wm.operate()
     
    """
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("💧MarkIt.")
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.config(background="white")
        # self.window.resizable(width=False, height=False)
        
        self.validator_spnbx = (self.window.register(self.spnbx_val_validate), "%P")
        self.tip = sf.TipManager()
        
        self.setup_option()
        self.setup_attribute()
        self.setup_variable()
        self.setup_labelframe()
        self.setup_widget()
        self.load_defaults()
        self.setup_rstble()
        
        self.window.update()
        
        self.awake_custom()
        self.tip.enable_all()
        
        
    def setup_option(self) -> None:
        # must set before widgets are created, cite: https://tcl.tk/man/tcl8.6/TkCmd/option.html
        self.window.option_add("*Font", default_font_fmt)
        self.window.option_add("*Button.cursor", "hand2")
        self.window.option_add("*Checkbutton.cursor", "hand2")
        self.window.option_add("*Spinbox.buttonCursor", "hand2")
        
        # self.window.option_add("*Combobox.cursor", "hand2") # not working
        
        # self.window.option_add("*Dialog.msg.font", 'Helvetica 30') # not working
        # explanation: https://stackoverflow.com/questions/53694345/how-to-change-font-size-of-messages-inside-messagebox-showinfomessage-hello
        # tcl cite: https://wiki.tcl-lang.org/page/tk%5FmessageBox
        
    def setup_attribute(self) -> None:
        """
        create every attribute for other functions.
        
        Include:
        - switch_state
        - text_calibrate
        """
        self.is_image = False
        self.is_mark = False
        
        self.switch_state:_state = "text"
        self.filepath_image:str = 'assets/img/default_image.png'
        self.filepath_mark:str|None = None
        
        self.mark_bg = gray
        self.canvas_bg = "gray"
        self.current_font_hexcolor = "black"
        self.current_font_rgb:tuple[int,int,int] = (0, 0, 0)
        
        self.fonts_dict:dict[str, dict[str, str]] = sf.get_sysfont_sorted()
        self.font_names:list[str] = sorted(list(self.fonts_dict.keys()))
        
        self.grid_watermark:list[int] = []
        self.grid_watermark_preview:list[int] = []
        
        self.apply_paths:list[str] = []
        
    def setup_variable(self) -> None:
        """
        create every variable for widgets.
        
        Include:
        - user_enter_text
        """
        # usrntr = user enter
        self.usrntr_fontsize = tk.IntVar()
        self.usrntr_fontsize.set(default_font_fmt[1])
        
        self.usrntr_rotate = tk.IntVar()
        self.usrntr_rotate.set(0)
        
        self.usrntr_scale = tk.DoubleVar()
        self.usrntr_scale.set(1)
        
        self.usrntr_opaque = tk.IntVar()
        self.usrntr_opaque.set(100)
        
        self.usrntr_grid = tk.IntVar()
        self.usrntr_grid.set(100)
        
        self.usrntr_border_w = tk.IntVar()
        self.usrntr_border_w.set(default_border_w)
        self.usrntr_border_h = tk.IntVar()
        self.usrntr_border_h.set(default_border_h)
        
        self.usrntr_offset_w = tk.IntVar()
        self.usrntr_offset_w.set(default_offset_w)
        self.usrntr_offset_h = tk.IntVar()
        self.usrntr_offset_h.set(default_offset_h)
        
        self.usrntr_shift_h = tk.IntVar()
        self.usrntr_shift_h.set(0)
        self.usrntr_shift_v = tk.IntVar()
        self.usrntr_shift_v.set(0)
        
        self.save_dir = tk.StringVar()
        self.save_dir.set("file save directory missing.")
        
        self.fname_prefix = tk.StringVar()
        self.fname_prefix.set("Before-")
        self.fname_suffix = tk.StringVar()
        self.fname_suffix.set("-After")
        
        self.fname_name = tk.StringVar()
        self.fname_name.set("Name")
        self.fname_example = tk.StringVar()
        
        # checkbutton variables, set value after checkbutton is created
        self.ckbtnvr_grid = tk.BooleanVar()
        self.ckbtnvr_show_preview = tk.BooleanVar()
        self.ckbtnvr_snap = tk.BooleanVar()
        self.ckbtnvr_show_cnvs_bg = tk.BooleanVar()
        self.ckbtnvr_show_mark_bg = tk.BooleanVar()
        self.ckbtnvr_wrng_mark_bg = tk.BooleanVar(value=True)
        self.ckbtnvr_fname_fmt = tk.BooleanVar(value=True)
        self.ckbtnvr_fname_rename = tk.BooleanVar()
        self.ckbtnvr_tooltip = tk.BooleanVar(value=True)
        
        # other icons
        self.guicon_files = ImageTk.PhotoImage(Image.open("assets/img/files.png"))
        self.guicon_folder = ImageTk.PhotoImage(Image.open("assets/img/folder.png"))
        self.guicon_reset = ImageTk.PhotoImage(Image.open("assets/img/arrow-counterclockwise.png"))


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
        
        self.block_canvas = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_canvas.grid(column=0, row=1, padx=10, pady=(11, 0), rowspan=3, sticky='n')
        
        self.block_cnvs_ctrl = tk.LabelFrame(self.window, bg="white", borderwidth=0, pady=0, border=0, highlightthickness=0)
        self.block_cnvs_ctrl.grid(column=0, row=4, padx=(0, 10), sticky='ne')
        
        self.block_switch = tk.LabelFrame(self.window, text="💧mark with", bg="white")
        self.block_switch.grid(column=1, row=0, sticky='w')
        
        self.block_save = tk.LabelFrame(self.window, bg="white",)
        self.block_save.grid(column=1, row=0, pady=(0, 5), padx=(321, 0), sticky='sw')
        
        self.block_text = tk.LabelFrame(self.window, text="font of text", bg="white", padx=11, pady=2)
        self.block_text.grid(column=1, row=1, sticky='w')

        self.block_panel = tk.LabelFrame(self.window, text="watermark edit", bg="white", pady=2)
        self.block_panel.grid(column=1, row=2, sticky='nw')
        
        self.block_preview = tk.LabelFrame(self.window, text="watermark preview", bg="white", padx=10, pady=10)
        self.block_preview.grid(column=1, row=3, pady=0, columnspan=2, sticky='nsew')
        
        self.block_advset = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_advset.grid(column=1, row=4, pady=(0, 20), sticky='new')
        
        self.window.rowconfigure(index=3, weight=1)
        # cite: https://stackoverflow.com/questions/45847313/what-does-weight-do-in-tkinter
    
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
        self.btn_open_image = tk.Button(self.block_open, text="image", command=self.btnf_load_image_path)
        self.btn_open_image.grid(column=0, row=0, rowspan=2, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_open_image, 
            text="open and select a image file to add watermark.", 
        )
        
        self.btn_open_images = tk.Button(
            self.block_open, 
            image=self.guicon_files, # type: ignore
            command=self.btnf_load_images_path
            )
        self.btn_open_images.grid(column=1, row=0, padx=2, pady=0)
        self.tip.add_to_queue(
            self.btn_open_images, 
            text="open and select multiple image files to add watermark.", 
        )
        
        self.btn_open_folder = tk.Button(
            self.block_open, 
            image=self.guicon_folder, # type: ignore
            command=self.btnf_load_folder_path
            )
        self.btn_open_folder.grid(column=1, row=1, padx=2, pady=0)
        self.tip.add_to_queue(
            self.btn_open_folder, 
            text='open and select a folder to add watermark.\naccepts "png", "jpg", "jpeg" files.', 
        )
        
        self.btn_open_mark = tk.Button(self.block_open, text="watermark", command=self.btnf_load_mark_path)
        self.btn_open_mark.grid(column=2, row=0, rowspan=2, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_open_mark, 
            text='open and select a image file to be watermark.', 
        )
        
        # block canvas label
        self.lbl_canvas = tk.Label(
            self.block_cnvs_lbl, 
            text="Canvas", font=("Segoe Print", 24, "normal"), 
            bg="white", borderwidth=0
            )
        self.lbl_canvas.pack()
        self.tip.add_to_queue(
            self.btn_open_mark, 
            text='open and select a image file to be watermark.', 
        )
        
        # block clear
        self.btn_clear_preview = tk.Button(
            self.block_clear, text="preview", 
            command= lambda: self.remove_exist_watermark(method='motion')
            )
        self.btn_clear_preview.grid(column=2, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_clear_preview, 
            text='remove preview watermark in canvas.', 
        )
        
        self.btn_clear_mark = tk.Button(
            self.block_clear, text="watermark", 
            command= lambda: self.remove_exist_watermark(method='clicked')
            )
        self.btn_clear_mark.grid(column=3, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_clear_mark, 
            text='remove watermark in canvas.', 
        )
        
        # block image
        self.canvas = tk.Canvas(self.block_canvas, bg='white', width=canvas_width, height=canvas_height)
        self.canvas.pack()
        
        # block canvas control
        self.ckbtnbrdr_preview = tk.Frame(self.block_cnvs_ctrl, bg="light gray") # ckbtnbrdr: checkbuttonborder
        self.ckbtn_preview = tk.Checkbutton(
            self.ckbtnbrdr_preview, 
            text="show watermark preview", 
            variable=self.ckbtnvr_show_preview,
            command=self.update_canvas_bind,  
            bg='white', 
            )
        self.ckbtn_preview.select()
        self.ckbtn_preview.pack(padx=1, pady=1)
        self.ckbtnbrdr_preview.grid(column=0, row=0)
        
        self.ckbtnbrdr_snap = tk.Frame(self.block_cnvs_ctrl, bg="light gray")
        self.ckbtn_snap = tk.Checkbutton(
            self.ckbtnbrdr_snap, 
            text="snap watermark to border", 
            variable=self.ckbtnvr_snap,
            bg='white', 
            )
        self.ckbtn_snap.select()
        self.ckbtn_snap.pack(padx=1, pady=1)
        self.ckbtnbrdr_snap.grid(column=1, row=0)
        self.tip.add_to_queue(
            self.ckbtn_snap, 
            text='enable/disable restrict watermark to stay inside image.', 
            side="tr", 
        )
        
        self.ckbtnbrdr_canvasbg = tk.Frame(self.block_cnvs_ctrl, bg="light gray")
        self.ckbtn_canvasbg = tk.Checkbutton(
            self.ckbtnbrdr_canvasbg, 
            text="show canvas background", 
            variable=self.ckbtnvr_show_cnvs_bg,
            command=self.update_canvas_bg,
            bg='white', 
            )
        self.ckbtn_canvasbg.deselect()
        self.ckbtn_canvasbg.pack(padx=1, pady=1)
        self.ckbtnbrdr_canvasbg.grid(column=2, row=0)
        
        self.btn_cnvsbg_color = tk.Button(
            self.block_cnvs_ctrl, 
            text="color", 
            compound="center", padx=0, pady=0, 
            command=lambda: self.choose_color(tg="canvas"), 
            )
        self.btn_cnvsbg_color.grid(column=3, row=0)
        self.tip.add_to_queue(
            self.btn_cnvsbg_color, 
            text='select color of canvas background,\nuses light gray if canceled.', 
            side="tr", 
        )
        
        # block switch
        self.btn_switch_image = tk.Button(self.block_switch, text="image", command=self.btnf_image_mode)
        self.btn_switch_image.grid(column=0, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_switch_image, 
            text='switch to use image as watermark.', 
        )
        
        self.btn_switch_text = tk.Button(self.block_switch, text="text", command=self.btnf_text_mode)
        self.btn_switch_text.grid(column=1, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_switch_text, 
            text='switch to use text as watermark.', 
        )
        
        # block save
        self.btn_save = tk.Button(self.block_save, text='save', command=self.btnf_save)
        self.btn_save.grid(column=0, row=0, padx=2, pady=2)
        
        self.btn_apply = tk.Button(self.block_save, text='apply', command=self.btnf_apply)
        self.btn_apply.grid(column=1, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_apply, 
            text='add watermark to all files selected,\nwatermark will be placed at relatively the same location.', 
            side="bl"
        )
        
        # block text
        row = 0
        self.lbl_text = tk.Label(self.block_text, text="text", bg='white')
        self.lbl_text.grid(column=0, row=row, pady=(0, 2), sticky='w')
        
        self.tktxt_entry = tk.Text(self.block_text, cursor='xterm', width=32, height=1)
        self.tktxt_entry.insert(0.0, "enter text as watermark")
        self.tktxt_entry.bind("<Button-1>", self.clear_tkentry_text)        
        self.tktxt_entry.grid(column=1, row=row, sticky='w')
        
        # cite: https://stackoverflow.com/questions/66391266/is-it-possible-to-reduce-a-button-size-in-tkinter
        self.pixel = tk.PhotoImage(width=1, height=1)
        self.btn_clear_tktxt = tk.Button(
            self.block_text, 
            text="X", 
            command=lambda: (self.tktxt_entry.delete(0.0, tk.END), self.text_mark_maker()), 
            image=self.pixel, compound="center", # add a transparent image to force tk.Button use pixels
            bg="white", 
            border=0, width=22, height=22, padx=0, pady=0, 
            )
        px = self.tktxt_entry.winfo_reqwidth() - self.btn_clear_tktxt.winfo_reqwidth() - 1
        self.btn_clear_tktxt.grid(column=1, row=row, padx=(px, 0), sticky='w')
        
        row = 1
        self.lbl_font = tk.Label(self.block_text, text="font", bg='white')
        self.lbl_font.grid(column=0, row=row, pady=(0, 2),sticky='w')
        
        self.cmbbx_font = ttk.Combobox(
            self.block_text, 
            values=self.font_names, 
            state="readonly", 
            cursor="hand2", 
            width=28
            )
        self.cmbbx_font.set(default_font)
        self.cmbbx_font.bind("<<ComboboxSelected>>", self.font_selected)
        self.cmbbx_font.grid(column=1, row=row, sticky='w')
        
        row = 2
        self.lbl_fontstyle = tk.Label(self.block_text, text="style", bg='white')
        self.lbl_fontstyle.grid(column=0, row=row, pady=(0, 2), sticky='w')
        
        self.cmbbx_fontstyle = ttk.Combobox(
            self.block_text, 
            values=default_style, 
            state="readonly", 
            cursor="hand2", 
            width=11
            )
        self.cmbbx_fontstyle.set('Regular')
        self.cmbbx_fontstyle.bind("<<ComboboxSelected>>", self.text_mark_maker)
        self.cmbbx_fontstyle.grid(column=1, row=row, sticky='w')
        
        self.lbl_fontsize = tk.Label(self.block_text, text="size", bg='white')
        self.lbl_fontsize.grid(column=1, row=row, padx=(161, 0), sticky='w')
        
        self.spnbx_fontsize = tk.Spinbox(
            self.block_text, 
            from_=3, to=216, 
            command=self.text_mark_maker, 
            textvariable=self.usrntr_fontsize, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=4
            )
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
        self.tip.add_to_queue(
            self.btn_color, 
            text='select font color of text,\nuses light gray if canceled.', 
            side="bl"
        )
        
        # block panel
        row = 0
        self.lbl_rotate = tk.Label(self.block_panel, text="rotate", bg='white')
        self.lbl_rotate.grid(column=0, row=row, padx=5, sticky='e')
        self.tip.add_to_queue(
            self.lbl_rotate, 
            text='rotate the watermark,\nworks with mode text and image.', 
        )
        
        self.spnbx_rotate = tk.Spinbox(
            self.block_panel, 
            from_=0, to=360, 
            increment=45,
            textvariable=self.usrntr_rotate, 
            command=self.update_userequest, 
            validate="key", validatecommand=self.validator_spnbx, 
            wrap=True, width=8, 
            )
        self.spnbx_rotate.bind("<KeyRelease>", self.text_mark_maker)
        self.spnbx_rotate.grid(column=1, row=row)
        
        self.btnrst_rotate = tk.Button(
            self.block_panel, 
            image=self.guicon_reset, # type: ignore
            command=lambda: self.reset_usrntr(func="rotate"), 
            bg="white"
            )
        self.btnrst_rotate.grid(column=2, row=row)
        self.tip.add_to_queue(
            self.btnrst_rotate, 
            text="resets the value of rotate.", 
        )
        
        self.lbl_scale = tk.Label(self.block_panel, text="scale", bg='white')
        self.lbl_scale.grid(column=3, row=row, padx=(32, 0))
        self.tip.add_to_queue(
            self.lbl_scale, 
            text="scales the watermark, may cause blurry watermark,\npixels of misplacement or size difference.", 
            side="bl", 
        )

        self.tick_scale = tk.IntVar(value=0)
        self.scale_scale = sf.CustomScale(
            self.block_panel, 
            from_=-90, to=90, 
            tickinterval=0.1, 
            variable=self.tick_scale, 
            cz_variable = self.tick_scale, 
            cmd=self.update_userequest,
            length=110, width=10, 
            orient='horizontal', bg='white', 
            )
        self.usrntr_scale = self.scale_scale.result
        self.scale_scale.bind("<Button-1>", self.scale_scale.command)
        self.scale_scale.grid(column=4, row=row, padx=4, sticky='e')
        
        self.btnrst_scale = tk.Button(
            self.block_panel, 
            image=self.guicon_reset, # type: ignore
            command=lambda: self.reset_usrntr(func="scale"), 
            bg="white"
            )
        self.btnrst_scale.grid(column=5, row=row, padx=(0, 5))
        self.tip.add_to_queue(
            self.btnrst_scale, 
            text="resets the value of scale.", 
            side="bl"
            )
        
        row = 1
        self.lbl_opaque = tk.Label(self.block_panel, text="opaque", bg='white')
        self.lbl_opaque.grid(column=0, row=row, padx=0)
        self.tip.add_to_queue(
            self.lbl_opaque, 
            text="set the opaqueness of watermark.", 
        )
        
        self.scale_opaque = tk.Scale(
            self.block_panel, 
            from_=0, to=100, 
            variable=self.usrntr_opaque, 
            command=self.update_userequest, 
            orient='horizontal', 
            length=110, width=10, bg='white', 
            )
        self.scale_opaque.grid(column=1, row=row, padx=4, sticky='w')
        
        self.btnrst_opaque = tk.Button(
            self.block_panel, 
            image=self.guicon_reset, # type: ignore
            command=lambda: self.reset_usrntr(func="opaque"), 
            bg="white"
            )
        self.btnrst_opaque.grid(column=2, row=row)
        self.tip.add_to_queue(
            self.btnrst_opaque, 
            text="resets the value of opaque.", 
            )
        
        self.ckbtnbrdr_grid = tk.Frame(self.block_panel, bg="light gray")
        self.ckbtn_grid = tk.Checkbutton(
            self.ckbtnbrdr_grid, 
            text="grid", 
            variable=self.ckbtnvr_grid, 
            command=self.update_userequest, 
            bg='white'
            )
        self.ckbtn_grid.grid(padx=1, pady=1)
        self.ckbtnbrdr_grid.grid(column=3, row=row, padx=0, sticky='e')
        self.tip.add_to_queue(
            self.ckbtn_grid, 
            text="enable/disable grid function.", 
            side="bl", 
        )
        
        self.tick_grid = tk.IntVar(value=0)
        self.scale_grid = sf.CustomScale(
            self.block_panel, 
            from_=-100, to=100, 
            tickinterval=0.1, 
            variable=self.tick_grid, 
            cz_variable=self.tick_grid, 
            cmd=self.update_userequest, 
            no_symbol=True, 
            length=110, width=10, 
            orient='horizontal', bg='white' 
            )
        self.usrntr_grid = self.scale_grid.repr_num
        self.scale_grid.bind("<Button-1>", self.scale_grid.command)
        self.scale_grid.grid(column=4, padx=4, row=row)
        
        self.btnrst_grid = tk.Button(
            self.block_panel, 
            image=self.guicon_reset, # type: ignore
            command=lambda: self.reset_usrntr(func="grid"), 
            bg="white")
        self.btnrst_grid.grid(column=5, row=row, padx=(0, 5))
        self.tip.add_to_queue(
            self.btnrst_grid, 
            text="resets the value of grid.", 
            side="bl", 
            )
        
        # block preview
        self.lbl_watermark_preview = tk.Label(self.block_preview, bg='white')
        self.lbl_watermark_preview.grid(column=0, row=0)
        self.tip.add_to_queue(
            self.lbl_watermark_preview, 
            text="preview of watermark,\nif text watermark got croped by border,\ngo to advanced settings in bottom right corner.", 
            side="bl", 
            )
        
        self.btn_advset = tk.Button(self.block_advset, text='advanced settings', width=17, command=self.btnf_advset)
        self.btn_advset.grid(column=2, row=0, padx=(249, 0), sticky="w")
    
    def load_defaults(self):
        self.default_image_example = self.proper_load(
            filepath='assets/img/advanced_settings_example.png', 
            type_='image', 
            max_size=(440, 300))
        
        self.update_switch_button()
        
        self.load_image() # loads default image
        self.text_mark_maker()
        
        self.tplvl_advset = tk.Toplevel(bg="white", padx=20, pady=5)
        self.setup_advset()
        self.tplvl_advset.withdraw()
        
        self.tplvl_save = tk.Toplevel(bg="white", padx=20, pady=5)
        self.setup_savefmt()
        self.tplvl_save.withdraw()
    
    def setup_rstble(self) -> None:
        self.rstble_vals: ( # rstble = resetable
            dict[
                _rstable, dict[
                    _dft_key,   int|
                                tk.Variable|
                                list[int]|
                                list[tk.Variable]
                    ]
            ]
        ) = {
            "rotate": {
                "attr_name": self.usrntr_rotate, 
                "default_val": self.usrntr_rotate.get(), 
                }, 
            "scale": {
                "attr_name": self.tick_scale, 
                "default_val": 0, 
                }, 
            "opaque": {
                "attr_name": self.usrntr_opaque, 
                "default_val": self.usrntr_opaque.get(), 
                }, 
            "grid": {
                "attr_name": self.tick_grid, 
                "default_val": 0, 
                }, 
            "advset": {
                "attr_name": [
                    self.usrntr_border_w, 
                    self.usrntr_border_h, 
                    self.usrntr_offset_w, 
                    self.usrntr_offset_h, 
                    self.usrntr_shift_h, 
                    self.usrntr_shift_v, 
                    ], 
                "default_val": [
                    self.usrntr_border_w.get(), 
                    self.usrntr_border_h.get(), 
                    self.usrntr_offset_w.get(), 
                    self.usrntr_offset_h.get(), 
                    self.usrntr_shift_h.get(), 
                    self.usrntr_shift_v.get(), 
                    ], 
            }, 
        }
        
        self.rest_widget:list[sf.CustomScale] = [
            self.scale_scale, 
            self.scale_grid, 
        ]
        
        self.standby_widget:list[sf.CustomScale|sf.CustomSpinbox] = [
            self.scale_scale, 
            self.scale_grid, 
            self.spnbx_mark_w, 
            self.spnbx_mark_h, 
            self.spnbx_offset_h, 
            self.spnbx_offset_v, 
            self.spnbx_shift_h, 
            self.spnbx_shift_v, 
        ]
    
    def awake_custom(self, event=None) -> None:
        offset = 3
        for widget in self.rest_widget:
            widget.command()
            
            relative_x = widget.winfo_x()
            relative_y = widget.winfo_y()
            scale_w = round(widget.winfo_reqwidth() / 2)
            lbl_w = round(widget.lbl.winfo_reqwidth() / 2)
            lbl_h = widget.lbl.winfo_reqheight()
            
            x = relative_x + scale_w - lbl_w
            y = relative_y - lbl_h + offset
            
            widget.lbl.place(x=x, y=y)
    
    def setup_advset(self) -> None:
        
        row = 0
        self.ckbtnbrdr_mark_bg = tk.Frame(self.tplvl_advset, bg="light gray")
        self.ckbtn_mark_bg = tk.Checkbutton(
            self.ckbtnbrdr_mark_bg, 
            text="show watermark background", 
            variable=self.ckbtnvr_show_mark_bg,
            command=lambda: (self.show_hidden_widget(), self.text_mark_maker()), 
            bg='white', 
            )
        self.ckbtn_mark_bg.grid(padx=1, pady=1)
        self.ckbtnbrdr_mark_bg.grid(column=0, row=row, padx=(0, 15), sticky='w')
        
        self.btn_cnvsbg_color = tk.Button(
            self.tplvl_advset, text="color", 
            command=lambda: self.choose_color(tg="mark bg")
            )
        self.btn_cnvsbg_color.grid(column=1, row=row)
        self.tip.add_to_queue(
            self.btn_cnvsbg_color, 
            text='select color of background of watermark,\nuses light gray if canceled.', 
            side="bl"
        )
        
        row = 1
        self.ckbtnbrdr_wrng_mark_bg = tk.Frame(self.tplvl_advset, bg="light gray")
        self.ckbtn_wrng_mark_bg = tk.Checkbutton(
            self.ckbtnbrdr_wrng_mark_bg, 
            text="warning when watermark contains background", 
            variable=self.ckbtnvr_wrng_mark_bg, 
            bg='white', 
        )
        self.ckbtn_wrng_mark_bg.pack(padx=1, pady=1)
        self.tip.add_to_queue(
            self.ckbtn_wrng_mark_bg, 
            text='enable/disable the warning window.', 
            side="b"
        )
        
        row = 2
        self.sprtr_watermark_bg = ttk.Separator(self.tplvl_advset, orient='horizontal')
        self.sprtr_watermark_bg.grid(column=0, row=row, columnspan=2, pady=(3, 5), sticky="we")
        
        row = 3
        self.lbl_border_w = tk.Label(
            self.tplvl_advset, 
            text="adjust watermark width", 
            bg='white'
            )
        self.lbl_border_w.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_border_w, 
            text='adjust total width of watermark,\nthe width gray box shown below.', 
            side="b"
        )
        
        self.spnbx_mark_w = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            cmd=self.text_mark_maker, 
            textvariable=self.usrntr_border_w, 
            cz_variable=self.usrntr_border_w, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=6
            )
        self.spnbx_mark_w.bind("<KeyRelease>", self.spnbx_mark_w.command)
        self.spnbx_mark_w.grid(column=1, row=row, sticky='e')
        
        row = 4
        self.lbl_border_h = tk.Label(
            self.tplvl_advset, 
            text="adjust watermark height", 
            bg='white'
            )
        self.lbl_border_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_border_h, 
            text='adjust total height of watermark,\nthe height gray box shown below.', 
            side="b"
        )
        
        self.spnbx_mark_h = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            cmd=self.text_mark_maker, 
            textvariable=self.usrntr_border_h, 
            cz_variable=self.usrntr_border_h, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=6
            )
        self.spnbx_mark_h.bind("<KeyRelease>", self.spnbx_mark_h.command)
        self.spnbx_mark_h.grid(column=1, row=row, sticky='e')
        
        row = 5
        self.lbl_offset_h = tk.Label(
            self.tplvl_advset, 
            text="adjust text position horizontally(Δh)", 
            bg='white'
            )
        self.lbl_offset_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_offset_h, 
            text='adjust text position in watermark,\nthe blue text in gray box, stands for\ncurrent text position in watermark.\nincrease makes text move right,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_offset_h = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            cmd=self.text_mark_maker, 
            textvariable=self.usrntr_offset_w, 
            cz_variable=self.usrntr_offset_w, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=6
            )
        self.spnbx_offset_h.bind("<KeyRelease>", self.spnbx_offset_h.command)
        self.spnbx_offset_h.grid(column=1, row=row, sticky='e')
        
        row = 6
        self.lbl_offset_v = tk.Label(
            self.tplvl_advset, 
            text="adjust text position vertically(Δv)", 
            bg='white'
            )
        self.lbl_offset_v.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_offset_v, 
            text='adjust text position in watermark,\nthe blue text in gray box, stands for\ncurrent text position in watermark.\nincrease to move text downward,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_offset_v = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            cmd=self.text_mark_maker, 
            textvariable=self.usrntr_offset_h, 
            cz_variable=self.usrntr_offset_h, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=6
            )
        self.spnbx_offset_v.bind("<KeyRelease>", self.spnbx_offset_v.command)
        self.spnbx_offset_v.grid(column=1, row=row, sticky='e')
        
        row = 7
        self.lbl_shift_h = tk.Label(
            self.tplvl_advset, 
            text="adjust watermark position horizontally", 
            bg='white'
            )
        self.lbl_shift_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_shift_h, 
            text='adjust watermark in output image,\nbecause load image to canvas\nmay cause pixels of deviation.\nincrease makes watermark move right,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_shift_h = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            cmd=self.text_mark_maker, 
            textvariable=self.usrntr_shift_h, 
            cz_variable=self.usrntr_shift_h, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=6
            )
        self.spnbx_shift_h.bind("<KeyRelease>", self.spnbx_shift_h.command)
        self.spnbx_shift_h.grid(column=1, row=row, sticky='e')
        
        row = 8
        self.lbl_shift_v = tk.Label(
            self.tplvl_advset, 
            text="adjust watermark position vertically", 
            bg='white'
            )
        self.lbl_shift_v.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_shift_v, 
            text='adjust watermark in output image,\nbecause load image to canvas\nmay cause pixels of deviation.\nincrease to move watermark downward,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_shift_v = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            cmd=self.text_mark_maker, 
            textvariable=self.usrntr_shift_v, 
            cz_variable=self.usrntr_shift_v, 
            validate="key", validatecommand=self.validator_spnbx, 
            width=6
            )
        self.spnbx_shift_v.bind("<KeyRelease>", self.spnbx_shift_v.command)
        self.spnbx_shift_v.grid(column=1, row=row, sticky='e')
        
        row = 9
        self.btnrst_advset = tk.Button(
            self.tplvl_advset,
            text="Reset All", 
            image=self.guicon_reset, # type: ignore
            compound= tk.LEFT, 
            command=lambda: self.reset_usrntr(func="advset"), 
            )
        self.btnrst_advset.grid(column=1, row=row, pady=(3, 0), sticky="e")
        self.tip.add_to_queue(
            self.btnrst_advset, 
            text='reset all adjustments.', 
            side="bl"
        )
        
        row = 10
        self.sprtr_adjust = ttk.Separator(self.tplvl_advset, orient='horizontal')
        self.sprtr_adjust.grid(column=0, row=row, columnspan=2, pady=(3, 5), sticky="we")
        
        row = 11
        self.lbl_example = tk.Label(
            self.tplvl_advset, 
            text="example diagram:", 
            bg="white"
            )
        self.lbl_example.grid(column=0, row=row, sticky="w")
        
        row = 12
        self.lbl_example_image = tk.Label(
            self.tplvl_advset, 
            image=self.default_image_example,  # type: ignore
            bg="white", 
            )
        self.lbl_example_image.grid(column=0, row=row, columnspan=3)
        
        row = 13
        self.sprtr_diagram = ttk.Separator(self.tplvl_advset, orient='horizontal')
        self.sprtr_diagram.grid(column=0, row=row, columnspan=2, pady=(3, 5), sticky="we")
        
        row = 14
        self.ckbtnbrdr_tooltip = tk.Frame(self.tplvl_advset, bg="light gray")
        self.ckbtn_tooltip = tk.Checkbutton(
            self.ckbtnbrdr_tooltip, 
            text="show tooltip", 
            variable=self.ckbtnvr_tooltip, 
            command=self.btnf_ckbtn_tooltip, 
            bg="white", 
            fg="black",
            highlightthickness=2,
        )
        self.ckbtn_tooltip.pack(padx=1, pady=1)
        self.ckbtnbrdr_tooltip.grid(column=0, row=row, sticky="w")
        self.tip.add_to_queue(
            self.ckbtn_tooltip, 
            text="enable/disable tooltip,\nthe text you currently looking at.", 
            side="t"
        )
        
        self.btn_hide_tplvl = tk.Button(
            self.tplvl_advset, 
            text="Done", 
            command=lambda: self.tplvl_advset.withdraw()
            )
        self.btn_hide_tplvl.grid(column=1, row=row, sticky="e")
        
    def setup_savefmt(self) -> None:
        
        row = 0
        self.btn_savedir = tk.Button(
            self.tplvl_save, 
            text="save directory", 
            command=self.btnf_savedir, 
            )
        self.btn_savedir.grid(column=0, row=row, padx=(0, 10), sticky='w')
        self.tip.add_to_queue(
            self.btn_savedir, 
            text="select a directory to save watermarked images.", 
        )
        
        self.lbl_savedir = tk.Label(
            self.tplvl_save, 
            textvariable=self.save_dir, 
            fg="red", 
        )
        self.lbl_savedir.grid(column=1, row=row, columnspan=2, sticky='w')
        self.tip.add_to_queue(
            self.lbl_savedir, 
            text="specified directory to save watermarked images.", 
            side="b", 
        )
        
        row = 1
        self.ckbtnbrdr_fname_fmt = tk.Frame(self.tplvl_save, bg="light gray")
        self.ckbtn_fname_fmt = tk.Checkbutton(
            self.ckbtnbrdr_fname_fmt, 
            text="format", 
            variable=self.ckbtnvr_fname_fmt, 
            command=lambda: self.btnf_ckbtn_switch(method="format"), 
            bg="white", 
        )
        self.ckbtn_fname_fmt.pack(padx=1, pady=1)
        self.ckbtnbrdr_fname_fmt.grid(column=0, row=row, sticky='w')
        self.tip.add_to_queue(
            self.ckbtn_fname_fmt, 
            text="add text before and/or after original\nfile name as the save name.", 
        )
        
        self.entry_prefix = tk.Entry(
            self.tplvl_save, 
            textvariable=self.fname_prefix, 
            width=10, 
            bg="#ededed"
        )
        self.entry_prefix.bind("<KeyRelease>", self.fmt_selected)
        self.entry_prefix.grid(column=1, row=row, sticky='w')
        
        self.btn_clear_entry_prefix = tk.Button(
            self.tplvl_save, 
            text="X", 
            command=lambda: (self.entry_prefix.delete(0, tk.END), self.fmt_selected()),  
            image=self.pixel, compound="center", 
            border=0, width=22, height=22, padx=0, pady=0, 
            )
        px = self.entry_prefix.winfo_reqwidth() - self.btn_clear_entry_prefix.winfo_reqwidth() - 1
        self.btn_clear_entry_prefix.grid(column=1, row=row, padx=(px, 0), sticky='w')
        
        self.entry_suffix = tk.Entry(
            self.tplvl_save, 
            textvariable=self.fname_suffix, 
            width=10, 
            bg="#ededed"
        )
        self.entry_suffix.bind("<KeyRelease>", self.fmt_selected)
        self.entry_suffix.grid(column=1, row=row, padx=(132, 0), sticky='w')
        
        self.btn_clear_entry_suffix = tk.Button(
            self.tplvl_save, 
            text="X", 
            command=lambda: (self.entry_suffix.delete(0, tk.END), self.fmt_selected()),  
            image=self.pixel, compound="center", 
            border=0, width=22, height=22, padx=0, pady=0, 
            )
        px = self.entry_suffix.winfo_reqwidth() - self.btn_clear_entry_suffix.winfo_reqwidth() - 1
        self.btn_clear_entry_suffix.grid(column=1, row=row, padx=(132+px, 0), sticky='w')
        
        row = 2
        self.ckbtnbrdr_fname_rename = tk.Frame(self.tplvl_save, bg="light gray")
        self.ckbtn_fname_rename = tk.Checkbutton(
            self.ckbtnbrdr_fname_rename, 
            text="rename", 
            variable=self.ckbtnvr_fname_rename, 
            command=lambda: self.btnf_ckbtn_switch(method="rename"), 
            bg="white", 
        )
        self.ckbtn_fname_rename.pack(padx=1, pady=1)
        self.ckbtnbrdr_fname_rename.grid(column=0, row=row, sticky='w')
        self.tip.add_to_queue(
            self.ckbtn_fname_rename, 
            text="rename file name as the save name,\noutput names will be Name-1, Name-2... etc."
        )
        
        self.entry_rename = tk.Entry(
            self.tplvl_save, 
            textvariable=self.fname_name, 
            width=21, 
            bg="#ededed"
        )
        self.entry_rename.bind("<KeyRelease>", self.fmt_selected)
        self.entry_rename.grid(column=1, row=row, columnspan=2, sticky='w')

        self.btn_clear_entry_rename = tk.Button(
            self.tplvl_save, 
            text="X", 
            command=lambda: (self.entry_rename.delete(0, tk.END), self.fmt_selected()), 
            border=0, width=22, height=22, padx=0, pady=0, 
            image=self.pixel, compound="center", 
            )
        px = self.entry_rename.winfo_reqwidth() - self.btn_clear_entry_rename.winfo_reqwidth() - 1
        self.btn_clear_entry_rename.grid(column=1, row=row, padx=(px, 0), sticky='w')
        
        row = 3
        self.lbl_filefmt = tk.Label(
            self.tplvl_save, 
            text="file format", 
            bg="white", 
            )
        self.lbl_filefmt.grid(column=0, row=row, sticky='w')
        
        self.cmbbx_filefmt = ttk.Combobox(
            self.tplvl_save, 
            values=['.png', '.jpg', '.jpeg'], 
            state="readonly", 
            cursor="hand2", 
            width=10, 
        )
        self.cmbbx_filefmt.set('.png')
        self.cmbbx_filefmt.bind("<<ComboboxSelected>>", self.fmt_selected)
        self.cmbbx_filefmt.grid(column=1, row=row, columnspan=2, sticky='w')
        
        row = 4
        self.lbl_example_fname = tk.Label(
            self.tplvl_save, 
            text="example", 
            bg="white", 
        )
        self.lbl_example_fname.grid(column=0, row=row, sticky='w')
        self.tip.add_to_queue(
            self.lbl_example_fname, 
            text="preview of file name under current\nnaming scheme, with first file as example."
        )
        
        self.lbl_outcome_fname = tk.Label(
            self.tplvl_save, 
            textvariable=self.fname_example,
        )
        self.lbl_outcome_fname.grid(column=1, row=row, pady=7, columnspan=3, sticky='w')
        
        row = 5
        self.btn_apply_savefmt = tk.Button(
            self.tplvl_save, 
            text="execute", 
            command=self.apply_to_folder, 
        )
        self.btn_apply_savefmt.grid(column=1, row=row)
        self.tip.add_to_queue(
            self.btn_apply_savefmt, 
            text="add watermark to all images selected,\nsave images by naming scheme above."
        )
        
    # GUI functions
    def btnf_load_image_path(self):
        self.filepath_image = "assets/img/200x200.png"
        # self.filepath_image = filedialog.askopenfilename()
        if self.filepath_image == "":
            return None
        self.load_image()
        # additional thought:
        # add load image mode RGB, RGBA ... cite: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
        # use combobox bind with `<<ComboboxSelected>>`, command set `self.load_image()`, 
        # reload the image when selected, if image have conflict with RGBA mode, 
        # user can change the mode manually, but `self.save_image` uses Image.alpha_composite(), 
        # which specifically requires Image mode=RGBA, also yet no precedent so postponed.
        
    def btnf_load_images_path(self):
        self.apply_paths = []
        filepaths = filedialog.askopenfilenames(filetypes=file_type)
        if filepaths == "":
            return None
        for filepath in filepaths:
            self.apply_paths.append(filepath)
        self.filepath_image = self.apply_paths[0]
        self.load_image()
        
    def btnf_load_folder_path(self):
        self.apply_paths = []
        folder = filedialog.askdirectory()
        if folder == "":
            return None
        for path, dirs, fnames in os.walk(folder):
            for fname in fnames:
                if any(map(fname.endswith, [".png", ".jpg", ".jpeg"])):
                    filepath = os.path.join(path, fname).replace("\\", "/")
                    self.apply_paths.append(filepath)
        self.filepath_image = self.apply_paths[0]
        self.load_image()
        
    def btnf_load_mark_path(self) -> None:
        self.filepath_mark = 'assets/img/watermark.png'
        # self.filepath_mark = filedialog.askopenfilename()
        if self.filepath_image == "":
            return None
        self.load_mark()
    
    def btnf_image_mode(self) -> None:
        self.switch_state = 'image'
        if self.condition_met(func_="btnf_image_mode"):
            self.load_mark()
        
    def btnf_text_mode(self) -> None:
        self.switch_state = 'text'
        self.update_switch_button()
        self.text_mark_maker()
    
    def update_userequest(self, event=None) -> None:
        if self.switch_state == "image":
            self.load_mark()
        elif self.switch_state == "text":
            self.text_mark_maker()
        self.remove_exist_watermark(method="motion")
    
    def btnf_advset(self) -> None:
        if self.tplvl_advset.winfo_exists():
            self.tplvl_advset.deiconify()
        else:
            self.tplvl_advset = tk.Toplevel(bg="white", padx=20, pady=5)
            self.setup_advset()
        
    def btnf_save(self) -> None:
        if not self.condition_met(func_="btnf_save"):
            return None
        
        dir_, fname = self.filepath_image.rsplit("/", maxsplit=1)
        name, type_ = fname.rsplit(".", maxsplit=1)
        fname = name + " - watermarked." + type_
        
        path = filedialog.asksaveasfilename(
            filetypes=file_type , 
            initialdir=dir_ , 
            initialfile=fname , 
        )
        
        if path == "":
            return None
        self.save_image(abs_path=path)
        
        # load the next image if there's any
        if len(self.apply_paths) > 1:
            self.apply_paths.remove(self.filepath_image)
            self.filepath_image = self.apply_paths[0]
        elif len(self.apply_paths) == 1:
            self.apply_paths.remove(self.filepath_image)
        if len(self.apply_paths) < 1:
            self.filepath_image = 'assets/img/default_image.png'
            self.is_image = False
            
        self.load_image()
        self.update_canvas_bind()
        
    def btnf_apply(self) -> None:
        if not self.condition_met(func_="btnf_apply"):
            return None
        
        if self.tplvl_save.winfo_exists():
            self.tplvl_save.deiconify()
        else:
            self.tplvl_save = tk.Toplevel(bg="white", padx=20, pady=5)
            self.setup_savefmt()
        self.fmt_selected()
        
    def btnf_savedir(self) -> None:
        dir_ = filedialog.askdirectory()
        if dir_ == "":
            return None
        self.save_dir.set(dir_)
        self.lbl_savedir.config(fg="black")
        self.tplvl_save.deiconify()
    
    def btnf_ckbtn_tooltip(self) -> None:
        if self.ckbtnvr_tooltip.get():
            self.tip.enable_all()
        else:
            self.tip.disable_all()
        
    def btnf_ckbtn_switch(self, method:_ckbtn_switch) -> None:
        if method == "format":
            self.ckbtn_fname_fmt.select()
            self.ckbtn_fname_rename.deselect()
        elif method == "rename":
            self.ckbtn_fname_fmt.deselect()
            self.ckbtn_fname_rename.select()
        self.fmt_selected()
        
    def reset_usrntr(self, func:_rstable) -> None:
        if func == "advset":
            for idx, value in enumerate(self.rstble_vals[func]["attr_name"]): # type: ignore
                value.set(self.rstble_vals[func]["default_val"][idx]) # type: ignore
        else:
            self.rstble_vals[func]["attr_name"].set( # type: ignore
                self.rstble_vals[func].get("default_val")
            )
        for widget in self.standby_widget:
            widget.command()
        self.update_userequest()
        
    def font_selected(self, event=None) -> None:
        rq_font = self.cmbbx_font.get()
        
        self.cmbbx_fontstyle.config(background="white")
        style = sorted(list(self.fonts_dict[rq_font].keys()))
        priori = ["Regular", "regular"]
        for item in priori:
            if item in style:
                self.cmbbx_fontstyle['values'] = style
                self.cmbbx_fontstyle.set(item)
                self.text_mark_maker()
                break
        else:
            if len(style) == 1:
                self.cmbbx_fontstyle['values'] = style
                self.cmbbx_fontstyle.current(0)
                self.text_mark_maker()
            else:
                # font without "Regular" and "regular", and have more than one style,
                # use "Sitka" and "Perpetua Titling MT" to test (generate by __prnt_style_without_regular_())
                self.cmbbx_fontstyle['values'] = ['select a style']
                self.cmbbx_fontstyle.config(background="red")
                self.cmbbx_fontstyle.current(0)
                self.cmbbx_fontstyle['values'] = style
                messagebox.showinfo(
                    title="Wait a sec.", 
                    message="the font selected has more than one style, and no default value, please select one."
                    )

    def fmt_selected(self, event=None) -> None:
        filename = self.get_fname()
        self.fname_example.set(filename)
        
    def get_fname(self, idx:int|None=None) -> str:
        if self.ckbtnvr_fname_fmt.get():
            prefix = self.fname_prefix.get()
            suffix = self.fname_suffix.get()
            og_name = self.filepath_image.rsplit("/", maxsplit=1)[1].rsplit(".", maxsplit=1)[-2]
            fname = prefix + og_name + suffix
        else:
            name = self.fname_name.get()
            if idx:
                fname = name + " - " + str(idx)
            else:
                fname = name + "-1"
        fmt = self.cmbbx_filefmt.get()
        return fname + fmt
        
    def show_hidden_widget(self) -> None:
        if self.ckbtnvr_show_mark_bg.get():
            self.ckbtnbrdr_wrng_mark_bg.grid(column=0, row=1, columnspan=2)
        else:
            self.ckbtnbrdr_wrng_mark_bg.grid_forget()
        
    # key functions
    def operate(self) -> None:
        """
        the power button.
        """
        self.window.mainloop()
        
    def usrntr_text(self) -> str:
        return self.tktxt_entry.get(0.0, "end-1c")
        
    def proper_load(
        self, 
        *, 
        filepath:str, 
        type_:_img, 
        alpha:int|None=255, 
        angle:int=0,
        max_size:tuple[int,int]|None=None, 
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
        # // load image and convert it to RGBA, to avoid ValueError: images do not match
        # // cite: https://stackoverflow.com/questions/12291641/python-pil-valueerror-images-do-not-match
        # when using Image.alpha_composite(), alpha channel are of course necessary.
        image_pil = Image.open(filepath).convert("RGBA")
        
        
        if alpha:
            image_pil.putalpha(alpha)
        image_pil = image_pil.rotate(angle, expand=True)
        
        self.store_pil(pil=image_pil, type_=type_)
        
        size = self.get_image_size(pil=image_pil, type_=type_, max_size=max_size)
        img = image_pil.resize(size)
        
        return ImageTk.PhotoImage(img)
    
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
        self.clicked = False
        
        if self.is_mark:
            self.update_mark_size()
            self.update_canvas_bind()
        
    def load_mark(self) -> None:
        """
        ask user filepath to load watermark,
        bind canvas with user action,
        calls to update watermark offset.
        """
        opaque = self.usrntr_opaque.get()
        alpha = round(np.round((opaque/100) * 255))
        angle = self.usrntr_rotate.get()
        
        self.ghost = self.mark = self.proper_load(
            filepath=self.filepath_mark, # type: ignore
            type_='mark', 
            alpha=alpha, 
            angle=angle, 
            )
        
        self.is_mark = True
        self.switch_state = "image"
        self.update_mark_offset()
        self.update_canvas_bind()
        self.update_switch_button()
        
        # update preview
        self.lbl_watermark_preview.config(image=self.mark) # type: ignore
    
    def canvas_action(self, event, *, method:str, call_by_func:bool|None=None) -> None:
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
            
        if call_by_func:
            x0, y0 = self.clicked_position
        else:
            x0, y0 = event.x, event.y
        self.clicked_position = x0, y0
        
        x, y, snap_position = self.mouse_loc_calibrate(x0, y0) 
        
        if method == 'clicked':
            self.clicked = True
            if self.ckbtnvr_snap.get() and snap_position:
                self.true_position:tuple[int,int] = snap_position
                self.snap_position:bool = True
            else:
                self.true_position:tuple[int, int] = x0, y0
                self.snap_position:bool = False
        
        if self.ckbtnvr_grid.get():
            grid_space = self.usrntr_grid.get()
            locs = self.grid_calculate(x, y, grid_space, on="canvas")
            for x_loc in locs["x"]:
                for y_loc in locs["y"]:
                    self.draw_watermark(x_loc, y_loc, method=method, grid=True)
        else:
            self.draw_watermark(x, y, method=method)
        
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
        if x_max >= x >= x_min and y_max >= y >= y_min or not self.ckbtnvr_snap.get(): # in image
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
        x_calibrate = mouse_loc[0] - self.mark_offset_x_min
        y_calibrate = mouse_loc[1] - self.mark_offset_y_min
        return x_calibrate, y_calibrate, snap_position
    
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
        name = self.cmbbx_font.get()
        style = self.cmbbx_fontstyle.get()
        rq_font = self.fonts_dict[name][style] # rq: requested
        pixel_size = self.usrntr_fontsize.get() / 0.75
        
        try:
            border_w = self.usrntr_border_w.get()
            border_h = self.usrntr_border_h.get()
        except tk.TclError: 
            return
        
        opaque = self.usrntr_opaque.get()
        alpha = round(np.round((opaque/100) * 255))
        angle = self.usrntr_rotate.get()

        # font of text
        fnt = ImageFont.truetype(font=rq_font, size=pixel_size) 
        offset = (self.usrntr_offset_w.get(), self.usrntr_offset_h.get())
        text_color = *self.current_font_rgb, alpha
        
        # get border of the text from PIL
        _ = Image.new("RGBA", text_watermark_max_size)
        f = ImageDraw.Draw(_)
        f_bbox = f.textbbox((0, 0), self.usrntr_text(), font=fnt)
        
        # get text border sizes of the text with font
        width = f_bbox[2] - f_bbox[0] + border_w
        height = f_bbox[3] - f_bbox[1] + border_h
        
        # make sure width and height of image > 0
        if not self.length_valid(width, height, f_bbox):
            return None
        
        if self.ckbtnvr_show_mark_bg.get():
            base = Image.new("RGBA", (width, height), (*self.mark_bg, 255))
        else:
            base = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            
        d = ImageDraw.Draw(base)
        d.text(offset, self.usrntr_text(), font=fnt, fill=text_color)
        
        mark_base = base.copy().convert("RGBA")
        mark_rot = mark_base.rotate(angle, expand=True)
        
        self.store_pil(pil=mark_rot, type_="text")
        size = self.get_image_size(pil=mark_rot, type_="text")
        
        mark = mark_rot.resize(size)
        self.ghost = self.mark = ImageTk.PhotoImage(mark)
        
        self.is_mark = True
        self.update_mark_offset()
        
        # update preview
        self.lbl_watermark_preview.config(image=self.mark) # type: ignore
    
    
    def save_image(self, *, abs_path:str, call_by_func:bool|None=None) -> None:
        """
        save image with watermark, where the location of watermark is set by user,
        snap to border if watermark will be outside of image,
        image will be saved at root folder in project.
        """
        true_markpil_width:int = round(np.round(self.mark_pil.width * self.usrntr_scale.get()))
        true_markpil_height:int = round(np.round(self.mark_pil.height * self.usrntr_scale.get()))
        
        if self.ckbtnvr_snap.get() and self.snap_position:
            x, y = self.true_position
            if self.true_position[0] == self.image_pil.width:
                x -= true_markpil_width + self.usrntr_shift_h.get()
            if self.true_position[1] == self.image_pil.height:
                y -= true_markpil_height + self.usrntr_shift_v.get()
        else:
            true_x = self.true_position[0] - self.mark_offset_x_min - self.image_datum_x
            true_y = self.true_position[1] - self.mark_offset_y_min - self.image_datum_y
            x:int = round(np.round(true_x * self.image_width_scale)) + self.usrntr_shift_h.get()
            y:int = round(np.round(true_y * self.image_height_scale)) + self.usrntr_shift_v.get()
            
        offset = (x, y)
        
        mark = self.mark_pil.copy()
        size = true_markpil_width, true_markpil_height
        resized_mark = mark.resize(size)
        
        if self.ckbtnvr_grid.get():
            grid_space = self.usrntr_grid.get()
            mark = self.grid_mark_maker(round(x), round(y), grid_space, resized_mark)
            offset = 0, 0
            result_mark = mark.copy()
        else:
            result_mark = resized_mark.copy()
            
        result_image = self.image_pil.copy()
        result_image.alpha_composite(result_mark, offset)
        result_image.save(abs_path)
        
    def grid_mark_maker(self, x:int, y:int, grid_space:int, mark:Image.Image) -> Image.Image:
        width = self.image_pil.width
        height = self.image_pil.height
        
        with Image.new("RGBA", (width, height)) as base:
            locs = self.grid_calculate(x, y, grid_space, on="image")
            for x in locs['x']:
                for y in locs['y']:
                    base.paste(im=mark, box=(x,y))
            return base.copy()
    
    def grid_calculate(self, x:int, y:int, grid_space:int, on:_loc) -> dict[str, list[int]]:
        if on == "canvas":
            width = self.image.width() + self.mark.width()
            height = self.image.height() + self.mark.height()
            step = max(self.mark.width(), self.mark.height()) + grid_space
            x_max = self.canvas.winfo_reqwidth()
            y_max = self.canvas.winfo_reqheight()
        elif on == "image":
            scaled_markpil_width = round(np.round(self.mark_pil.width * self.usrntr_scale.get()))
            width = self.image_pil.width + scaled_markpil_width
            
            scaled_markpil_height = round(np.round(self.mark_pil.height * self.usrntr_scale.get()))
            height = self.image_pil.height + scaled_markpil_height
            
            grid_scale = min(self.image_width_scale, self.image_height_scale)
            step = max(scaled_markpil_width, scaled_markpil_height) + round(grid_space * grid_scale)
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
    
    def apply_to_folder(self, event=None):
        if not self.condition_met(func_="apply_to_folder"):
            return None
        
        save_dir = self.save_dir.get()
        for idx, path in enumerate(self.apply_paths):
            self.filepath_image = path
            self.load_image()
            
            fname = self.get_fname(idx=idx)
            save_path = save_dir + "/" + fname
            self.save_image(abs_path=save_path, call_by_func=True)
        self.apply_paths = []
    
    # update stuff
    def update_canvas_bg(self) -> None:
        if self.ckbtnvr_show_cnvs_bg.get():
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
            if self.ckbtnvr_show_preview.get():
                self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
            else:
                self.canvas.unbind("<Motion>")
            self.canvas.focus_set()
            self.remove_exist_watermark(method="motion")
            self.remove_exist_watermark(method="clicked")
        else:
            self.canvas.unbind("<Button-1>")
        
    def update_mode(self) -> None:
        if self.switch_state == "text":
            self.btnf_image_mode()
        elif self.switch_state == 'image':
            self.btnf_text_mode()
        
    def update_mark_size(self):
        width = np.round(self.mark_pil.width / self.image_width_scale)
        height = np.round(self.mark_pil.height / self.image_height_scale)
        size = (round(width), round(height))
        
        image_resize = self.mark_pil.resize(size)
        
        self.ghost = self.mark = ImageTk.PhotoImage(image_resize)
        
    def update_mark_offset(self) -> None:
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
        self.remove_exist_watermark(method="all")
    
    # support functions
    def store_pil(self, pil:Image.Image, type_:_img) -> None:
        if type_ == 'image':
            self.image_pil = pil
        elif type_ == 'mark' or type_ == "text":
            self.mark_pil = pil
            
    def clear_tkentry_text(self, event=None) -> None:
        """
        remove default text in tk.Entry, when user click in tk.Entry
        and bind M1 to function:self.entry_action.

        Args:
            event (_type_): _description_ 
        """
        self.tktxt_entry.delete(0.0, tk.END)
        self.tktxt_entry.unbind("<Button-1>")
        self.tktxt_entry.bind("<KeyRelease>", self.text_mark_maker)
        
    def get_image_size(
        self, 
        pil:Image.Image, 
        type_:_img, 
        max_size:tuple[int,int]|None=None
        ) -> tuple[int, int]:
        
        if type_ == "text":
            width = np.round(pil.width / self.image_width_scale)
            height = np.round(pil.height / self.image_height_scale)
            size = (round(width), round(height))
        else:
            size = self.image_size_calculate(pil.width, pil.height, type_=type_, max_size=max_size)
        rq_scale = self.usrntr_scale.get()
        rq_width = np.round(size[0] * rq_scale)
        rq_height = np.round(size[1] * rq_scale)
        return (round(rq_width), round(rq_height))
    
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
            w = 1 / self.image_width_scale
            h = 1 / self.image_height_scale
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
                self.mark_bg = gray
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
            elif method == "all":
                self.canvas.delete(self.canvas_mark_preview)
                self.canvas.delete(self.canvas_mark)
        except AttributeError:
            print("making sure to remove unwanted watermarks")
        
        if self.ckbtnvr_grid.get() and method == 'clicked':
            for item in self.grid_watermark:
                self.canvas.delete(item)
        elif self.ckbtnvr_grid.get() and method == 'motion':
            for item in self.grid_watermark_preview:
                self.canvas.delete(item)
        
    def length_valid(self, width:int, height:int, bbox:tuple[int, int, int, int]) -> bool:
        condition = []
        vaild = True
        if width <= 0:
            condition.append(f"watermark width > {-(bbox[2] - bbox[0])}")
            vaild = False
        if height <= 0:
            condition.append(f"watermark height > {-(bbox[3] - bbox[1])}")
            vaild = False
        if not vaild:
            messagebox.showwarning(
                title="Invaild adjust value.", 
                message=f"Length of width and height of square must > 1.\n In this case, {', '.join(condition)}."
                )
        return vaild
    
    def spnbx_val_validate(self, value) -> bool:
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
        
    def condition_met(self, func_:_msgbx) -> bool:
        if func_ == "btnf_image_mode":
            if self.filepath_mark is None:
                self.btn_switch_text.config(relief='sunken')
                messagebox.showwarning(title="Missing something", message="click watermark button and select a image file first!")
                return False
        elif func_ == "btnf_save":
            if self.filepath_image == 'assets/img/default_image.png':
                messagebox.askyesno(
                    title="Too early. Load a image first!", 
                    message="load a image and place watermark on the image then click the save button.", 
                    )
                return False
            elif self.clicked == False:
                messagebox.showwarning(
                    title="Too early. Place watermark first!", 
                    message="place watermark on the image, then click the save button.", 
                    )
                return False
            elif self.ckbtnvr_show_mark_bg.get() and self.switch_state == "text" and self.ckbtnvr_wrng_mark_bg.get():
                save = messagebox.askyesno(
                    title="Wait a second.", 
                    message="the background of watermark preview will also appear in the result image, still want to save the image?", 
                    )
                if not save:
                    return False
        elif func_ == "btnf_apply":
            if self.filepath_image == 'assets/img/default_image.png':
                messagebox.showwarning(
                    title="Too early. Load a image first!", 
                    message="load a image and place watermark on the image, then click the apply button.", 
                    )
                return False
            elif self.clicked == False:
                messagebox.showwarning(
                    title="Too early. Place watermark first!", 
                    message="place watermark on the image, then click the apply button.", 
                    )
                return False
            elif self.apply_paths == []:
                messagebox.showwarning(
                    title="Too early. Open and select a folder first!", 
                    message="select a folder of image to apply watermark, then click the apply button.", 
                    )
                return False
        elif func_ == "apply_to_folder":
            if self.save_dir.get() == "file save directory missing.":
                messagebox.showwarning(
                    title="Too early. Open and select a folder first!", 
                    message="select a folder to save watermarked image, then click the execute button.", 
                    )
                return False
        return True

    def __prnt_style_without_regular_(self):
        font_dict = sf.get_sysfont_sorted()
        for name in font_dict:
            all_style = []
            for style in font_dict[name]:
                all_style.append(style)
            if len(all_style) > 1:
                if "Regular" not in all_style and "regular" not in all_style:
                    print(name, font_dict[name])

    def __get_rotated_size(self, width, height, angle):
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
    
wm = WaterMarker()
wm.operate()