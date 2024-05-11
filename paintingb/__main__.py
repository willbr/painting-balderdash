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

#canvas.config(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
#canvas.config(scrollregion=(-4000, -4000, 4000, 4000))

hscrollbar.config(command=canvas.xview)
vscrollbar.config(command=canvas.yview)

def clear_canvas():
    canvas.delete('all')

clear_button.config(command=clear_canvas)

def paint(event):
    step = brush_size / 2
    x1, y1 = (canvas.canvasx(event.x) - step), (canvas.canvasy(event.y) - step)
    x2, y2 = x1 + brush_size, y1 + brush_size

    canvas.create_oval(x1, y1, x2, y2, fill=bursh_color,  width=0)


def on_canvas_resize(event=None):
    bbox = canvas.bbox('all')
    window_width, window_height = canvas.winfo_width(), canvas.winfo_height()

    if bbox is None:
        x1 = -window_width
        y1 = -window_height
        x2 = window_width * 2
        y2 = window_height * 2
    else:
        #print(bbox)
        x1 = bbox[0] - bbox[2] - window_width
        y1 = bbox[1] - bbox[3] - window_height
        x2 = bbox[2] + bbox[2] + window_width
        y2 = bbox[3] + bbox[3] + window_width

    scroll_region = canvas.cget("scrollregion")
    if scroll_region == '':
        #print('not set')
        pass
    else:
        old_x1, old_y1, old_x2, old_y2 = (float(n) for n in scroll_region.split(' '))
        #print(('old', old_x1, old_y1, old_x2, old_y2))
        x1 = min(x1, old_x1)
        y1 = min(y1, old_y1)
        x2 = max(x2, old_x2)
        y2 = max(y2, old_y2)

    #print(('new', x1, y1, x2, y2))

    canvas.config(scrollregion=(x1, y1, x2, y2))

    canvas.config(
        xscrollcommand=hscrollbar.set,
        yscrollcommand=vscrollbar.set)

def on_windows_zoom(event):
    ctrl_is_down = event.state == 4
    if ctrl_is_down == False:
        return
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    if event.delta > 0:
        zoom_in(x, y)
    else:
        zoom_out(x, y)

zoom_in_scale  = 1.2
zoom_out_scale = 0.8

def zoom_in(x, y):
    canvas.scale('all', x,y, zoom_in_scale, zoom_in_scale)

def zoom_out(x, y):
    canvas.scale('all', x,y, zoom_out_scale, zoom_out_scale)

canvas.config(cursor='crosshair')

canvas.bind('<Configure>', on_canvas_resize)

canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonPress-1>', paint)
canvas.bind('<ButtonRelease-1>', on_canvas_resize)

canvas.bind('<MouseWheel>', on_windows_zoom)
root.wm_state('zoomed')
root.mainloop()

