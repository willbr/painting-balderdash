from tkinter import *
from tkinter.ttk import *

background_colour = '#aaa'

brush_size = 20
bursh_color = '#8B88EF'

root = Tk()
root.geometry('800x600')
root.title('Painting Balderdash')

toolbox = Frame(root)
toolbox.pack(side=LEFT, fill=Y, padx=0, pady=0)

colours = [
    ['Black', '#333'],
    ['White', '#eee'],
    ['Red', '#e33'],
    ['Green', '#8BEF88'],
    ['Blue', '#88f'],
]

def set_colour(colour):
    def fn():
        global bursh_color
        bursh_color = colour
    return fn

for k, v in colours:
    btn = Button(toolbox, text=k, command=set_colour(v))
    btn.pack(side=TOP, padx=10, pady=10)

clear_button = Button(toolbox, text='Clear',)
clear_button.pack(side=BOTTOM, padx=10, pady=10)


frame = Frame(root)
frame.pack(fill=BOTH, expand=YES, padx=0, pady=0)

hscrollbar = Scrollbar(frame, orient=HORIZONTAL)
hscrollbar.pack(side=BOTTOM, fill=X)

vscrollbar = Scrollbar(frame, orient=VERTICAL)
vscrollbar.pack(side=RIGHT, fill=Y)

canvas = Canvas(frame, bd=0, bg=background_colour)
canvas.pack(side=LEFT, fill=BOTH, expand=YES)

hscrollbar.config(command=canvas.xview)
vscrollbar.config(command=canvas.yview)

def clear_canvas(event):
    canvas.delete('all')

clear_button.command = clear_canvas

def paint(event):

    step = brush_size / 2
    x1, y1 = (canvas.canvasx(event.x) - step), (canvas.canvasy(event.y) - step)
    x2, y2 = x1 + brush_size, y1 + brush_size

    canvas.create_oval(x1, y1, x2, y2, fill=bursh_color,  width=0)


def on_canvas_resize(event):
    bbox = canvas.bbox('all')
    if bbox is None:
        return

    margin = 0.25

    x1 = bbox[0] - bbox[2] * margin
    y1 = bbox[1] - bbox[3] * margin
    x2 = bbox[2] + bbox[2] * margin
    y2 = bbox[3] + bbox[3] * margin

    canvas.config(scrollregion=(x1, y1, x2, y2))

    canvas.config(
        xscrollcommand=hscrollbar.set,
        yscrollcommand=vscrollbar.set)


canvas.config(cursor='crosshair')

canvas.bind('<Configure>', on_canvas_resize)

canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonPress-1>', paint)
canvas.bind('<ButtonRelease-1>', on_canvas_resize)

root.wm_state('zoomed')
root.mainloop()
