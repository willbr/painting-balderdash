from tkinter import *
from tkinter.ttk import *

root = Tk()
root.geometry('800x600')
root.title('Painting Balderdash')

frame = Frame(root)
frame.pack(fill=BOTH, expand=YES, padx=0, pady=0)

hscrollbar = Scrollbar(frame, orient=HORIZONTAL)
hscrollbar.pack(side=BOTTOM, fill=X)

vscrollbar = Scrollbar(frame, orient=VERTICAL)
vscrollbar.pack(side=RIGHT, fill=Y)

canvas = Canvas(frame, bd=0, bg='#aaaaaa') #, xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
canvas.pack(side=LEFT, fill=BOTH, expand=YES)

hscrollbar.config(command=canvas.xview)
vscrollbar.config(command=canvas.yview)

def paint(event):
    size = 20
    step = size / 2
    x1, y1 = (event.x - step), (event.y - step)
    x2, y2 = (event.x + step), (event.y + step)

    x1, y1 = event.x, event.y
    x2, y2 = x1 + size, y1 + size

    #canvas.create_oval(event.x, event.y, event.x, event.y, fill='#000000',  width=0)
    canvas.create_oval(x1, y1, x2, y2, fill='#8B88EF',  width=0)

def paint(event):
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    size = min(canvas_width, canvas_height) * 0.05
    step = size / 2
    x1, y1 = (canvas.canvasx(event.x) - step), (canvas.canvasy(event.y) - step)
    x2, y2 = (canvas.canvasx(event.x) + step), (canvas.canvasy(event.y) + step)

    canvas.create_oval(event.x, event.y, event.x, event.y, fill='#000000',  width=0)
    canvas.create_oval(x1, y1, x2, y2, fill='#8B88EF',  width=0)


def on_canvas_resize(event):
    canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), canvas.winfo_height()))

canvas.bind('<Configure>', on_canvas_resize)

def on_canvas_resize(event):
    canvas.configure(scrollregion=canvas.bbox('all'))
    hscrollbar.set(0.0, 1.0)
    vscrollbar.set(0.0, 1.0)

canvas.bind('<Configure>', on_canvas_resize)

#canvas.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonPress-1>', paint)

root.wm_state('zoomed')
root.mainloop()
