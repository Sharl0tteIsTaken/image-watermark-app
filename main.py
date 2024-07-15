import tkinter as tk

from tkinter import filedialog
from PIL import ImageTk, Image

def clicked(event):
    print("clicked.")





window = tk.Tk()
window.title("💧MarkIt.")
window.minsize(width=800, height=500)

# this line *must* be after tk.Tk() is declared.
image = ImageTk.PhotoImage(file='grey_box.png')

panel = tk.Canvas(window, bg='white')
panel.pack()
panel.create_image(0, 0, image=image, anchor='nw')
panel.bind("<Button-1>", clicked)





window.mainloop()
