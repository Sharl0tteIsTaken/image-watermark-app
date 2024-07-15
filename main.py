import tkinter as tk

from tkinter import filedialog
from PIL import ImageTk, Image

def clicked_block(event):
    x, y = event.x, event.y
    print(f"clicked at: x:{x}, y:{y} in block.")
    position_judgement(x, y)

def clicked_canvas(event):
    x, y = event.x, event.y
    print(f"clicked at: x:{x}, y:{y} in canvas.")
    position_judgement(x, y)

def position_judgement(x:int, y:int):
    if x <= 10 and y <= 10:
        print('top left corner')
    elif x >= (image.width() - 20) and y <= 10:
        print('top right corner')
    elif x <= 10 and y >= (image.height() - 20):
        print("btm left corner")
    elif x > (image.width() - 20) and y >= (image.height() - 20):
        print("btm right corner")


window = tk.Tk()
window.title("💧MarkIt.")
window.minsize(width=800, height=500)

block1 = tk.LabelFrame(window, bg="brown")
block1.config(padx=10, pady=10)
block1.pack()

# attempt 1.

# this line *must* be after tk.Tk() is declared.
# image = ImageTk.PhotoImage(file='grey_box.png')

# print(f"x={image.width()}, y={image.height()}")

# canvas = tk.Canvas(block1, bg='white')
# canvas.pack()
# canvas.create_image(0, 0, image=image, anchor='nw')
# block1.bind("<Button-1>", clicked_block)
# canvas.bind("<Button-1>", clicked_canvas)

# attempt 2.
# create canvas after getting the image's size is better.

image_pil=Image.open('grey_box.png')

print(image_pil.width, image_pil.height) # use this dimension to resize with in canvas

image_resize=image_pil.resize((800, 600))
image=ImageTk.PhotoImage(image_resize)

print(f"x={image.width()}, y={image.height()}")

canvas = tk.Canvas(block1, bg='white', width=800, height=600)
canvas.pack()
canvas.create_image(0, 0, image=image, anchor='nw')
block1.bind("<Button-1>", clicked_block)
canvas.bind("<Button-1>", clicked_canvas)

window.mainloop()
