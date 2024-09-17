import tkinter as tk
import numpy as np

from typing import Literal
from typing_extensions import TypeAlias
from collections.abc import Callable
from matplotlib import font_manager
from PIL import ImageFont

_callable: TypeAlias = Callable
_side: TypeAlias = Literal["tl", "tr", "bl", "br", "t", "b"] # topleft, bottomright etc.

class ToolTip():
    """
    add hover text to a widget in tkinter.
    a tooltip window with customizable text in tooltip window 
    and specify which side of the original widget to display on.
    this version isn't designed to be operating individually,
    please call this class by TipManager().
    
    cite: https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python/56749167#56749167
    """
    def __init__(self) -> None:
        "create the first tooltip window."
        self.createtip()
        
    def createtip(self) -> None:
        "create tooltip window and label."
        self.tip_window = tk.Toplevel()
        self.tip_window.config(borderwidth=1, background="black")
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.withdraw()
        self.label = tk.Label(self.tip_window, font='Arial 16', background="light yellow")
        self.label.pack()
        
    def configtip(self, widget:tk.Widget, text:str, side:_side) -> None:
        """
        configure widget on top of tooltip window.

        Args:
            widget (tk.Widget): the master of tooltip,
            text (str): text on tooltip window.
            side (_side): the side to show tooltip from the widget, 
                          use `tl`, `tr`, `bl`, `br`, `t`, `b`; 
                          `t` for top, `b` for bottom, `l` for left, `r` for right.
        """
        base_x, base_y = widget.winfo_rootx(), widget.winfo_rooty()
        self.label.config(text=text)
        if side == "br":
            x = base_x + widget.winfo_reqwidth()
            y = base_y + widget.winfo_reqheight()
        elif side == "bl":
            x = base_x - self.label.winfo_reqwidth()
            y = base_y + widget.winfo_reqheight()
        elif side == "tl":
            x = base_x - self.label.winfo_reqwidth()
            y = base_y - self.label.winfo_reqheight()
        elif side == "tr":
            x = base_x + widget.winfo_reqwidth()
            y = base_y - self.label.winfo_reqheight()
        elif side == "b":
            x = base_x
            y = base_y + widget.winfo_reqheight()
        elif side == "t":
            x = base_x
            y = base_y - self.label.winfo_reqheight()
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
    def showtip(self, widget:tk.Widget, text:str, side:_side) -> None:
        """
        controls show portion of tooltip window.

        Args:
            widget (tk.Widget): the master of tooltip,
            text (str): text on tooltip window.
            side (_side): the side to show tooltip from the widget, 
                          use `tl`, `tr`, `bl`, `br`, `t`, `b`; 
                          `t` for top, `b` for bottom, `l` for left, `r` for right.
        """
        if self.tip_window.winfo_exists():
            self.configtip(widget, text, side)
            self.tip_window.deiconify()
        else:
            self.createtip()
            self.configtip(widget, text, side)
    
    def hidetip(self) -> None:
        "controls hide portion of tooltip window."
        self.tip_window.withdraw()

class TipManager():
    """
    this is a support component for ToolTip(), 
    specific for large amount of tooltip in the same project,
    with additional functionality of enable and disable all the tooltip.
    
    Example:
     >>> import support_func as sf
     >>> tip = sf.TipManager()
     >>> tip.add_to_queue(widget_to_add_tooltip, 
     >>>     text="text to show when hover over widget", 
     >>> )
     >>> ...
     >>> tip.enable_all()
    
    """
    def __init__(self) -> None:
        self.widget_set = {}
        self.toolTip = ToolTip()
    
    def add_to_queue(self, widget:tk.Widget, *, text:str, side:_side="br"):
        """
        add widget to queue of tooltip, enable tooltips with `enable_all()`.

        Args:
            widget (tk.Widget): the master of tooltip,
            text (str): text on tooltip window.
            side (_side): the side to show tooltip from the widget, 
                          use `tl`, `tr`, `bl`, `br`, `t`, `b`; 
                          `t` for top, `b` for bottom, `l` for left, `r` for right.
                          Defaults to `br`, bottom right.
        """
        self.widget_set[widget.winfo_id()] = {
            "widget":  widget, 
            "text":  text, 
            "side":  side, 
            }
    
    def enable_all(self):
        "enable tooltip for every widgets in queue."
        for winfo_id in self.widget_set.keys():
            widget = self.widget_set[winfo_id]["widget"]
            widget.bind('<Enter>', self.__enter)
            widget.bind('<Leave>', self.__leave)
    
    def disable_all(self):
        "disable tooltip for every widgets in queue."
        for winfo_id in self.widget_set.keys():
            widget = self.widget_set[winfo_id]["widget"]
            widget.unbind('<Enter>')
            widget.unbind('<Leave>')
    
    def __enter(self, event):
        "show tooltip when mouse hover."
        winfo_id = event.widget.winfo_id()
        widget = self.widget_set[winfo_id]["widget"]
        text = self.widget_set[winfo_id]["text"]
        side = self.widget_set[winfo_id]["side"]
        self.toolTip.showtip(widget, text, side)
                
    def __leave(self, event):
        "hide tooltip when mouse left."
        self.toolTip.hidetip()

def get_sysfont_sorted() -> dict[str, dict[str, str]]:
    """
    get every font's name, filename, weight in path: C:/Windows/Fonts into a dict,
    change the names of some(commonly used) Chinese-supported(zh-TW) fonts to Chinese.
    
    #! this function assumes any font file only correspond with a unique style with the same font name.
    #! this function is not suitable for more then one correspond between style and file.
    
    C:/Windows/Fonts:
    ├──file_1.ttf    # font name:a, style: 1
    ├──file_2.ttf    # font name:a, style: 2
    ├──file_3.ttf    # font name:a, style: 3
    ├──file_4.ttf    # font name:a, style: 3
    ├──file_5.ttf    # font name:b, style: 1
    └──file_6.ttf    # font name:c, style: 2
    └──file_7.ttf    # font name:c, style: 3
    -> only file_3.ttf will be lost. 
    # * only return the last file of the the same font name and style got looped by this function.
    
    Returns:
        dict[str, dict[str, list[str]]]: {'font name': {'weight': ['...', ...], 'fname': 'file name', ...]}, ...}
    """
    sysfonts = font_manager.findSystemFonts()
    fonts_dict:dict[str, dict[str, str]] = {}

    # cite: https://en.wikipedia.org/wiki/List_of_typefaces_included_with_Microsoft_Windows
    fname_table = {
        'MingLiU': '新細明體',
        "DFKai-SB": '標楷體',
        'Microsoft JhengHei': '微軟正黑體',
        'Microsoft YaHei': '微軟雅黑體',
        'SimSun': '中易宋體',
    }

    # cite: https://stackoverflow.com/questions/75310650/how-to-get-font-path-from-font-name-python
    for filepath in sysfonts: 
        font = ImageFont.FreeTypeFont(filepath)
        try:
            name, style = font.getname()
            assert name and style
        except AssertionError:
            continue
        _, file_name = filepath.rsplit("\\", maxsplit=1)
        if name in fname_table:
            font_name = fname_table[name]
        else:
            font_name = name
        if font_name not in fonts_dict.keys():
            fonts_dict[font_name] = {}
        fonts_dict[font_name][style] = file_name
    return dict(fonts_dict.items())

class CustomScale(tk.Scale):
    """
    A tk.Scale that set scale indicator to the middle, 
    and can customize the value of ticks on both side 
    to have different tickinterval and limits.
    
    Arguments:
    
    cz_variable (tk.Variable): must be the same as the variable
    cmd (Callable): the function to be called after any interaction
    **kwargs: any supported by tk.Scale
    
    Example:
    
     >>> import support_func as sf 
     >>> tick = tk.IntVar()
     >>> c_scale = sf.CustomScale(
     >>>    ...
     >>>    variable=tick, 
     >>>    cz_variable=tick, 
     >>>    cmd=foo, 
     >>>    ...
     >>> )
    
    - get unformatted value:
     >>> var = c_scale.result
     >>> value = var.get()
    
    - set value:
     >>> tick.set(value=value)
    
    cite: https://stackoverflow.com/questions/56613120/python-3-ttk-spinbox-format-option
    """
    def __init__(self, master, cz_variable:tk.Variable, cmd:_callable, no_symbol:bool=False, **kwargs):
        kwargs['command'] = self.command
        super().__init__(master, **kwargs)
        
        self.result = tk.DoubleVar(value=1)
        self.repr_num = tk.IntVar()
        self.text = tk.StringVar()
        
        self.variable = cz_variable
        self.cmd = cmd
        self.no_symbol = no_symbol
        
        self.pixel = tk.PhotoImage(width=1, height=1)
        self.lbl = tk.Label(
            master, 
            textvariable=self.text, 
            image=self.pixel,
            compound="center", 
            width=105, 
            bg="white"
            )
        
    def command(self, event=None, *args) -> None:
        value = self.variable.get() / 100
        if value > 0:
            modify = 10
        else:
            modify = 1
        self.result.set(np.round(1 + modify * value, decimals=2))
        fmtd = f"{self.result.get():0.0%}"
        if self.no_symbol:
            fmtd = fmtd.rstrip("%")
        self.text.set(fmtd)
        self.repr_num.set(int(fmtd.rstrip("%")))
        self.cmd()

    def set(self, value:int|float) -> None:
        self.variable.set(value)
        self.command()
        

class CustomSpinbox(tk.Spinbox):
    """
    A tk.Spinbox that displays an additional '+' symbol before positive numbers.
    
    Arguments:
    
    cz_variable (tk.Variable): must be the same as the variable
    cmd (Callable): the function to be called after any interaction
    **kwargs: any supported by tk.Spinbox
    
    Example(just like regular tk.spinbox):
    
     >>> import support_func as sf 
     >>> var = tk.IntVar()
     >>> scale = sf.CustomSpinbox(
     >>>    ...
     >>>    textvariable=var, 
     >>>    cz_variable=var, 
     >>>    cmd=foo, 
     >>>    ...
     >>> )
     
    - get unformatted value:
     >>> value = var.get()
     
    - set value:
     >>> var.set(value=value)
    
    cite: https://stackoverflow.com/questions/56613120/python-3-ttk-spinbox-format-option
    """
    def __init__(self, master, cz_variable:tk.Variable, cmd:_callable, **kwargs):
        kwargs['command'] = self.command
        super().__init__(master, **kwargs)
        self.variable = cz_variable
        self.cmd = cmd
        self.command()
        
    def command(self, event=None, *args) -> None:
        try:
            value = self.variable.get()
        except tk.TclError as error: # in place to catch error caused by 08 and 09
            value = int(str(error).split('"')[1].lstrip("0"))
        self.value = value
        if value >= 0:
            s = "+"
        else:
            s = ""
        
        self.delete(0, tk.END)
        self.insert(0, f'{s}{value}')
        self.cmd()
        
    def set(self, value):
        self.variable.set(value)
        self.command()
    
    def get(self):
        return self.value
