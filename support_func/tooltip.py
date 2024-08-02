import tkinter as tk
import tkinter.ttk as ttk

from matplotlib import font_manager
from PIL import ImageFont

class ToolTip(object):
    """
    cite: https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python/56749167#56749167
    """
    def __init__(self, widget:tk.Widget):
        self.widget:tk.Widget = widget
        self.tip_window:tk.Toplevel|None = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text:str):
        "Display text in tooltip window"
        self.text:str = text
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 60
        y = self.widget.winfo_rooty() + 45
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.config(borderwidth=1, background="black")
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip_window, text=self.text, background="light yellow").pack(side='left')

    def hidetip(self):
        exist_window = self.tip_window
        self.tip_window = None
        if exist_window:
            exist_window.destroy()

def add_tool_tip(widget:tk.Widget, text:str):
    """
    add hover text to a widget in tkinter.

    Args:
        widget (tkinter.Widget): any widget in tkinter.
        text (_type_): text displayed when mouse hovers.
    """
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

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

class FormattedSpinbox(ttk.Spinbox):
    """
    A ttk.Spinbox that displays a number followed by a specify symbol.
    
    cite: https://stackoverflow.com/questions/56613120/python-3-ttk-spinbox-format-option
    """
    def __init__(self, master, symbol:str, **kwargs):
        kwargs['command'] = self.command
        super().__init__(master, **kwargs)
        self.symbol = symbol
        
    def set(self, value):
        super().set(value)
        self.command()
        
    def get(self):
        return int(super().get().strip().split()[0])
    
    def command(self):
        value = self.get()
        self.delete(0, tk.END)
        self.insert(0, f"{value} {self.symbol}")