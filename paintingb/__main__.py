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

def paint(event):
    size = 20
    step = size / 2
    x1, y1 = (event.x - step), (event.y - step)
    x2, y2 = (event.x + step), (event.y + step)
    canvas.create_oval(x1, y1, x2, y2, fill='#8B88EF',  width=0)

canvas.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonPress-1>', paint)

root.wm_state('zoomed')
root.mainloop()
