import tkinter as tk
import math

from tkinter import filedialog
from PIL import ImageTk, Image

# key dimensions
canvas_width = 800
canvas_height = 600


def clicked_block(event):
    x, y = event.x, event.y
    print(f"\nclicked at: x:{x}, y:{y} in block.")
    position_judgement(x, y)

def clicked_canvas(event):
    x, y = event.x, event.y
    print(f"\nclicked at: x:{x}, y:{y} in canvas.")
    position_judgement(x, y)

def hover_block(event):
    x, y = event.x, event.y
    msg = f"hover over: x:{x}, y:{y} in block."
    print(msg, end='')
    print('\b' * len(msg), end='', flush=True)
    
def hover_canvas(event):
    x, y = event.x, event.y
    msg = f"hover over: x:{x}, y:{y} in canvas."
    print(msg, end='')
    print('\b' * len(msg), end='', flush=True)

def position_judgement(x:int, y:int):
    if x <= 10 and y <= 10:
        print('top left corner')
    elif x >= (image.width() - 20) and y <= 10:
        print('top right corner')
    elif x <= 10 and y >= (image.height() - 20):
        print("btm left corner")
    elif x > (image.width() - 20) and y >= (image.height() - 20):
        print("btm right corner")

def resize_image(width:int, height:int):
    ratio:float = 1
    if width > canvas_width or height > canvas_height:
        ratio =  min(canvas_width / width, canvas_height / height)
    size:tuple[int, int] = math.floor(width * ratio * 0.99), math.floor(height * ratio * 0.99)
    # size:tuple[int, int] = math.floor(width * ratio), math.floor(height * ratio)
    return size
    
window = tk.Tk()
window.title("💧MarkIt.")
window.minsize(width=1000, height=700)

block_image = tk.LabelFrame(window, bg="brown")
block_image.config(padx=10, pady=10)
block_image.pack()

image_pil = Image.open('grey_box.png')
image_resize = image_pil.resize(resize_image(image_pil.width, image_pil.height))
image = ImageTk.PhotoImage(image_resize)

canvas = tk.Canvas(block_image, bg='white', width=canvas_width, height=canvas_height)
canvas.create_image(canvas_width / 2, canvas_height / 2, image=image, anchor='center')
canvas.pack()

block_image.bind("<Button-1>", clicked_block)
canvas.bind("<Button-1>", clicked_canvas)

block_image.bind("<Motion>", hover_block)
canvas.bind("<Motion>", hover_canvas)


window.mainloop()
