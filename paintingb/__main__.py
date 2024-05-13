from tkinter import *
from tkinter.ttk import *
from time import time
from math import sqrt

background_colour = '#aaa'

last_x = None
last_y = None
last_time = None

brush_size = 20
brush_color = '#8B88EF'

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

speed_map = [max(10, int(x // 8)) for x in range(256)][::-1]

def set_colour(colour):
    def fn():
        global brush_color
        brush_color = colour
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


def paint_first(event):
    global last_time
    global last_x
    global last_y
    global brush_size
    last_time = time() - 0.000001
    last_x = canvas.canvasx(event.x)
    last_y = canvas.canvasy(event.y)
    brush_size = 10
    paint(event)


def paint(event):
    global last_time
    global last_x
    global last_y
    global brush_size

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    print((x, y, last_x, last_y))

    this_time = time()

    if last_time is None:
        last_time = this_time
        last_x = x
        last_y = y

    time_diff = this_time - last_time
    distance = sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
    if time_diff == 0:
        return
    else:
        speed = distance / time_diff
        speed = min(4000, max(100, speed))


    b = int((speed / 4000) * 255)
    speed_color = f'#0000{b:02x}'

    next_brush_size = speed_map[b]
    brush_size = (brush_size + next_brush_size) // 2

    #print((f'{x:3.0f},{y:3.0f} {distance:-2.2f}, {speed:-7.2f}, {brush_size} {b:-3d}'))

    canvas.create_line(
            last_x, last_y,
            x, y,
            fill=brush_color,
            #fill=speed_color,
            width=brush_size,
            joinstyle='round',
            capstyle=ROUND,
            smooth=True,
            )

    last_time = this_time
    last_x = x
    last_y = y


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

canvas.bind('<ButtonPress-1>', paint_first)
canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonRelease-1>', on_canvas_resize)

canvas.bind('<MouseWheel>', on_windows_zoom)
#root.wm_state('zoomed')
root.mainloop()

