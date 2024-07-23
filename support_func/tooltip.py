import tkinter as tk

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
        self.tip_window.overrideredirect(True)
        self.tip_window.geometry(f"+{x}+{y}")
        tk.Label(self.tip_window, text=self.text, background="light yellow").pack()

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
