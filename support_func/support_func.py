# standard library
import tkinter as tk

from collections.abc import Callable
from ctypes import windll, wintypes
from tkinter import Misc
from typing import Literal, TypeAlias

# related third party imports
import numpy as np

from matplotlib import font_manager
from PIL import ImageFont

# custom types
_callable: TypeAlias = Callable
_side: TypeAlias = Literal["tl", "tr", "bl", "br", "t", "b"] # topleft, bottomright etc.


class ToolTip():
    """
    Add tooltip to a widget in tkinter.
    A tooltip window with customizable text,
    configurable which side of the widget to display tooltip on.
    This version isn't designed to be operating individually,
    please call this class by class TipManager.
    
    cite: https://stackoverflow.com/a/56749167
    """
    def __init__(self) -> None:
        self.createtip()
        
    def createtip(self) -> None:
        "Create tooltip window and label."
        self.tip_window = tk.Toplevel()
        self.tip_window.config(borderwidth=1, background="black")
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.withdraw()
        self.label = tk.Label(self.tip_window, font='Arial 16', background="light yellow")
        self.label.pack()
        
    def configtip(self, widget:tk.Widget, text:str, side:_side) -> None:
        """
        Configure widget on top of tooltip window.

        Parameters
        ----------
        widget (tk.Widget)
            The master of tooltip, show tooltip when mouse hover this widget.
        text (str)
            Text on tooltip window.
        side (_side)
            The side to show tooltip from the widget, 
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
        Controls show portion of tooltip window.

        Parameters
        ----------
        widget (tk.Widget)
            The master of tooltip, show tooltip when mouse hover this widget.
        text (str)
            Text on tooltip window.
        side (_side)
            The side to show tooltip from the widget, 
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
        "Controls hide portion of tooltip window."
        self.tip_window.withdraw()

class TipManager():
    """
    This is a support component for class ToolTip, 
    specific for large amount of tooltip in the same project,
    with additional functionality of enable or disable all tooltip.
    
    Example
    -------
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
    
    def add_to_queue(self, widget:tk.Widget, *, text:str, side:_side="br") -> None:
        """
        Add widget to queue of tooltip, enable tooltips with `enable_all()`.

        Parameters
        ----------
        widget (tk.Widget)
            The master of tooltip, show tooltip when mouse hover this widget.
        text (str)
            Text on tooltip window.
        side (_side, optional. Defaults to "br")
            The side to show tooltip from the widget, 
            use `tl`, `tr`, `bl`, `br`, `t`, `b`; 
            `t` for top, `b` for bottom, `l` for left, `r` for right.
        """
        self.widget_set[widget.winfo_id()] = {
            "widget":  widget, 
            "text":  text, 
            "side":  side, 
            }
    
    def enable_all(self) -> None:
        "Enable tooltip for every widgets in queue."
        for winfo_id in self.widget_set.keys():
            widget = self.widget_set[winfo_id]["widget"]
            widget.bind('<Enter>', self.__enter)
            widget.bind('<Leave>', self.__leave)
    
    def disable_all(self) -> None:
        "Disable tooltip for every widgets in queue."
        for winfo_id in self.widget_set.keys():
            widget = self.widget_set[winfo_id]["widget"]
            widget.unbind('<Enter>')
            widget.unbind('<Leave>')
        self.toolTip.hidetip()
    
    def __enter(self, event:tk.Event) -> None:
        """
        Show tooltip.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        winfo_id = event.widget.winfo_id()
        widget = self.widget_set[winfo_id]["widget"]
        text = self.widget_set[winfo_id]["text"]
        side = self.widget_set[winfo_id]["side"]
        self.toolTip.showtip(widget, text, side)
                
    def __leave(self, event:tk.Event) -> None:
        """
        Hide tooltip.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        self.toolTip.hidetip()

def get_sysfont_sorted() -> dict[str, dict[str, str]]:
    """
    Get every font's name, filename, weight in path: C:/Windows/Fonts into a dict,
    change the names of some(commonly used) Chinese-supported(zh-TW) fonts to Chinese.
    
    Assumes
    -------
    This function assumes any font file only corresponds to a unique style with the same font name.
    
    Example
    -------
    C:/Windows/Fonts:
    ├──file_1.ttf    # font name: a, style: 1
    ├──file_2.ttf    # font name: a, style: 2
    ├──file_3.ttf    # font name: a, style: 3
    ├──file_4.ttf    # font name: a, style: 3
    ├──file_5.ttf    # font name: b, style: 1
    ├──file_6.ttf    # font name: c, style: 2
    └──file_7.ttf    # font name: c, style: 3
    
    Only return the last file, with the the same font name and style, 
    file_3.ttf and file_4.ttf have the same font name and style:
        -> file_3.ttf will be lost.
    
    Returns
    -------
    dict[str, dict[str, list[str]]]
        `{'font name': {'weight': ['...', ...], 'fname': 'file name', ...]}, ...}`
        All fonts on system in alphabetical order. 
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
    A custom version of tk.Scale that has different tickinterval and limits on both side, 
    and have customized format in value label, which is set to the middle of the scale.
    
    Change function originally intended for `command` in original tk.Scale
    to be pass into attributes: `command` and `cmd`.
    
    This customized version of tk.Scale assumes a function will be passed in.
    
    Tickinterval example
    --------------------
    10%, 11%, 12%, ..., 100%, ..., 980%, 990%, 1000%
    
    Attributes
    ----------
    master (Misc)
        The master of this widget.
    cz_variable (tk.Variable)
        Argument must be the same as the argument passed into parameter: variable.
    cmd (Callable)
        The function to be called after any interaction with this widget.
    no_symbol (bool. Defaults to False)
        If symbol is not needed.
    **kwargs
        Any supported by tk.Scale.
    
    Example
    -------
    >>> import support_func as sf 
    >>> tick = tk.IntVar()
    >>> c_scale = sf.CustomScale(
    >>>    ...
    >>>    variable=tick, 
    >>>    cz_variable=tick, 
    >>>    cmd=foo, 
    >>>    ...
    >>> )
    
    Get unformatted value
    ---------------------
    >>> var = c_scale.result
    >>> value = var.get()
    
    Set value
    ---------
    >>> tick.set(value=value)
    >>> c_scale.command() # update label to show formated value
    
    cite: https://stackoverflow.com/questions/56613120/python-3-ttk-spinbox-format-option
    """
    def __init__(self, master: Misc, *, cz_variable: tk.Variable, cmd: _callable, no_symbol: bool = False, **kwargs) -> None:
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
        
    def command(self, event:tk.Event|None=None) -> None:
        """
        Format the number to be displayed on the scale,
        then calls the function passed in by function: cmd.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
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
        
class CustomSpinbox(tk.Spinbox):
    """
    A custom version of tk.Spinbox that displays 
    an additional '+' symbol before positive numbers.
    
    This version is designed to be working with other function, 
    using individually may have unintended behavior.
    
    Change function originally intended for `command` in original tk.Scale
    to be pass into attributes: `command` and `cmd`.
    
    This customized version of tk.Scale assumes a function will be passed in.
    
    Attributes
    ----------
    master (Misc)
        The master of this widget.
    cz_variable (tk.IntVar)
        Argument must be the same as the argument passed into parameter: variable.
    cmd (Callable)
        The function to be called after any interaction with this widget.
    **kwargs
        Any supported by tk.Scale.
    
    Example
    -------
    >>> import support_func as sf 
    >>> var = tk.IntVar()
    >>> c_spinbox = sf.CustomSpinbox(
    >>>    ...
    >>>    textvariable=var, 
    >>>    cz_variable=var, 
    >>>    cmd=foo, 
    >>>    ...
    >>> )
     
    Get unformatted value
    ---------------------
    >>> value = var.get()
     
    Set value
    ---------
    >>> var.set(value=value)
    >>> c_spinbox.command() # update label to show formated value
    
    cite: https://stackoverflow.com/questions/56613120/python-3-ttk-spinbox-format-option
    """
    def __init__(self, master: Misc, *, cz_variable: tk.IntVar, cmd: _callable, **kwargs) -> None:
        kwargs['command'] = self.command
        super().__init__(master, **kwargs)
        self.variable = cz_variable
        self.cmd = cmd
        self.command()
        
    def command(self, event:tk.Event|None=None) -> None:
        """
        The customizable part, format the number displayed of the scale,
        then calls the command by function: cmd.
        
        Parameters
        ----------
        event (tk.Event|None, optional. Defaults to None)
            The tkinter event.
        """
        try:
            self.value = int(self.variable.get())
            if self.value >= 0:
                s = "+"
            else:
                s = ""
            
            self.delete(0, tk.END)
            self.insert(0, f'{s}{self.value}')
            self.cmd()
        except tk.TclError: 
            # expected error for invalid user input of non-integer
            return

def remove_titlebar(win:tk.Toplevel) -> None:
    """
    Remove all buttons in tk.Toplevel title bar in windows, 
    result in a tk.Toplevel with draggable empty title bar.
    
    * ``This function must be called after tk.Tk().update().``
    
    For more detail information, see: https://github.com/Sharl0tteIsTaken/no-title-bar-tkinter-toplevel

    Parameters
    ----------
    win (tk.Toplevel)
        The tk.Toplevel to remove title bar.
    """
    GWL_STYLE = -16
    WS_SYSMENU = 0x00080000

    SWP_FRAMECHANGED = 0x0020
    SWP_NOACTIVATE = 0x0010
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001

    GetWindowLong = windll.user32.GetWindowLongW
    GetWindowLong.restype = wintypes.ULONG
    GetWindowLong.argtypes = (wintypes.HWND, wintypes.INT)

    SetWindowLong = windll.user32.SetWindowLongW
    SetWindowLong.restype = wintypes.ULONG
    SetWindowLong.argtypes = (wintypes.HWND, wintypes.INT, wintypes.ULONG)

    SetWindowPos = windll.user32.SetWindowPos
        
    hwnd = windll.user32.GetParent(win.winfo_id())
    style = GetWindowLong(hwnd, GWL_STYLE)
    style = style & ~WS_SYSMENU
    SetWindowLong(hwnd, GWL_STYLE, style)
    SetWindowPos(hwnd, 0, 0,0,0,0, SWP_FRAMECHANGED | SWP_NOACTIVATE | SWP_NOMOVE | SWP_NOSIZE)
