# standard library
import math, os
import tkinter as tk

from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Literal, TypeAlias

# related third party imports
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk

# local application/library specific imports
import support_func as sf

# file paths
FPATH_DFT_IMG = "assets/img/default_image.png" # dft_img: default image
FPATH_ICON_FILE = "assets/img/files.png"
FPATH_ICON_FLDR = "assets/img/folder.png" # fldr: folder
FPATH_ICON_RSET = "assets/img/arrow-counterclockwise.png" # rset: reset
FPATH_ASET_EG = "assets/img/advanced_settings_example.png" # aset_eg: advanced settings example

# test file paths
FPATH_TEST_IMG = "assets/img/200x200.png"
FPATH_TEST_MARK = "assets/img/watermark.png"

# default key dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 720

CANVAS_WIDTH = 860
CANVAS_HEIGHT = 560
CANVAS_PADX = 30
CANVAS_PADY = 30

MARK_MAX_SIZE = (2000, 2000)
GRAY_RGB = (128, 128, 128)

# border and offsets
BORDER_WIDTH = 7
BORDER_HEIGHT = 5
OFFSET_WIDTH = 3
OFFSET_HEIGHT = -3

# default font related stuff
FONT_FORMAT_NORMAL = ("Arial", 16, "normal")
FONT_FORMAT_SMALL = ("Arial", 14, "normal")
FONT = 'Arial'
styles = ['Regular', 'Narrow Bold Italic', 'Bold', 'Narrow Bold', 'Narrow Italic', 'Narrow', 'Bold Italic', 'Black', 'Italic'] 
STYLES = sorted(styles)

# allowed file types
FTYPE = ((".png", "*.png"), (".jpg", "*.jpg"), (".jpeg", "*.jpeg"))

# custom types
_state: TypeAlias = Literal["image", "text"]
_color: TypeAlias = Literal["text bg", "text fg", "canvas bg"]
_img: TypeAlias = Literal["image", "mark", "text",]
_loc: TypeAlias = Literal["image", "canvas"]
_rstable: TypeAlias = Literal["rotate", "scale", "opaque", "grid", "advset"]
_ckbtn_switch: TypeAlias = Literal["format", "rename"]
_msgbx: TypeAlias = Literal[
    "btnf_image_mode", "btnf_save", "btnf_apply", "btnf_preview", 
    "canvas_clicked", "unselected_style", 
    "apply_to_folder", 
]
_pbar: TypeAlias = Literal["start", "step", "hide", "set"]
_cnvs_actn: TypeAlias = Literal["clicked", "motion"]
_rm_mark: TypeAlias = Literal["clicked", "motion", "all"]



class WaterMarker():
    """
    A Python Class to create a app for watermark a image, 
    watermark picture with a image file or create one with text.
    
    With many features:
    1. rotate, set rotation to watermark.
    2. scale, resize watermark proportionally.
    3. opaque, set transparency to watermark.
    4. grid, fill the whole image with watermark with distance in between.
    5. snap, restrict watermark to stay inside image border.
    6. create text watermark with configurable parameters:
        a. text content
        b. font
        c. font style
        d. size
        e. text color
        f. background color
        g. width and height of watermark
        h. horizontal and vertical position of text in watermark.
    
    Example
    -------
    >>> wm = WaterMarker()
    >>> wm.operate()
    
    Known Bugs
    ----------
    - Enters '08' or '09' at tkinter Spinbox will cause `tk.TclError: 
    expected floating-point number but got "08" (looks like invalid octal number)`.
        Not much can do, nothing seems to fix this with the current code logic, 
        and alternative seems effective: with show messagebox warning when user 
        clicked on canvas and '08' or '09 was entered, .
        Also see: self.condition_met(from_="canvas_clicked")
    """
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("💧MarkIt.")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.config(background="white")
        self.window.resizable(width=False, height=False)
        
        self.validator_spnbx = (self.window.register(self.spnbx_val_validate), "%P")
        self.tip = sf.TipManager()
        
        self.setup_option()
        self.setup_attribute()
        self.setup_variable()
        self.setup_labelframe()
        self.setup_widget()
        self.load_defaults()
        self.setup_rstble_and_custom()
        
        self.window.update()
        
        self.awake_custom()
        self.tip.enable_all()
        self.customize_titltbar()
        
    def setup_option(self) -> None:
        """
        Setup tkinter Tk options for Windows, 
        this function must be called before any widget are created to have effect on them.
        cite: https://tcl.tk/man/tcl8.6/TkCmd/option.html
        """
        self.window.option_add("*Font", FONT_FORMAT_NORMAL)
        self.window.option_add("*Button.cursor", "hand2")
        self.window.option_add("*Checkbutton.cursor", "hand2")
        self.window.option_add("*Spinbox.buttonCursor", "hand2")
        
        # self.window.option_add("*Combobox.cursor", "hand2") # not working
        
        # self.window.option_add("*Dialog.msg.font", 'Helvetica 30') # not working
        # explanation: https://stackoverflow.com/questions/53694345/how-to-change-font-size-of-messages-inside-messagebox-showinfomessage-hello
        # tcl cite: https://wiki.tcl-lang.org/page/tk%5FmessageBox
        
    def setup_attribute(self) -> None:
        """Create attributes for functions."""
        self.inidir_image:str = ""
        self.inidir_mark:str = ""
        self.inidir_save:str = ""
        self.inidir_apply:str = ""
        
        self.is_image = False
        self.is_mark = False
        
        self.switch_state:_state = "text"
        self.filepath_image:str = FPATH_DFT_IMG
        self.filepath_mark:str = ""
        
        self.mark_bg = GRAY_RGB
        self.canvas_bg = "gray"
        self.current_font_hexcolor = "black"
        self.current_font_rgb:tuple[int,int,int] = (0, 0, 0)
        
        self.fonts_dict:dict[str, dict[str, str]] = sf.get_sysfont_sorted()
        self.font_names:list[str] = sorted(list(self.fonts_dict.keys()))
        
        self.grid_watermark:list[int] = []
        self.grid_watermark_preview:list[int] = []
        
        self.apply_paths:list[str] = []
        
        # other icons
        self.guicon_files = ImageTk.PhotoImage(Image.open(FPATH_ICON_FILE))
        self.guicon_folder = ImageTk.PhotoImage(Image.open(FPATH_ICON_FLDR))
        self.guicon_reset = ImageTk.PhotoImage(Image.open(FPATH_ICON_RSET))
        
        # Note: resolved safefuses
        # With holding down tkinter Spinbox and got interfered by tkinter messagebox, 
        # guessing the button on tkinter Spinbox never releases, and gets stuck in infinite loop,
        # the solution to get out of loop manually is by set the value to a large number 
        # so that you got some reaction time, then release the sunken button by click on 
        # the up/down triangle button or the number entering area, 
        # not going to expect anyone to figure this out.
        # Solution from function: btnf_tplvl_advset_hide
        # The solution to infinite loop cause by `user held down tkinter Spinbox button 
        # got interfered by tkinter messagebox` can be solved by `don't do that`,
        # in this case, check if length of width or height of image is valid
        # after user is done adjust the watermark, when the `Done` button is clicked.
        
    def setup_variable(self) -> None:
        """Create tkinter variables for widgets."""
        self.usrntr_fontsize = tk.IntVar() # usrntr: user enter
        self.usrntr_fontsize.set(FONT_FORMAT_NORMAL[1])
        
        self.usrntr_rotate = tk.IntVar()
        self.usrntr_rotate.set(0)
        
        self.usrntr_scale = tk.DoubleVar()
        self.usrntr_scale.set(1)
        
        self.usrntr_opaque = tk.IntVar()
        self.usrntr_opaque.set(100)
        
        self.usrntr_grid = tk.IntVar()
        self.usrntr_grid.set(100)
        
        self.text_image_count = tk.StringVar()
        
        self.usrntr_border_w = tk.IntVar()
        self.usrntr_border_w.set(BORDER_WIDTH)
        self.usrntr_border_h = tk.IntVar()
        self.usrntr_border_h.set(BORDER_HEIGHT)
        
        self.usrntr_offset_w = tk.IntVar()
        self.usrntr_offset_w.set(OFFSET_WIDTH)
        self.usrntr_offset_h = tk.IntVar()
        self.usrntr_offset_h.set(OFFSET_HEIGHT)
        
        self.usrntr_shift_h = tk.IntVar()
        self.usrntr_shift_h.set(0)
        self.usrntr_shift_v = tk.IntVar()
        self.usrntr_shift_v.set(0)
        
        self.save_dir = tk.StringVar()
        self.save_dir.set("File save directory missing.")
        
        self.fname_prefix = tk.StringVar()
        self.fname_prefix.set("Prefix")
        self.fname_suffix = tk.StringVar()
        self.fname_suffix.set("Suffix")
        
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
        
    def setup_labelframe(self) -> None:
        """Create and place labelframes."""
        self.block_open = tk.LabelFrame(self.window, text="Open File", bg="white",)
        self.block_open.grid(column=0, row=0, padx=15, pady=5, sticky='w')
        
        self.block_cnvs_lbl = tk.LabelFrame(self.window, bg="white", borderwidth=0)
        self.block_cnvs_lbl.grid(column=0, row=0, pady=(47, 0), rowspan=2, sticky='n')
        
        self.block_clear = tk.LabelFrame(self.window, text="Remove in Canvas", bg="white")
        self.block_clear.grid(column=0, row=0, padx=(0, 15), sticky='e')
        
        self.block_canvas = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_canvas.grid(column=0, row=1, padx=15, pady=(11, 0), rowspan=3, sticky='n')
        
        self.block_cnvs_ctrl = tk.LabelFrame(self.window, bg="white", borderwidth=0, pady=0, border=0, highlightthickness=0)
        self.block_cnvs_ctrl.grid(column=0, row=4, padx=(0, 15), pady=(2, 0),  sticky='ne')
        
        self.block_switch = tk.LabelFrame(self.window, text="💧Mark with", bg="white")
        self.block_switch.grid(column=1, row=0, sticky='w')
        
        self.block_save = tk.LabelFrame(self.window, bg="white",)
        self.block_save.grid(column=1, row=0, pady=(0, 5), padx=(226, 0), sticky='sw')
        
        self.block_text = tk.LabelFrame(self.window, text="Text Edit", bg="white", padx=2, pady=2)
        self.block_text.grid(column=1, row=1, sticky='w')

        self.block_panel = tk.LabelFrame(self.window, text="Watermark Edit", bg="white", pady=2)
        self.block_panel.grid(column=1, row=2, sticky='nw')
        
        self.block_preview = tk.LabelFrame(self.window, text="Watermark Preview", bg="white", padx=10, pady=10)
        self.block_preview.grid(column=1, row=3, pady=0, columnspan=2, sticky='nsew')
        
        self.block_more_info = tk.LabelFrame(self.window, bg="white", border=0)
        self.block_more_info.grid(column=1, row=4, pady=(2, 20), sticky='new')
        
        self.window.rowconfigure(index=3, weight=1)
        # cite: https://stackoverflow.com/questions/45847313/what-does-weight-do-in-tkinter
    
    def setup_widget(self) -> None:
        """Create and place widgets."""
        # block open
        self.btn_open_image = tk.Button(self.block_open, text="Image", command=self.btnf_load_image_path)
        self.btn_open_image.grid(column=0, row=0, rowspan=2, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_open_image, 
            text="Open and select a image file to add watermark.", 
        )
        
        self.btn_open_images = tk.Button(
            self.block_open, 
            image=self.guicon_files, # type: ignore
            command=self.btnf_load_images_path
            )
        self.btn_open_images.grid(column=1, row=0, padx=2, pady=0)
        self.tip.add_to_queue(
            self.btn_open_images, 
            text="Open and select multiple image files to add watermark.", 
        )
        
        self.btn_open_folder = tk.Button(
            self.block_open, 
            image=self.guicon_folder, # type: ignore
            command=self.btnf_load_folder_path
            )
        self.btn_open_folder.grid(column=1, row=1, padx=2, pady=0)
        self.tip.add_to_queue(
            self.btn_open_folder, 
            text='Open and select a folder to add watermark.\naccepts ".png", ".jpg", ".jpeg" files.', 
        )
        
        self.btn_open_mark = tk.Button(self.block_open, text="Watermark", command=self.btnf_load_mark_path)
        self.btn_open_mark.grid(column=2, row=0, rowspan=2, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_open_mark, 
            text='Open and select a image file to be watermark.', 
        )
        
        # block canvas label
        self.lbl_canvas = tk.Label(
            self.block_cnvs_lbl, 
            text="Canvas", font=("Segoe Print", 24, "normal"), 
            bg="white", borderwidth=0
            )
        self.lbl_canvas.pack()
        self.tip.add_to_queue(
            self.lbl_canvas, 
            text="Display loaded images, shows watermark\npreview when mouse hover over image,\nleft click to set watermark on image,\ndon't forget to save the image.", 
        )
        
        # block clear
        self.btn_clear_preview = tk.Button(
            self.block_clear, text="Preview", 
            command= lambda: self.remove_exist_watermark(method='motion')
            )
        self.btn_clear_preview.grid(column=2, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_clear_preview, 
            text='Remove preview watermark in canvas.', 
        )
        
        self.btn_clear_mark = tk.Button(
            self.block_clear, text="Watermark", 
            command= lambda: self.remove_exist_watermark(method='clicked')
            )
        self.btn_clear_mark.grid(column=3, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_clear_mark, 
            text='Remove watermark in canvas.', 
        )
        
        # block canvas
        self.canvas = tk.Canvas(self.block_canvas, bg='white', width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.bind("<Leave>", lambda event: self.remove_exist_watermark(method='motion'))
        self.canvas.pack()
        
        # block canvas control
        self.ckbtnbrdr_preview = tk.Frame(self.block_cnvs_ctrl, bg="light gray") # ckbtnbrdr: checkbutton border
        self.ckbtn_preview = tk.Checkbutton(
            self.ckbtnbrdr_preview, 
            text="Show watermark preview", 
            variable=self.ckbtnvr_show_preview,
            command=self.update_canvas_bind,  
            font=FONT_FORMAT_SMALL, 
            bg='white', 
            )
        self.ckbtn_preview.select()
        self.ckbtn_preview.pack(padx=1, pady=1)
        self.ckbtnbrdr_preview.grid(column=0, row=0)
        
        self.ckbtnbrdr_snap = tk.Frame(self.block_cnvs_ctrl, bg="light gray")
        self.ckbtn_snap = tk.Checkbutton(
            self.ckbtnbrdr_snap, 
            text="Snap watermark to border", 
            variable=self.ckbtnvr_snap,
            font=FONT_FORMAT_SMALL, 
            bg='white', 
            )
        self.ckbtn_snap.select()
        self.ckbtn_snap.pack(padx=1, pady=1)
        self.ckbtnbrdr_snap.grid(column=1, row=0)
        self.tip.add_to_queue(
            self.ckbtn_snap, 
            text='Enable/disable restrict watermark to stay inside image border.', 
            side="tr", 
        )
        
        self.ckbtnbrdr_canvasbg = tk.Frame(self.block_cnvs_ctrl, bg="light gray")
        self.ckbtn_canvasbg = tk.Checkbutton(
            self.ckbtnbrdr_canvasbg, 
            text="Show canvas background", 
            variable=self.ckbtnvr_show_cnvs_bg,
            command=self.update_canvas_bg,
            font=FONT_FORMAT_SMALL, 
            bg='white', 
            )
        self.ckbtn_canvasbg.deselect()
        self.ckbtn_canvasbg.pack(padx=1, pady=1)
        self.ckbtnbrdr_canvasbg.grid(column=2, row=0)
        
        self.btn_cnvsbg_color = tk.Button(
            self.block_cnvs_ctrl, 
            text="Color", 
            font=FONT_FORMAT_SMALL, 
            compound="center", padx=0, pady=0, 
            command=lambda: self.choose_color(target="canvas bg"), 
            )
        self.btn_cnvsbg_color.grid(column=3, row=0)
        self.tip.add_to_queue(
            self.btn_cnvsbg_color, 
            text='Select color of canvas background,\ndefault to light gray.', 
            side="tr", 
        )
        
        # block switch
        self.btn_switch_image = tk.Button(self.block_switch, text="Image", command=self.btnf_image_mode)
        self.btn_switch_image.grid(column=0, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_switch_image, 
            text='Switch to use image as watermark.', 
        )
        
        self.btn_switch_text = tk.Button(self.block_switch, text="Text", command=self.btnf_text_mode)
        self.btn_switch_text.grid(column=1, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_switch_text, 
            text='Switch to use text as watermark.', 
        )
        
        # block save
        self.btn_preview = tk.Button(self.block_save, text="Preview", command=self.btnf_preview)
        self.btn_preview.grid(column=0, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_preview, 
            text='Preview the watermarked image, \nif watermark have pixels of misplacement\ngo to advanced settings in bottom right corner, \nadjust watermark position.', 
            side="bl"
        )
        
        self.btn_save = tk.Button(self.block_save, text="Save", command=self.btnf_save)
        self.btn_save.grid(column=1, row=0, padx=2, pady=2)
        
        self.btn_apply = tk.Button(self.block_save, text="Apply", command=self.btnf_tplvl_apply_show)
        self.btn_apply.grid(column=2, row=0, padx=2, pady=2)
        self.tip.add_to_queue(
            self.btn_apply, 
            text='Add watermark to all files selected,\nwatermark will be placed at relatively the same location.', 
            side="bl"
        )
        
        # block text
        row = 0
        self.lbl_text = tk.Label(self.block_text, text="Text", bg='white')
        self.lbl_text.grid(column=0, row=row, pady=(0, 2), sticky='w')
        
        self.tktxt_entry = tk.Text(self.block_text, cursor='xterm', width=33, height=1)
        self.tktxt_entry.insert(0.0, "Enter text as watermark")
        self.tktxt_entry.bind("<Button-1>", self.clear_tkentry_text)        
        self.tktxt_entry.grid(column=1, row=row, padx=(0, 10), sticky='w')
        
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
        self.lbl_font = tk.Label(self.block_text, text="Font", bg='white')
        self.lbl_font.grid(column=0, row=row, pady=(0, 2),sticky='w')
        
        self.cmbbx_font = ttk.Combobox(
            self.block_text, 
            values=self.font_names, 
            state="readonly", 
            cursor="hand2", 
            width=28
            )
        self.cmbbx_font.set(FONT)
        self.cmbbx_font.bind("<<ComboboxSelected>>", self.font_selected)
        self.cmbbx_font.grid(column=1, row=row, sticky='w')
        
        row = 2
        self.lbl_fontstyle = tk.Label(self.block_text, text="Style", bg='white')
        self.lbl_fontstyle.grid(column=0, row=row, pady=(0, 2), sticky='w')
        
        self.cmbbx_fontstyle = ttk.Combobox(
            self.block_text, 
            values=STYLES, 
            state="readonly", 
            cursor="hand2", 
            width=11
            )
        self.cmbbx_fontstyle.set('Regular')
        self.cmbbx_fontstyle.bind("<<ComboboxSelected>>", self.text_mark_maker)
        self.cmbbx_fontstyle.grid(column=1, row=row, sticky='w')
        
        self.lbl_fontsize = tk.Label(self.block_text, text="Size", bg='white')
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
            text="Color", 
            width=55, height=23, 
            image=self.pixel, 
            compound="center", padx=0, pady=0, 
            command=lambda: self.choose_color(target="text fg"), 
            )
        self.btn_color.grid(column=1, row=row, padx=(0, 30), pady=(2, 0), sticky='e')
        self.tip.add_to_queue(
            self.btn_color, 
            text='Select font color of text,\nuses light gray if canceled.', 
            side="bl"
        )
        
        # block panel
        row = 0
        self.lbl_rotate = tk.Label(self.block_panel, text="Rotate", bg='white')
        self.lbl_rotate.grid(column=0, row=row, padx=5, sticky='e')
        self.tip.add_to_queue(
            self.lbl_rotate, 
            text='Rotate the watermark,\nworks with mode text and image.', 
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
            command=lambda: self.btnf_reset_usrntr(target="rotate"), 
            bg="white"
            )
        self.btnrst_rotate.grid(column=2, row=row)
        self.tip.add_to_queue(
            self.btnrst_rotate, 
            text="Resets the value of rotate.", 
        )
        
        self.lbl_scale = tk.Label(self.block_panel, text="Scale", bg='white')
        self.lbl_scale.grid(column=3, row=row, padx=(32, 0))
        self.tip.add_to_queue(
            self.lbl_scale, 
            text="Scales the watermark, may cause blurry watermark,\npixels of misplacement or size difference.", 
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
            command=lambda: self.btnf_reset_usrntr(target="scale"), 
            bg="white"
            )
        self.btnrst_scale.grid(column=5, row=row, padx=(0, 5))
        self.tip.add_to_queue(
            self.btnrst_scale, 
            text="Resets the value of scale.", 
            side="bl"
        )
        
        row = 1
        self.lbl_opaque = tk.Label(self.block_panel, text="Opaque", bg='white')
        self.lbl_opaque.grid(column=0, row=row, padx=0)
        self.tip.add_to_queue(
            self.lbl_opaque, 
            text="Set the opaqueness of watermark.", 
        )
        
        self.scale_opaque = tk.Scale(
            self.block_panel, 
            from_=0, to=100, 
            variable=self.usrntr_opaque, 
            command=self.update_userequest,  # type: ignore
            orient='horizontal', 
            length=110, width=10, bg='white', 
            )
        self.scale_opaque.grid(column=1, row=row, padx=4, sticky='w')
        
        self.btnrst_opaque = tk.Button(
            self.block_panel, 
            image=self.guicon_reset, # type: ignore
            command=lambda: self.btnf_reset_usrntr(target="opaque"), 
            bg="white"
            )
        self.btnrst_opaque.grid(column=2, row=row)
        self.tip.add_to_queue(
            self.btnrst_opaque, 
            text="Resets the value of opaque.", 
        )
        
        self.ckbtnbrdr_grid = tk.Frame(self.block_panel, bg="light gray")
        self.ckbtn_grid = tk.Checkbutton(
            self.ckbtnbrdr_grid, 
            text="Grid", 
            variable=self.ckbtnvr_grid, 
            command=self.update_userequest, 
            bg='white'
            )
        self.ckbtn_grid.grid(padx=1, pady=1)
        self.ckbtnbrdr_grid.grid(column=3, row=row, padx=0, sticky='e')
        self.tip.add_to_queue(
            self.ckbtn_grid, 
            text="Enable/disable grid function.", 
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
            command=lambda: self.btnf_reset_usrntr(target="grid"), 
            bg="white")
        self.btnrst_grid.grid(column=5, row=row, padx=(0, 5))
        self.tip.add_to_queue(
            self.btnrst_grid, 
            text="Resets the value of grid.", 
            side="bl", 
        )
        
        # block preview
        self.lbl_watermark_preview = tk.Label(self.block_preview, bg='white')
        self.lbl_watermark_preview.grid(column=0, row=0)
        self.tip.add_to_queue(
            self.lbl_watermark_preview, 
            text="Preview of watermark,\nif text watermark got croped by border,\ngo to advanced settings in bottom right corner, \nadjust watermark width or height, or text position.", 
            side="bl", 
        )

        # block more info
        self.lbl_image_count = tk.Label(self.block_more_info, textvariable=self.text_image_count, anchor='w', width=22, bg='white')
        self.lbl_image_count.grid(column=0 ,row=0, sticky="w")
        
        self.btn_advset = tk.Button(self.block_more_info, text='Advanced Settings', width=15, command=self.btnf_tplvl_advset_show)
        self.btn_advset.grid(column=0, row=0, padx=(280, 0), sticky="w")
    
        # progress bar
        self.progress_bar = ttk.Progressbar(self.window, length=WINDOW_WIDTH)
        self.progress_bar.grid(column=0, row=5, columnspan=10, sticky='s')
        self.progress_bar.grid_forget()
    
    def load_defaults(self) -> None:
        """Load default images and functions that can be loaded before update tkinter Tk."""
        self.default_image_example = self.proper_load(
            filepath=FPATH_ASET_EG, 
            type_='image', 
            max_size=(440, 300)
            )
        
        self.update_switch_button()
        
        self.load_image() # loads default image here because load_image() requires tk.Canvas() exist.
        self.text_mark_maker()
        
        self.inidir_image = "" # reset initial directory here after all load_image() is done by __init__
        self.is_image = False
        
        self.tplvl_advset = tk.Toplevel(bg="white", padx=20, pady=10)
        self.tplvl_advset.resizable(width=False, height=False)
        self.setup_advset()
        self.tplvl_advset.withdraw()
        
        self.tplvl_savefmt = tk.Toplevel(bg="white", padx=20, pady=10)
        self.tplvl_savefmt.resizable(width=False, height=False)
        self.setup_savefmt()
        self.tplvl_savefmt.withdraw()
    
    def setup_rstble_and_custom(self) -> None:
        """
        Create dictionary to store resettable on GUI and default values, 
        create iterable to store custom widgets that has specific load process.
        """
        # widgets with default value
        self.rstble_vals = { # rstble: resettable
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
        
        # widgets with custom label that need to be placed after tk.Tk().update()
        self.rest_widget:list[sf.CustomScale] = [
            self.scale_scale, 
            self.scale_grid, 
        ]
        
        # widgets with custom label that need to be updated after it's placed
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
        
        # variables setup after others loaded
        self.text_image_count.set("")
        
        # spinboxes, validate input when user closing toplevel 
        self.spnbxs: list[sf.CustomSpinbox] = [
            self.spnbx_mark_w, 
            self.spnbx_mark_h, 
            self.spnbx_offset_h, 
            self.spnbx_offset_v, 
            self.spnbx_shift_h, 
            self.spnbx_shift_v, 
        ]
    
    def awake_custom(self) -> None:
        """
        Place custom label from custom widgets in support function, 
        Custom label need to be placed after update tkinter Tk.
        """
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
    
    def setup_advset(self) -> None: # advset: advanced settings
        """Create and place every widget on advanced settings toplevel."""
        row = 0
        self.ckbtnbrdr_mark_bg = tk.Frame(self.tplvl_advset, bg="light gray")
        self.ckbtn_mark_bg = tk.Checkbutton(
            self.ckbtnbrdr_mark_bg, 
            text="Show watermark background", 
            variable=self.ckbtnvr_show_mark_bg,
            command=lambda: (self.show_hidden_widget(), self.text_mark_maker()), 
            bg='white', 
            )
        self.ckbtn_mark_bg.grid(padx=1, pady=1)
        self.ckbtnbrdr_mark_bg.grid(column=0, row=row, padx=(0, 15), sticky='w')
        
        self.btn_cnvsbg_color = tk.Button(
            self.tplvl_advset, text="Color", 
            command=lambda: self.choose_color(target="text bg")
            )
        self.btn_cnvsbg_color.grid(column=1, row=row, padx=(0, 6))
        self.tip.add_to_queue(
            self.btn_cnvsbg_color, 
            text='Select color of background of watermark,\nuses light gray if canceled.', 
            side="bl"
        )
        
        row = 1
        self.ckbtnbrdr_wrng_mark_bg = tk.Frame(self.tplvl_advset, bg="light gray")
        self.ckbtn_wrng_mark_bg = tk.Checkbutton(
            self.ckbtnbrdr_wrng_mark_bg, 
            text="Warning when watermark contains background", 
            variable=self.ckbtnvr_wrng_mark_bg, 
            bg='white', 
            )
        self.ckbtn_wrng_mark_bg.grid(padx=1, pady=1)
        self.tip.add_to_queue(
            self.ckbtn_wrng_mark_bg, 
            text='Enable/disable the warning pop-up window.', 
            side="b"
        )
        
        row = 2
        self.sprtr_watermark_bg = ttk.Separator(self.tplvl_advset, orient='horizontal')
        self.sprtr_watermark_bg.grid(column=0, row=row, columnspan=2, pady=(3, 5), sticky="we")
        
        row = 3
        self.lbl_border_w = tk.Label(
            self.tplvl_advset, 
            text="A) Adjust watermark width", 
            bg='white'
            )
        self.lbl_border_w.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_border_w, 
            text='Adjust total width of watermark,\nthe width gray box shown below.', 
            side="b"
        )
        
        self.spnbx_mark_w = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            textvariable=self.usrntr_border_w, 
            cz_variable=self.usrntr_border_w, 
            cmd=self.text_mark_maker, 
            width=6
            )
        self.spnbx_mark_w.bind("<KeyRelease>", self.spnbx_mark_w.command)
        self.spnbx_mark_w.grid(column=1, row=row, sticky='e')
        
        row = 4
        self.lbl_border_h = tk.Label(
            self.tplvl_advset, 
            text="B) Adjust watermark height", 
            bg='white'
            )
        self.lbl_border_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_border_h, 
            text='Adjust total height of watermark,\nthe height gray box shown below.', 
            side="b"
        )
        
        self.spnbx_mark_h = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            textvariable=self.usrntr_border_h, 
            cz_variable=self.usrntr_border_h, 
            cmd=self.text_mark_maker, 
            width=6
            )
        self.spnbx_mark_h.bind("<KeyRelease>", self.spnbx_mark_h.command)
        self.spnbx_mark_h.grid(column=1, row=row, sticky='e')
        
        row = 5
        self.lbl_offset_h = tk.Label(
            self.tplvl_advset, 
            text="C) Adjust text position horizontally(Δh)", 
            bg='white'
            )
        self.lbl_offset_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_offset_h, 
            text='Adjust text position in watermark,\nthe blue text in gray box, stands for\ncurrent text position in watermark.\nIncrease makes text move right,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_offset_h = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            textvariable=self.usrntr_offset_w, 
            cz_variable=self.usrntr_offset_w, 
            cmd=self.text_mark_maker, 
            width=6
            )
        self.spnbx_offset_h.bind("<KeyRelease>", self.spnbx_offset_h.command)
        self.spnbx_offset_h.grid(column=1, row=row, sticky='e')
        
        row = 6
        self.lbl_offset_v = tk.Label(
            self.tplvl_advset, 
            text="D) Adjust text position vertically(Δv)", 
            bg='white'
            )
        self.lbl_offset_v.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_offset_v, 
            text='Adjust text position in watermark,\nthe blue text in gray box, stands for\ncurrent text position in watermark.\nIncrease to move text downward,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_offset_v = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            textvariable=self.usrntr_offset_h, 
            cz_variable=self.usrntr_offset_h, 
            cmd=self.text_mark_maker, 
            width=6
            )
        self.spnbx_offset_v.bind("<KeyRelease>", self.spnbx_offset_v.command)
        self.spnbx_offset_v.grid(column=1, row=row, sticky='e')
        
        row = 7
        self.lbl_shift_h = tk.Label(
            self.tplvl_advset, 
            text="E) Adjust watermark position horizontally", 
            bg='white'
            )
        self.lbl_shift_h.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_shift_h, 
            text='Adjust watermark in image,\nbecause load image to canvas\nmay cause pixels of deviation.\nIncrease makes watermark move right,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_shift_h = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            textvariable=self.usrntr_shift_h, 
            cz_variable=self.usrntr_shift_h, 
            cmd=self.text_mark_maker, 
            width=6
            )
        self.spnbx_shift_h.bind("<KeyRelease>", self.spnbx_shift_h.command)
        self.spnbx_shift_h.grid(column=1, row=row, sticky='e')
        
        row = 8
        self.lbl_shift_v = tk.Label(
            self.tplvl_advset, 
            text="F) Adjust watermark position vertically", 
            bg='white'
            )
        self.lbl_shift_v.grid(column=0, row=row, padx=(2, 0), sticky='w')
        self.tip.add_to_queue(
            self.lbl_shift_v, 
            text='Adjust watermark in image,\nbecause load image to canvas\nmay cause pixels of deviation.\nIncrease to move watermark downward,\nvice versa.', 
            side="b"
        )
        
        self.spnbx_shift_v = sf.CustomSpinbox(
            self.tplvl_advset, 
            from_=-200, to=200, 
            textvariable=self.usrntr_shift_v, 
            cz_variable=self.usrntr_shift_v, 
            cmd=self.text_mark_maker, 
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
            command=lambda: self.btnf_reset_usrntr(target="advset"), 
            )
        self.btnrst_advset.grid(column=1, row=row, pady=(3, 0), sticky="e")
        self.tip.add_to_queue(
            self.btnrst_advset, 
            text='Reset all adjustments.', 
            side="bl"
        )
        
        row = 10
        self.sprtr_adjust = ttk.Separator(self.tplvl_advset, orient='horizontal')
        self.sprtr_adjust.grid(column=0, row=row, columnspan=2, pady=(3, 5), sticky="we")
        
        row = 11
        self.lbl_example = tk.Label(
            self.tplvl_advset, 
            text="Example Diagram:", 
            bg="white"
            )
        self.lbl_example.grid(column=0, row=row, sticky="w")
        
        row = 12
        self.lbl_example_image = tk.Label(
            self.tplvl_advset, 
            image=self.default_image_example, # type: ignore
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
            text="Show Tooltip", 
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
            text="Enable/disable tooltip,\nthe text you currently looking at.", 
            side="t"
        )
        
        self.btn_hide_tplvl = tk.Button(
            self.tplvl_advset, 
            text="Done", 
            command=self.btnf_tplvl_advset_hide, 
            )
        self.btn_hide_tplvl.grid(column=1, row=row, sticky="e")
        
    def setup_savefmt(self) -> None: # savefmt: save format
        """Create and place every widget on save format toplevel."""
        row = 0
        self.btn_savedir = tk.Button(
            self.tplvl_savefmt, 
            text="Directory", 
            command=self.btnf_savedir, 
            )
        self.btn_savedir.grid(column=0, row=row, padx=(0, 10), sticky='w')
        self.tip.add_to_queue(
            self.btn_savedir, 
            text="Select a directory to save watermarked images.", 
        )
        
        self.lbl_savedir = tk.Label(
            self.tplvl_savefmt, 
            textvariable=self.save_dir, 
            fg="red", 
            )
        self.lbl_savedir.grid(column=1, row=row, columnspan=2, sticky='w')
        self.tip.add_to_queue(
            self.lbl_savedir, 
            text="Specified directory to save watermarked images.", 
            side="b", 
        )
        
        row = 1
        self.sprtr_fname_scheme = ttk.Separator(self.tplvl_savefmt, orient='horizontal')
        self.sprtr_fname_scheme.grid(column=0, row=row, columnspan=3, pady=(3, 5), sticky="we")
        
        row = 2
        self.lbl_fname_scheme = tk.Label(
            self.tplvl_savefmt, 
            text="File Naming Scheme", 
            bg="white", 
            )
        self.lbl_fname_scheme.grid(column=0, row=row, columnspan=2, sticky="w")
        
        row = 3
        self.ckbtnbrdr_fname_fmt = tk.Frame(self.tplvl_savefmt, bg="light gray")
        self.ckbtn_fname_fmt = tk.Checkbutton(
            self.ckbtnbrdr_fname_fmt, 
            text="Format  ", 
            variable=self.ckbtnvr_fname_fmt, 
            command=lambda: self.btnf_ckbtn_switch(scheme="format"), 
            bg="white", 
            )
        self.ckbtn_fname_fmt.pack(padx=1, pady=1)
        self.ckbtnbrdr_fname_fmt.grid(column=0, row=row, sticky='w')
        self.tip.add_to_queue(
            self.ckbtn_fname_fmt, 
            text="Format file name with added text before and/or \nafter original file name, left both field empty \nwill use the original file name.", 
        )
        
        self.entry_prefix = tk.Entry(
            self.tplvl_savefmt, 
            textvariable=self.fname_prefix, 
            width=20, 
            bg="#ededed"
            )
        self.entry_prefix.bind("<KeyRelease>", self.update_fname_example)
        self.entry_prefix.grid(column=1, row=row, sticky='w')
        
        self.btn_clear_entry_prefix = tk.Button(
            self.tplvl_savefmt, 
            text="X", 
            command=lambda: (self.entry_prefix.delete(0, tk.END), self.update_fname_example()),  
            image=self.pixel, compound="center", 
            border=0, width=22, height=22, padx=0, pady=0, 
            )
        px = self.entry_prefix.winfo_reqwidth() - self.btn_clear_entry_prefix.winfo_reqwidth() - 1
        self.btn_clear_entry_prefix.grid(column=1, row=row, padx=(px, 0), sticky='w')
        
        self.entry_suffix = tk.Entry(
            self.tplvl_savefmt, 
            textvariable=self.fname_suffix, 
            width=20, 
            bg="#ededed"
            )
        self.entry_suffix.bind("<KeyRelease>", self.update_fname_example)
        self.entry_suffix.grid(column=1, row=row, padx=(252, 0), sticky='w')
        
        self.btn_clear_entry_suffix = tk.Button(
            self.tplvl_savefmt, 
            text="X", 
            command=lambda: (self.entry_suffix.delete(0, tk.END), self.update_fname_example()),  
            image=self.pixel, compound="center", 
            border=0, width=22, height=22, padx=0, pady=0, 
            )
        px = self.entry_suffix.winfo_reqwidth() - self.btn_clear_entry_suffix.winfo_reqwidth() - 1
        self.btn_clear_entry_suffix.grid(column=1, row=row, padx=(252+px, 0), sticky='w')
        
        row = 4
        self.ckbtnbrdr_fname_rename = tk.Frame(self.tplvl_savefmt, bg="light gray")
        self.ckbtn_fname_rename = tk.Checkbutton(
            self.ckbtnbrdr_fname_rename, 
            text="Rename", 
            variable=self.ckbtnvr_fname_rename, 
            command=lambda: self.btnf_ckbtn_switch(scheme="rename"), 
            bg="white", 
            )
        self.ckbtn_fname_rename.pack(padx=1, pady=1)
        self.ckbtnbrdr_fname_rename.grid(column=0, row=row, sticky='w')
        self.tip.add_to_queue(
            self.ckbtn_fname_rename, 
            text="Discards original file name,\noutput names will be Name-1, Name-2, ..."
        )
        
        self.entry_rename = tk.Entry(
            self.tplvl_savefmt, 
            textvariable=self.fname_name, 
            width=41, 
            bg="#ededed"
            )
        self.entry_rename.bind("<KeyRelease>", self.update_fname_example)
        self.entry_rename.grid(column=1, row=row, columnspan=2, sticky='w')

        self.btn_clear_entry_rename = tk.Button(
            self.tplvl_savefmt, 
            text="X", 
            command=lambda: (self.entry_rename.delete(0, tk.END), self.update_fname_example()), 
            border=0, width=22, height=22, padx=0, pady=0, 
            image=self.pixel, compound="center", 
            )
        px = self.entry_rename.winfo_reqwidth() - self.btn_clear_entry_rename.winfo_reqwidth() - 1
        self.btn_clear_entry_rename.grid(column=1, row=row, padx=(px, 0), sticky='w')
        
        row = 5
        self.lbl_filefmt = tk.Label(
            self.tplvl_savefmt, 
            text="File Format", 
            bg="white", 
            )
        self.lbl_filefmt.grid(column=0, row=row, sticky='w')
        
        self.cmbbx_filefmt = ttk.Combobox(
            self.tplvl_savefmt, 
            values=['.png', '.jpg', '.jpeg'], 
            state="readonly", 
            cursor="hand2", 
            width=10, 
            )
        self.cmbbx_filefmt.set('.png')
        self.cmbbx_filefmt.bind("<<ComboboxSelected>>", self.update_fname_example)
        self.cmbbx_filefmt.grid(column=1, row=row, columnspan=2, sticky='w')
        
        row = 6
        self.lbl_example_fname = tk.Label(
            self.tplvl_savefmt, 
            text="Example", 
            bg="white", 
            )
        self.lbl_example_fname.grid(column=0, row=row, sticky='w')
        self.tip.add_to_queue(
            self.lbl_example_fname, 
            text="Preview of file name under current\nnaming scheme, with first file as example."
        )
        
        self.lbl_outcome_fname = tk.Label(
            self.tplvl_savefmt, 
            textvariable=self.fname_example,
            )
        self.lbl_outcome_fname.grid(column=1, row=row, pady=7, columnspan=3, sticky='w')
        
        row = 7
        self.btn_apply_savefmt = tk.Button(
            self.tplvl_savefmt, 
            text="Execute", 
            command=self.btnf_apply_to_images, 
            )
        self.btn_apply_savefmt.grid(column=1, row=row, sticky="w")
        self.tip.add_to_queue(
            self.btn_apply_savefmt, 
            text="Add watermark to all images selected,\nsave images by naming scheme above."
        )
        
        self.btn_savefmt_cancel = tk.Button(
            self.tplvl_savefmt, 
            text="Cancel", 
            command=self.btnf_tplvl_apply_hide
            )
        self.btn_savefmt_cancel.grid(column=1, row=row, padx=(416, 0), sticky="w")
        
    # GUI functions
    def btnf_load_image_path(self) -> None: # btnf: button function
        """Ask user to select a image file as the image to be watermarked."""
        filepath = filedialog.askopenfilename(
            title="Select A Image To Watermark", 
            initialdir=self.inidir_image, 
            filetypes=FTYPE, 
            )
        if filepath == "":
            return None
        self.filepath_image = filepath
        self.load_image()
        # Additional thought:
        # Add load image mode RGB, RGBA ..., cite: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
        # Use combobox bind with `<<ComboboxSelected>>`, command set `self.load_image()`, 
        # reload the image when selected, if image have conflict with RGBA mode, 
        # user can change the mode manually, but `self.save_image` uses Image.alpha_composite(), 
        # which specifically requires Image mode=RGBA, also no precedent yet so postponed.
        
    def btnf_load_images_path(self) -> None:
        """Ask user to select multiple image files to be watermarked."""
        self.apply_paths = []
        filepaths = filedialog.askopenfilenames(
            title="Select Images To Watermark", 
            initialdir=self.inidir_image, 
            filetypes=FTYPE, 
            )
        if filepaths == "":
            return None
        for filepath in filepaths:
            self.apply_paths.append(filepath)
        self.filepath_image = self.apply_paths[0]
        self.load_image()
        
    def btnf_load_folder_path(self) -> None:
        """Ask user to select a folder, filtered to get image files to be watermarked."""
        self.apply_paths = []
        folder = filedialog.askdirectory(
            title="Select Folder To Watermark", 
            initialdir=self.inidir_image, 
            )
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
        """Ask user to select a image file as watermark."""
        filepath = filedialog.askopenfilename(
            title="Select Image As Watermark", 
            initialdir=self.inidir_mark, 
            filetypes=FTYPE, 
            )
        if filepath == "":
            return None
        self.filepath_mark = filepath
        self.inidir_mark, _ = self.filepath_mark.rsplit("/", maxsplit=1)
        self.load_mark()
    
    def btnf_image_mode(self) -> None:
        """
        Change to image watermark (if exists) from text watermark, 
        does nothing if there's none.
        """
        if self.condition_met(from_="btnf_image_mode"):
            self.switch_state = 'image'
            self.update_switch_button()
            self.load_mark()
        
    def btnf_text_mode(self) -> None:
        """change to text watermark from image watermark."""
        self.switch_state = 'text'
        self.update_switch_button()
        self.text_mark_maker()
    
    def btnf_preview(self) -> None:
        """Show preview of watermarked image."""
        if self.condition_met(from_="btnf_preview"):
            self.apply_watermark()
            self.result_image.show()
        
    def btnf_save(self) -> None:
        """
        Ask user directory, save the watermarked image,
        load the next image file if is any.
        """
        if not self.condition_met(from_="btnf_save"):
            return None
        print(self.filepath_image)
        
        dir_, fname = self.filepath_image.rsplit("/", maxsplit=1)
        name, type_ = fname.rsplit(".", maxsplit=1)
        fname = name + " - watermarked." + type_
        
        if self.inidir_save != "":
            dir_ = self.inidir_save
        
        filepath = filedialog.asksaveasfilename(
            title="Save Watermarked Image As", 
            filetypes=FTYPE , 
            initialdir=dir_ , 
            initialfile=fname , 
            )
        if filepath == "":
            return None
        self.inidir_save, _ = filepath.rsplit("/", maxsplit=1)
        
        self.apply_watermark()
        self.save_image(abs_path=filepath)
        
        # prep the next image if there's any
        if len(self.apply_paths) > 1:
            self.apply_paths.remove(self.filepath_image)
            self.filepath_image = self.apply_paths[0]
        elif len(self.apply_paths) == 1:
            self.apply_paths.remove(self.filepath_image)
        
        # load the next image if there's any, resets everything if none
        if len(self.apply_paths) < 1:
            self.reset_to_default_image()
        else:
            self.load_image()
            self.update_canvas_bind()
        
    def btnf_tplvl_apply_show(self) -> None:
        """
        Show and focus (deiconify) the save format toplevel, 
        if the toplevel does not exist, create one and setup widgets inside it.
        """
        if not self.condition_met(from_="btnf_apply"):
            return None
        
        if self.tplvl_savefmt.winfo_exists():
            self.tplvl_savefmt.deiconify()
        else:
            self.tplvl_savefmt = tk.Toplevel(bg="white", padx=20, pady=5)
            self.tplvl_savefmt.resizable(width=False, height=False)
            self.setup_savefmt()
        self.update_fname_example()
        
    def btnf_tplvl_advset_show(self) -> None:
        """
        Show and focus (deiconify) the advanced settings toplevel, 
        if the toplevel does not exist, create one and setup widgets inside it.
        """
        if self.tplvl_advset.winfo_exists():
            self.tplvl_advset.deiconify()
        else:
            self.tplvl_advset = tk.Toplevel(bg="white", padx=20, pady=5)
            self.tplvl_advset.resizable(width=False, height=False)
            self.setup_advset()
            
    # GUI functions in toplevel: save format
    def btnf_savedir(self) -> None:
        """Ask user the directory to save images."""
        dir_ = filedialog.askdirectory(title="Select Save Directory")
        if dir_ == "":
            return None
        self.save_dir.set(dir_)
        self.lbl_savedir.config(fg="black")
        self.tplvl_savefmt.deiconify()
    
    def btnf_ckbtn_switch(self, scheme:_ckbtn_switch) -> None:
        """
        Switches save file (watermarked image) naming scheme between `format` and `rename`,
        `format` retains original file name, format it with additional prefix or suffix, 
        `rename` discards original file name, new file name will be `UserEnterFileName-1.png, UserEnterFileName-2.png, ...etc`.
        
        Parameters
        ----------
        scheme (_ckbtn_switch)
            The naming scheme.
        """
        if scheme == "format":
            self.ckbtn_fname_fmt.select()
            self.ckbtn_fname_rename.deselect()
        elif scheme == "rename":
            self.ckbtn_fname_fmt.deselect()
            self.ckbtn_fname_rename.select()
        self.update_fname_example()
    
    def btnf_apply_to_images(self, event:tk.Event|None=None) -> None:
        """
        Ask user directory to save the watermarked images, 
        apply watermark and save the image at directory,
        load the next image file if there is any.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        if not self.condition_met(from_="apply_to_folder"):
            return None
        
        save_dir = self.save_dir.get()
        
        self.update_progress_bar("set", max_=len(self.apply_paths))
        self.update_progress_bar("start")
        
        for idx, path in enumerate(self.apply_paths):
            self.filepath_image = path
            self.load_image()
            
            fname = self.get_fname(idx=idx)
            save_path = save_dir + "/" + fname
            self.apply_watermark()
            self.save_image(abs_path=save_path)
            self.update_progress_bar("step")
        
        self.update_progress_bar("hide", path=save_dir)
        self.reset_to_default_image()
    
    def btnf_tplvl_apply_hide(self) -> None:
        """Hide (withdraw) the save format toplevel."""
        self.tplvl_savefmt.withdraw()
    
    # GUI functions in toplevel: advanced settings
    def btnf_reset_usrntr(self, target:_rstable) -> None:
        """
        Resets value of target widgets with default value.
        
        Parameter
        ---------
        target (_rstable)
            The widget to reset value.
        """
        if target == "advset":
            for idx, value in enumerate(self.rstble_vals[target]["attr_name"]):
                value.set(self.rstble_vals[target]["default_val"][idx])
        else:
            self.rstble_vals[target]["attr_name"].set(
                self.rstble_vals[target].get("default_val")
            )
        for widget in self.standby_widget:
            widget.command()
        self.update_userequest()
    
    def btnf_ckbtn_tooltip(self) -> None:
        """Enable/disable all tooltips based on state of tkinter Checkbutton."""
        if self.ckbtnvr_tooltip.get():
            self.tip.enable_all()
        else:
            self.tip.disable_all()
    
    def btnf_tplvl_advset_hide(self):
        """
        Hide(withdraw) the advanced settings toplevel.
        """
        if self.adjust_value_validate() and self.length_valid():
            self.tplvl_advset.withdraw()
        
    # key functions
    def operate(self) -> None:
        """The power button."""
        self.window.mainloop()
        
    def get_usrntr_text(self) -> str:
        """
        Get value of user entered text for watermark in tkinter Entry.
        
        Returns
        -------
        str
            User entered text.
        """
        return self.tktxt_entry.get(0.0, "end-1c")
        
    def proper_load(
        self, 
        *, 
        filepath: str, 
        type_: _img, 
        alpha: int|None = 255, 
        angle: int = 0,
        max_size: tuple[int, int]|None = None, 
        ) -> ImageTk.PhotoImage:
        """
        Load image from filepath to PIL.Image.Image, 
        convert image `mode` to `RGBA`, sets alpha, angle, 
        resizes it and convert to PIL.ImageTk.PhotoImage.

        Parameters
        ----------
        filepath (str) 
            File path of the loading image.
        type (_img)
            Type of loading image.
        alpha (int|None, optional. Defaults to 255)
            Add translucent to the image, ranging from 0 to 255. translucent% = alpha/255.
        angle (int, optional. Defaults to 0) 
            The rotation of image.
        max_size (tuple[int, int]|None, optional. Defaults to None)
            Set maximum width an height of the image, 
            the image will scale up proportionally until the width and/or height reached max_size.
        
        Returns
        -------
        ImageTk.PhotoImage
            The image after modify and converted to PIL.PhotoImage.
        """
        # // Load image and convert it to RGBA, to avoid ValueError: images do not match
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
        Load image by filepath, calculate all relevant attributes, 
        remove previous image and create the image on canvas.
        
        The value of `self.filepath_image` must be set in advance of function call.
        """
        # remove previous image
        if self.is_image:
            self.canvas.delete(self.canvas_image)
        
        # load image
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
        self.update_image_count()
        self.inidir_image, _ = self.filepath_image.rsplit("/", maxsplit=1)
        
        if self.is_mark:
            self.update_mark_size()
            self.update_canvas_bind()
        
    def load_mark(self) -> None:
        """
        Load image by filepath, calls all relevant functions.
        
        The value of `self.filepath_mark` must be set in advance of function call, 
        """
        opaque = self.usrntr_opaque.get()
        alpha = round(np.round((opaque/100) * 255))
        angle = self.usrntr_rotate.get()
        
        self.ghost = self.mark = self.proper_load(
            filepath=self.filepath_mark, 
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
    
    def canvas_action(self, event:tk.Event, *, method:_cnvs_actn) -> None:
        """
        Main function in responce for user action in canvas,
        manage everything after mouse movement and click.
        
        Parameters
        ----------
        event (tk.Event)
            The tkinter event.
        method (_cnvs_actn)
            User action on canvas.
        """
        try:
            self.remove_exist_watermark(method=method)
        except AttributeError:
            print("first time only AttributeError, no worries.")
            
        x0, y0 = event.x, event.y
        x, y, snap_position = self.mouse_loc_calibrate(x0, y0) 
        
        if method == 'clicked':
            if not self.condition_met(from_="canvas_clicked"):
                return None
            
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
        
    def draw_watermark(self, x:int, y:int, method:_cnvs_actn, grid:bool=False) -> None:
        """
        Draw watermark in canvas, has two method: clicked and motion, 
        `clicked` will place self.mark on canvas, 
        `motion` will place self.ghost (a transparent version watermark) on canvas, 
        self.ghost will follow the cursor's last location on canvas.
        
        Parameters
        ----------
        x (int)
            The x coordinate of the location to draw on the canvas.
        y (int)
            The y coordinate of the location to draw on the canvas.
        method (_cnvs_actn)
            User action on canvas.
        grid (bool. Defaults to False)
            Enable/disable grid function.
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
        Make sure wherever user's mouse is (in canvas), 
        center of watermark and preview will be at the mouse location, 
        due to canvas has padding, additional calculate is needed.
        When snap is on, watermark and preview will be at the nearest distance to mouse location,
        while stay inside of image border.
        
        Parameters
        ----------
        x (int)
            The x coordinate of mouse location.
        y (int)
            The y coordinate of mouse location.

        Returns
        -------
        tuple[int, int, tuple[int, int]|None]
            `(x, y, (x_snap, y_snap)|None)`
            Mouse location on canvas, None if watermark isn't snapped to border of image.

        Raises
        ------
        ValueError
            User click on somewhere unexpected, can't imagine how, so print everything thought will be helpful.
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
    
    def text_mark_maker(self, event:tk.Event|None=None) -> None:
        """
        Make text watermark based on user input in GUI, 
        this function will generate a new PIL.ImageTk.PhotoImage every time it's called, 
        said image wont be saved.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        name = self.cmbbx_font.get()
        style = self.cmbbx_fontstyle.get()
        rq_font = self.fonts_dict[name][style] # rq: requested
        pixel_size = self.usrntr_fontsize.get() / 0.75
        border_w = self.usrntr_border_w.get()
        border_h = self.usrntr_border_h.get()
        opaque = self.usrntr_opaque.get()
        alpha = round(np.round((opaque/100) * 255))
        angle = self.usrntr_rotate.get()

        # font of text
        fnt = ImageFont.truetype(font=rq_font, size=pixel_size) 
        offset = (self.usrntr_offset_w.get(), self.usrntr_offset_h.get())
        text_color = *self.current_font_rgb, alpha
        
        # get border of the text from PIL
        _ = Image.new("RGBA", MARK_MAX_SIZE)
        f = ImageDraw.Draw(_)
        f_bbox = f.textbbox((0, 0), self.get_usrntr_text(), font=fnt)
        
        # get text border sizes of the text with font
        width = f_bbox[2] - f_bbox[0] + border_w
        height = f_bbox[3] - f_bbox[1] + border_h
        
        # store bbox value to check if width and height of image is larger than 0
        # (later when user closes advanced settings toplevel, at function: btnf_tplvl_advset_hide)
        self.mark_bbox = f_bbox
        
        if self.ckbtnvr_show_mark_bg.get():
            base = Image.new("RGBA", (width, height), (*self.mark_bg, 255))
        else:
            base = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            
        d = ImageDraw.Draw(base)
        d.text(offset, self.get_usrntr_text(), font=fnt, fill=text_color)
        
        mark_base = base.copy().convert("RGBA")
        mark_rot = mark_base.rotate(angle, expand=True)
        
        self.store_pil(pil=mark_rot, type_="text")
        size = self.get_image_size(pil=mark_rot, type_="text")
        
        mark = mark_rot.resize(size)
        self.ghost = self.mark = ImageTk.PhotoImage(mark)
        
        self.is_mark = True
        self.clicked = False
        self.update_mark_offset()
        
        # update preview
        self.lbl_watermark_preview.config(image=self.mark) # type: ignore
    
    def apply_watermark(self) -> None:
        """Apply watermark to image."""
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
        self.result_image = self.image_pil.copy()
        self.result_image.alpha_composite(result_mark, offset)
        
    def save_image(self, *, abs_path:str) -> None:
        """
        Save watermarked image at path.
        
        Parameters
        ----------
        abs_path (str)
            Directory to save watermarked image.
        """
        self.result_image.save(abs_path)
        
    def grid_mark_maker(self, x:int, y:int, grid_space:int, mark:Image.Image) -> Image.Image:
        """
        Generate a transpraent image contain grid of watermark, said image wont be saved.
        The generated image will be used as watermark.
        
        Parameters
        ----------
        x (int)
            The x coordinate of mouse location.
        y (int)
            The y coordinate of mouse location.
        grid_space (int)
            Space between watermarks on grid.
        mark (Image.Image)
            Watermark image to use in grid. 

        Returns
        -------
        Image.Image
            Transpraent Image contain grid of watermark with space in between.
        """
        width = self.image_pil.width
        height = self.image_pil.height
        
        with Image.new("RGBA", (width, height)) as base:
            locs = self.grid_calculate(x, y, grid_space, on="image")
            for x in locs['x']:
                for y in locs['y']:
                    base.paste(im=mark, box=(x,y))
            return base.copy()
    
    def grid_calculate(self, x:int, y:int, grid_space:int, on:_loc) -> dict[str, list[int]]:
        """
        Calculate all the positions for the center of the watermark on the grid.

        Parameters
        ----------
        x (int)
            The x coordinate of mouse location.
        y (int)
            The y coordinate of mouse location.
        grid_space (int)
            Space between watermarks on grid.
        on (_loc)
            Location of grid is going to be placed at.

        Returns
        -------
        dict[str, list[int]]
            `{"x": [x_loc, ...], "y": [y_loc, ...]}`
            The x, y coordinates of watermark on the grid.
        """
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
    
    # update stuff
    def update_image_count(self) -> None:
        """Update the number of image(s) user selected to be watermarked."""
        if self.apply_paths == []:
            self.text_image_count.set("Image loaded: 1")
        else:
            self.text_image_count.set(f"Images loaded: {len(self.apply_paths)}")
    
    def update_userequest(self, event:tk.Event|None=None) -> None:
        """
        Change to image or text watermark based on button pressed.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        if self.switch_state == "image":
            self.load_mark()
        elif self.switch_state == "text":
            self.text_mark_maker()
        self.remove_exist_watermark(method="motion")
    
    def update_canvas_bg(self) -> None:
        """Enable/disable background color of canvas."""
        if self.ckbtnvr_show_cnvs_bg.get():
            self.canvas.config(bg=self.canvas_bg)
        else:
            self.canvas.config(bg="white")
        
    def update_canvas_bind(self) -> None:
        """
        Bind M1 and mouse motion base on if watermark and image exists, 
        unbind M1 and mouse motion if otherwise.
        """
        if self.is_mark and self.is_image:
            self.canvas.bind("<Button-1>", lambda event: self.canvas_action(event, method='clicked'))
            if self.ckbtnvr_show_preview.get():
                self.canvas.bind("<Motion>", lambda event: self.canvas_action(event, method='motion'))
            else:
                self.canvas.unbind("<Motion>")
            self.remove_exist_watermark(method="motion")
            self.remove_exist_watermark(method="clicked")
        else:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Motion>")
        
    def update_mark_size(self) -> None:
        """Update watermark size to scale with image scale."""
        width = np.round((self.mark_pil.width * self.usrntr_scale.get()) / self.image_width_scale)
        height = np.round((self.mark_pil.height * self.usrntr_scale.get()) / self.image_height_scale)
        size = (round(width), round(height))
        
        image_resize = self.mark_pil.resize(size)
        
        self.ghost = self.mark = ImageTk.PhotoImage(image_resize)
        self.lbl_watermark_preview.config(image=self.mark) # type: ignore
        
    def update_mark_offset(self) -> None:
        """
        Calculate the distance from center of watermark to the left and top as min,
        and to the right and bottom as max.
        The value min and max will be used at calculating location of watermark,
        to restrict watermark to stay inside image border when snap is enabled.
        """
        self.mark_offset_x_min = math.floor(self.mark.width() / 2)
        self.mark_offset_y_min = math.floor(self.mark.height() / 2)
        self.mark_offset_x_max = self.mark.width() - self.mark_offset_x_min
        self.mark_offset_y_max = self.mark.height() - self.mark_offset_y_min
    
    def update_switch_button(self) -> None:
        """
        Switch watermark to image or text, not-the-current one,
        remove previous created watermark and preview.
        """
        if self.switch_state == 'image':
            self.btn_switch_image.config(relief='sunken')
            self.btn_switch_text.config(relief='raised')
        elif self.switch_state == 'text':
            self.btn_switch_image.config(relief='raised')
            self.btn_switch_text.config(relief='sunken')
        self.remove_exist_watermark(method="all")
            
    def update_fname_example(self, event:tk.Event|None=None) -> None:
        """
        Update the file name example on save format toplevel.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        filename = self.get_fname()
        self.fname_example.set(filename)
    
    def update_progress_bar(self, execute:_pbar, max_:int|None=None, path:str|None=None) -> None:
        """
        Progress bar control function.

        Parameters
        ----------
        execute (_pbar)
            which operation to execute.
            `set`, set the maximum value of progress bar.
            `start`, show the progress bar on app.
            `step`, add 1 to the progress bar value.
            `hide`, hide the progress bar on app.
        max_ (int|None, optional. Defaults to None)
            The maximum value of progress bar.
        path (str|None, optional. Defaults to None)
            The directory to save watermarked image file.
        """
        if execute == "set":
            self.progress_bar['maximum'] = max_
        elif execute == "start":
            self.progress_bar.grid(column=0, row=5, columnspan=10, sticky='s')
        elif execute == "step":
            if self.progress_bar['value'] == self.progress_bar['maximum'] - 1:
                self.progress_bar['value'] = self.progress_bar['maximum']
            else:
                self.progress_bar.step()
        elif execute == "hide":
            messagebox.showinfo(title="operation completed successfully", message=f"all file saved at directory:     \n{path}")
            self.progress_bar.grid_forget()
            self.progress_bar['value'] = 0
        self.window.update()
        
    # support functions
    def customize_titltbar(self) -> None:
        """
        Remove buttons (minimize, maximize/restore) in title bar for all toplevels, 
        only button available in title bar is the close button.
        """
        sf.remove_titlebar(self.tplvl_advset)
        sf.remove_titlebar(self.tplvl_savefmt)
    
    def store_pil(self, pil:Image.Image, type_:_img) -> None:
        """
        Stores the PIL.Image.Image to access later.

        Parameters
        ----------
        pil (Image.Image)
            The image to store.
        type_ (_img)
            The type of image.
        """
        if type_ == 'image':
            self.image_pil = pil
        elif type_ == 'mark' or type_ == "text":
            self.mark_pil = pil
            
    def clear_tkentry_text(self, event:tk.Event|None=None) -> None:
        """
        Remove text in tkinter Entry.
        This function only work once each time app is executed.

        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        self.tktxt_entry.delete(0.0, tk.END)
        self.text_mark_maker()
        self.tktxt_entry.unbind("<Button-1>")
        self.tktxt_entry.bind("<KeyRelease>", self.text_mark_maker)
        
    def get_image_size(
        self, 
        pil: Image.Image, 
        type_: _img, 
        max_size: tuple[int, int]|None = None, 
        ) -> tuple[int, int]:
        """
        Some image (watermark and image to be watermarked) is scaled down on GUI, 
        because the image needs to fit within the app's canvas.
        This function calculate the appropriate image width and height to have padding on canvas.
        Image to be watermarked needs to be pass in first, 
        to get the ratio of the image before and after scaling, 
        this ratio will be used to scale other types of image.

        Parameters
        ----------
        pil (Image.Image)
            Image to get width and height.
        type_ (_img)
            Type of image.
        max_size (tuple[int,int]|None, optional. Defaults to None)
            Set maximum width an height of the image, 
            the image will scale up proportionally until the width and/or height reached max_size..
        
        Returns
        -------
        tuple[int, int]
            `(width, height)`
            Calculated image width and height.
        """
        rq_scale = 1
        if type_ == "text":
            width = np.round(pil.width / self.image_width_scale)
            height = np.round(pil.height / self.image_height_scale)
            size = (round(width), round(height))
            rq_scale = self.usrntr_scale.get()
        else:
            width, height = pil.width, pil.height
            if max_size:
                wid, hei = max_size
                w = wid / width
                h = hei / height
            elif type_ == 'image':
                w = (self.canvas.winfo_reqwidth() - CANVAS_PADX * 2) / width
                h = (self.canvas.winfo_reqheight() - CANVAS_PADY * 2) / height
            elif type_ == 'mark':
                w = 1 / self.image_width_scale
                h = 1 / self.image_height_scale
                rq_scale = self.usrntr_scale.get()
            ratio:float = min(w, h)
            size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
        rq_width = np.round(size[0] * rq_scale)
        rq_height = np.round(size[1] * rq_scale)
        return (round(rq_width), round(rq_height))
    
    def font_selected(self, event:tk.Event|None=None) -> None:
        """
        Set style to `regular` or `Regular` if exist, 
        remind user with messagebox when there are neither style.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
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
    
    def choose_color(self, target:_color) -> None:
        """
        Calls tkinter colorchooser to select and set color on specified location.

        Parameters
        ----------
        target (_color)
            Target to set color to.
        """
        color_code = colorchooser.askcolor(title ="Choose a color")
        if target == "text fg":
            if color_code[1] is not None:
                self.current_font_rgb, self.current_font_hexcolor = color_code
                self.lbl_watermark_preview.config(fg=self.current_font_hexcolor)
                self.text_mark_maker()
        elif target == "text bg":
            if color_code[0] is not None:
                self.mark_bg, _ = color_code
            else:
                self.mark_bg = GRAY_RGB
            self.text_mark_maker()
        elif target == "canvas bg":
            if color_code[1] is not None:
                _, self.canvas_bg = color_code
                self.update_canvas_bg()
    
    def remove_exist_watermark(self, method:_rm_mark) -> None:
        """
        Remove preview and/or watermark specified on canvas.
        
        Parameters
        ----------
        method (_rm_mark)
            The method watermark was created by.
        """
        try:
            if method == 'clicked':
                self.canvas.delete(self.canvas_mark)
                self.clicked = False
            elif method == 'motion':
                self.canvas.delete(self.canvas_mark_preview)
            elif method == "all":
                self.canvas.delete(self.canvas_mark_preview)
                self.canvas.delete(self.canvas_mark)
                self.clicked = False
        except AttributeError:
            print("making sure to remove unwanted watermarks")
        
        if self.ckbtnvr_grid.get() and method == 'clicked':
            for item in self.grid_watermark:
                self.canvas.delete(item)
            self.clicked = False
        elif self.ckbtnvr_grid.get() and method == 'motion':
            for item in self.grid_watermark_preview:
                self.canvas.delete(item)
        
    def show_hidden_widget(self) -> None:
        """Show/hide tkinter Checkbutton that enable/disable warning when watermark has background."""
        if self.ckbtnvr_show_mark_bg.get():
            self.ckbtnbrdr_wrng_mark_bg.grid(column=0, row=1, padx=(0, 15), columnspan=2, sticky="w")
        else:
            self.ckbtnbrdr_wrng_mark_bg.grid_forget()
        
    def reset_to_default_image(self) -> None:
        """Reset image and relevant attributes, variables to default."""
        self.apply_paths = []
        
        inidir_image = self.inidir_image
        
        # loads default image
        self.filepath_image = FPATH_DFT_IMG
        self.load_image() # resets initial directory
        
        self.inidir_image = inidir_image
        
        # remove canvas bind so watermark the default image isn't possible
        self.is_image = False
        self.update_canvas_bind() 
        self.text_image_count.set("") # reset here so default image doesn't count
        
    def length_valid(self) -> bool:
        """
        If the values user entered will cause width and/or height of watermark 
        to be less than 1, remind user with messagebox.
        
        Returns
        -------
        bool
            If user settings will result length > 1.
        """
        border_w = self.usrntr_border_w.get()
        border_h = self.usrntr_border_h.get()
        
        w = self.mark_bbox[2] - self.mark_bbox[0]
        h = self.mark_bbox[3] - self.mark_bbox[1]

        width = w + border_w
        height = h + border_h
        
        condition = []
        vaild = True
        if width <= 0:
            condition.append(f"watermark width > {-w}")
            vaild = False
            self.usrntr_border_w.set(-w)
        if height <= 0:
            condition.append(f"watermark height > {-h}")
            self.usrntr_border_h.set(-h)
            vaild = False
        if not vaild:
            messagebox.showwarning(
                title="Invaild adjust value.", 
                message=f"Watermark after adjustment have width and/or height < 1.\n In this case set: {' and '.join(condition)}."
            )
            self.tplvl_advset.deiconify()
        return vaild
    
    def adjust_value_validate(self) -> bool:
        """
        If the values user entered are not integer, remind user with messagebox
        and highlight the corresponding tkinter Spinbox with red foreground.
        Return True or False based on if all the values user entered are valid.
        
        Returns
        -------
        bool
            If all the values user entered are integer.
        """
        vals = [spnbx.get() for spnbx in self.spnbxs]
        map_result = list(map(self.spnbx_val_validate, vals))
        map_fail_idx = [idx for idx, val in enumerate(map_result) if val is False]
        
        # reset fg color
        for spnbx in self.spnbxs:
            spnbx.config(fg="black")
        
        if all(map_result) is True: # `True is True` for readability
            return True
        
        adjust_idx = ['a', 'b', 'c', 'd', 'e', 'f']
        invalid = [adjust_idx[idx] for idx in map_fail_idx]
        
        messagebox.showerror(
            title="Invalid Inputs!", 
            message=f"The input are invalid with adjust: " + ", ".join(invalid) + ".\nOnly accepts integers(positive and negative whole numbers and zero).", 
        )
        
        # set fg of widgets with invalid input to red
        widgets = [self.spnbxs[idx] for idx in map_fail_idx]
        for widget in widgets:
            widget.config(fg="red")
            
        self.tplvl_advset.deiconify()
        return False
    
    def spnbx_val_validate(self, value:str) -> bool:
        """
        Validator of tkinter Spinbox.
        Constrain value of tkinter Spinbox to be convertable to integer.

        Parameters
        ----------
        value (str)
            The value user entered to be validated.
        
        Returns
        -------
        bool
            If the entered value is valid.
        """
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
        
    def get_fname(self, idx:int|None=None) -> str:
        """
        Return file name and format selected by user. 
        File naming scheme has two mode `format` and `rename`,
        `format` retains original file name, with additional prefix or suffix, 
        `rename` discards original file name, new file name will be `UserEnterFileName-1.png, UserEnterFileName-2.png, ...etc`.
        
        Parameters
        ----------
        idx (int|None, optional. Defaults to None)
            Index number of image, will be used by `rename` naming scheme. 
        
        Returns
        -------
        str
            File name concat with file format.
        """
        if self.ckbtnvr_fname_fmt.get():
            prefix = self.fname_prefix.get()
            suffix = self.fname_suffix.get()
            og_fname = self.filepath_image.rsplit("/", maxsplit=1)[1] # fname without directory
            og_name = og_fname.rsplit(".", maxsplit=1)[0] # fname without file format
            fname = prefix + og_name + suffix
        else:
            name = self.fname_name.get()
            if idx:
                fname = name + " - " + str(idx)
            else:
                fname = name + "-1"
        fmt = self.cmbbx_filefmt.get()
        return fname + fmt
        
    def condition_met(self, from_:_msgbx) -> bool:
        """
        Conditions for all functions, gathered here for readability purposes, 
        return True if all requirement before function call is met, 
        False otherwise, also remind user with messagebox.

        Parameters
        ----------
        from_ (_msgbx)
            The source of function call, 
            the location to check if conditions met, 
            the identification of which condition to check.

        Returns
        -------
        bool
            If conditions met.
        """
        if from_ == "btnf_image_mode":
            if self.filepath_mark == "":
                self.btn_switch_text.config(relief='sunken')
                messagebox.showwarning(
                    title="Missing watermark image!", 
                    message="Click watermark button and select a image file first!"
                )
                return False
        elif from_ == "btnf_save":
            if self.filepath_image == FPATH_DFT_IMG:
                messagebox.askyesno(
                    title="Too early. Load a image first!", 
                    message="Load a image and place watermark on the image, then click the save button.", 
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
                    message="The background of watermark preview will also appear in the result image, still want to save the image?", 
                    )
                if not save:
                    return False
        elif from_ == "btnf_apply":
            if self.filepath_image == FPATH_DFT_IMG:
                messagebox.showwarning(
                    title="Too early. Load a image first!", 
                    message="Load a image and place watermark on the image, then click the apply button.", 
                )
                return False
            elif self.clicked == False:
                messagebox.showwarning(
                    title="Too early. Place watermark first!", 
                    message="Place watermark on the image, then click the apply button.", 
                )
                return False
            elif self.apply_paths == []:
                messagebox.showwarning(
                    title="Too early. Open and select a folder first!", 
                    message="Select a folder of image to apply watermark, then click the apply button.", 
                )
                return False
        elif from_ == "apply_to_folder":
            if self.save_dir.get() == "File save directory missing.":
                messagebox.showwarning(
                    title="Too early. Where to store the images?", 
                    message="Select a folder to save watermarked image, then click the execute button.", 
                )
                return False
        elif from_ == "btnf_preview":
            if self.is_image and self.is_mark:
                return True
            messagebox.showwarning(
                title="Too early. Load a image first!", 
                message="Load a image and place watermark on the image, then click the preview button.", 
            )
            return False
        elif from_ == "canvas_clicked" :
            try:
                # Spinbox with the current validation allow "" and value convertible to int
                # all accepted letters are: 0~9, +, -, and space(s), 
                # the rule found possible are:  
                # 1. space will be before and/or after all numbers and symbol(+/-)
                # 2. only one symbol can exist, and will exist before numbers
                # 3. 0 can exist before other numbers
                
                user_input = self.usrntr_rotate.get()
                txt = str(user_input).strip() # strip off spaces
                num = int(txt) # also remove unnecessary + sign and 0s before other numbers
                self.usrntr_rotate.set(num)
            except tk.TclError as error:
                user_input = str(error).split('"')[1] # get user input from error message
                if user_input == '':
                    messagebox.showwarning(
                        title="Invalid input!", 
                        message=f"Input value in rotate field are empty, value is set to 0.", 
                        )
                    self.usrntr_rotate.set(0)
                    return True
                val_set = messagebox.askokcancel(
                    title="Invalid input!", 
                    message=f"Input value in rotate field are invalid: '{user_input}', set value to '{int(user_input)}'?", 
                    )
                if val_set:
                    self.usrntr_rotate.set(int(user_input))
                    
                    # update text mark here, so watermark will show after user clicked yes on messagebox (val_set)
                    self.text_mark_maker()
                    return True
                return False
            if self.cmbbx_fontstyle.get() == "select a style":
                messagebox.showwarning(
                    title="Font style missing!", 
                    message="There is no default style(regular or Regular) in selected font, please select one.", 
                )
                return False
        return True

    def __prnt_style_without_regular_(self) -> None:
        """
        This function for testing purpose only, 
        will print out all fonts without style: `regular` or `Regular`, 
        in path: C:/Windows/Fonts.
        """
        font_dict = sf.get_sysfont_sorted()
        for name in font_dict:
            all_style = []
            for style in font_dict[name]:
                all_style.append(style)
            if len(all_style) > 1:
                if "Regular" not in all_style and "regular" not in all_style:
                    print(name, font_dict[name])

    def __get_rotated_size(self, width:int, height:int, angle:int) -> tuple[int, int]:
        """
        This is a reminder function, 
        to remind me of always read the document thoroughly, and don't skip lines, 
        and don't try reinvent the wheel (in this case, PIL.Image.Image.rotate(angle, `expand=True`)).
        
        Parameters
        ----------
        width (int)
            Width of the image.
        height (int)
            Height of the image.
        angle (int)       
            Angle the image is going to be rotated.
        
        Returns
        -------
        tuple[int, int]
            `(width, height)`
            The image size after rotation.
        """
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