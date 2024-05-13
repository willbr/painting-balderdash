from tkinter import *
from tkinter.ttk import *
from math import sqrt

background_colour = '#aaa'

zoom_level = 1
line_points = None
line_id = None

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
    global line_points
    global line_id
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    line_points = [x,y,x,y]

    line_id = canvas.create_line(
            x, y,
            x, y,
            fill=brush_color,
            width=brush_size,
            joinstyle='round',
            capstyle=ROUND,
            smooth=False, # it's too slow, once you have lots of things on screen
                          # maybe try disabling it while scrolling?
            )
    paint(event)


def paint(event):
    last_x, last_y = line_points[-2:]
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)

    distance = sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
    if distance < brush_size // 2:
        return

    line_points.extend((x,y))
    #print(len(line_points))
    canvas.coords(line_id, line_points)


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
    global zoom_level

    if zoom_level > 10:
        return

    zoom_level *= zoom_in_scale
    #print(zoom_level)

    canvas.scale('all', x,y, zoom_in_scale, zoom_in_scale)

    all_items = canvas.find_all()
    for item_id in all_items:
        if canvas.type(item_id) == 'line':
            current_width = float(canvas.itemcget(item_id, 'width'))
            new_width = current_width * zoom_in_scale
            canvas.itemconfig(item_id, width=new_width)


def zoom_out(x, y):
    global zoom_level

    if zoom_level < 0.10:
        return

    zoom_level *= zoom_out_scale
    #print(zoom_level)

    canvas.scale('all', x,y, zoom_out_scale, zoom_out_scale)
    all_items = canvas.find_all()
    for item_id in all_items:
        if canvas.type(item_id) == 'line':
            current_width = float(canvas.itemcget(item_id, 'width'))
            new_width = current_width * zoom_out_scale
            canvas.itemconfig(item_id, width=new_width)

def echo_event(event):
    print(event)

canvas.config(cursor='crosshair')

canvas.bind('<Configure>', on_canvas_resize)

canvas.bind('<ButtonPress-1>', paint_first)
canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonRelease-1>', on_canvas_resize)

#canvas.bind('<ButtonPress-2>', echo_event)
#canvas.bind('<B2-Motion>', echo_event)
#canvas.bind('<ButtonRelease-2>', echo_event)

def on_b3_press(event):
    x, y = event.x, event.y
    canvas.scan_mark(x, y)

def on_b3_motion(event):
    x, y = event.x, event.y
    canvas.scan_dragto(x, y, gain=1)

canvas.bind('<ButtonPress-3>', on_b3_press)
canvas.bind('<B3-Motion>', on_b3_motion)

canvas.bind('<MouseWheel>', on_windows_zoom)
root.wm_state('zoomed')
root.mainloop()

