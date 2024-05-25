from tkinter import *
from tkinter.ttk import *
from math import sqrt

background_colour = '#aaa'

zoom_level = 5
zoom_scales = [
    0.1,
    0.25,
    0.333,
    0.5,
    0.667,
    1,
    1.5,
    2,
    3,
    4,
    5,
    6,
    7,
]

line_points = None
line_id = None


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


zoom_label = Label(toolbox, text=f'100%')
zoom_label.pack(side=TOP, padx=10, pady=10)

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

brush_size = 20
brush_color = '#8B88EF'

def clear_canvas(event=None):
    global brush_cursor_id
    canvas.delete('all')
    brush_cursor_id = canvas.create_oval(0, 0, 0, 0, outline='grey', fill=brush_color, width=0)
    init_colour_pallete()
    canvas.focus_set()

    target_level = 5
    diff = target_level - zoom_level
    zoom(0, 0, diff)


def paint_first(event):
    global line_points
    global line_id
    #echo_event(event)

    if colour_pallete_visible:
        return

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    line_points = [x,y,x,y]

    canvas.itemconfig(brush_cursor_id, state='hidden')
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
    if line_points is None:
        return
    last_x, last_y = line_points[-2:]
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)

    if brush_size < 10:
        # makes large brushed laggy
        distance = sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
        if distance < brush_size // 2:
            return

    line_points.extend((x,y))
    #print(len(line_points))
    canvas.coords(line_id, line_points)


def paint_end(event):
    #echo_event(event)
    if line_points is None:
        return
    num_points = len(line_points)
    print(f'{num_points=}\n')
    canvas.itemconfig(brush_cursor_id, state='normal')
    canvas.tag_raise(brush_cursor_id)
    update_brush_cursor(event)
    on_canvas_resize(event)


def on_canvas_resize(event=None):
    #print('resize')
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
        zoom(x, y, 1)
    else:
        zoom(x, y, -1)

    update_brush_cursor(event)


def zoom(x, y, step):
    global zoom_level

    # if zoom_level > 9:
    #    return

    prev_level = zoom_level
    next_level = min(max(0, zoom_level + step), len(zoom_scales)-1)

    if prev_level == next_level:
        return


    prev_zoom_scale = zoom_scales[prev_level]
    next_zoom_scale = zoom_scales[next_level]
    #print(f'{prev_zoom_scale=}, {next_zoom_scale=}')

    zoom_step_scale = next_zoom_scale / prev_zoom_scale
    #print(f'{zoom_step_scale=}')

    zoom_level += step
    #print(f'{zoom_level=}')

    zoom_label.configure(text=f'{next_zoom_scale*100:4.2f}%')

    #canvas.scale('all', x,y, zoom_step_scale, zoom_step_scale)
    canvas.scale('!colours', x,y, zoom_step_scale, zoom_step_scale)

    all_items = canvas.find_all()

    for item_id in all_items:
        if canvas.type(item_id) == 'line':
            current_width = float(canvas.itemcget(item_id, 'width'))
            new_width = current_width * zoom_step_scale
            canvas.itemconfig(item_id, width=new_width)


def echo_event(event):
    print(event)
    return "break"

def update_brush_cursor(event):
    #print(event)
    r = brush_size / 2
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    x0, y0 = x - r, y - r
    x1, y1 = x + r, y + r
    #canvas.itemconfig(brush_cursor_id, state='normal')
    canvas.coords(brush_cursor_id, x0, y0, x1, y1)

#canvas.config(cursor='crosshair')
canvas.config(cursor='none')

canvas.bind('<Configure>', on_canvas_resize)

canvas.bind('<ButtonPress-1>', paint_first)
canvas.bind('<B1-Motion>', paint)
canvas.bind('<Motion>', update_brush_cursor)
canvas.bind('<ButtonRelease-1>', paint_end)

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


initial_brush_size = 0
brush_size_last_x = 0
brush_size_last_y = 0


def on_alt_b3_press(event):
    global brush_size_last_x
    global brush_size_last_y
    global initial_brush_size 

    brush_size_last_x = event.x
    brush_size_last_y = event.y

    initial_brush_size = brush_size


def on_alt_b3_motion(event):
    global brush_size
    delta_x = (event.x - brush_size_last_x) / 4
    #print(delta_x)

    brush_size = int(min(max(10, initial_brush_size + delta_x), 500))
    brush_size += brush_size % 2 # bugfix; removes shimmering artifacts
    #print(brush_size)

    event.x = brush_size_last_x
    event.y = brush_size_last_y

    update_brush_cursor(event)


def on_alt_b3_release(event):
    print(f'{brush_size=}')
    canvas.event_generate(
            '<Motion>',
            warp=True,
            x=brush_size_last_x,
            y=brush_size_last_y)


canvas.bind('<Alt-ButtonPress-3>', on_alt_b3_press, add='+')
canvas.bind('<Alt-B3-Motion>', on_alt_b3_motion, add='+')
canvas.bind('<Alt-B3-ButtonRelease>', on_alt_b3_release, add='+')

root.bind('<Alt_L>', lambda x: "break") # ignore key press


colour_pallete_visible = False
colour_pallete_pos = (0, 0)


def init_colour_pallete():
    global colour_pallete_visible
    global colour_pallete_pos

    colour_pallete_visible = False
    colour_pallete_pos = (0, 0)

    width  = 100
    height = 100
    step_x = width // 2
    step_y = height // 2
    x = -((len(colours) * width) // 2) + step_x
    y = (height // 2) - step_y
    for name, colour in colours:
        canvas.create_rectangle(x - step_x, y - step_y, x+step_x, y+step_y, fill=colour, tags='colours', state='hidden')
        x += width



def update_colour_pallete(cursor_x, cursor_y):
    global colour_pallete_pos
    old_x, old_y = colour_pallete_pos
    diff_x = cursor_x - old_x
    diff_y = cursor_y - old_y

    print(f'{(old_x, old_y)=}')
    print(f'{(cursor_x, cursor_y)=}')
    print(f'{(diff_x, diff_y)=}\n')

    colour_ids = canvas.find_withtag("colours")
    for colour_id in colour_ids:
        canvas.move(colour_id, diff_x, diff_y)
        canvas.tag_raise(colour_id)

    colour_pallete_pos = (cursor_x, cursor_y)


def show_colour_pallete(event):
    global colour_pallete_visible
    if colour_pallete_visible:
        #print('skip show')
        return
    canvas.itemconfigure('colours', state='normal')
    canvas.config(cursor='crosshair')
    colour_pallete_visible = True

    #print(f'{(event.x, event.y)=}')
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    update_colour_pallete(x, y)


def hide_colour_pallete(event):
    global colour_pallete_visible
    global brush_color

    #colour_ids = canvas.find_withtag("current && colours")
    colour_ids = canvas.find_withtag("current")
    if colour_ids:
        #print(colour_ids)
        #assert len(colour_ids) == 1
        colour_id = colour_ids[0]
        #print(colour_id)

        new_colour = canvas.itemcget(colour_id, 'fill')
        #print(new_colour)

        brush_color = new_colour
        canvas.itemconfig(brush_cursor_id, fill=new_colour)
    else:
        print('no ids')


    canvas.itemconfigure('colours', state='hidden')
    canvas.config(cursor='none')
    colour_pallete_visible = False


clear_canvas()


root.bind('<KeyPress-f>', show_colour_pallete)
root.bind('<KeyRelease-f>', hide_colour_pallete)

root.bind('<KeyPress-Escape>', clear_canvas)

canvas.bind('<MouseWheel>', on_windows_zoom)

root.wm_state('zoomed')
root.mainloop()

