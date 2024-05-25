from tkinter import *
from tkinter.ttk import *
from math import sqrt

background_colour = '#aaa'

zoom_level = 5
zoom_scales = [
    0.1, 0.25, 0.333, 0.5, 0.667,
    1,
    1.5, 2, 3, 4, 5, 6, 7, 8,
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


brush_label = Label(toolbox, text=f'N')
brush_label.pack(side=TOP, padx=10, pady=10)

zoom_label = Label(toolbox, text=f' 100.00%')
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

brush_size = None
brush_size_on_canvas = None
brush_color = '#8B88EF'

current_tool = None

undo_stack = []
redo_stack = []

brush_cursor_id = canvas.create_oval(0, 0, 0, 0, outline='grey', fill=brush_color, width=0)

def set_brush_size(new_size):
    global brush_size
    global brush_size_on_canvas
    brush_size = int(min(max(2, new_size), 200))
    brush_label.configure(text=f'{brush_size:3d}')
    brush_size_on_canvas = int(max(2, brush_size * zoom_scales[zoom_level]))
    brush_size_on_canvas -= brush_size_on_canvas % 2 # bugfix; removes shimmering artifacts
    #print(f'{brush_size_on_canvas=}')


def get_visible_ids():
    ignore_list = list(canvas.find_withtag('colours'))
    ignore_list.append(brush_cursor_id)
    #visible_ids = set(canvas.find_all()) - set(ignore_list)
    all_items = canvas.find_all()
    visible_ids = {item for item in all_items if canvas.itemcget(item, 'state') != 'hidden'} - set(ignore_list)
    return visible_ids


def clear_canvas(event=None):
    visible_ids = get_visible_ids()
    #print(visible_ids)
    for object_id in visible_ids:
        canvas.itemconfig(object_id, state='hidden')

    undo_stack.append(('clear', visible_ids))

    init_colour_pallete()
    canvas.focus_set()

    target_level = 5
    diff = target_level - zoom_level

    zoom(0, 0, diff)

    set_brush_size(14)


def paint_start(event):
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
            width=brush_size_on_canvas,
            joinstyle='round',
            capstyle=ROUND,
            smooth=False, # it's too slow, once you have lots of things on screen
                          # maybe try disabling it while scrolling?
            )
    paint_motion(event)


def paint_motion(event):
    if line_points is None:
        return
    last_x, last_y = line_points[-2:]
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)

    if brush_size_on_canvas < 10:
        # makes large brushed laggy
        distance = sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
        if distance < brush_size_on_canvas // 2:
            return

    line_points.extend((x,y))
    #print(len(line_points))
    canvas.coords(line_id, line_points)


def paint_end(event):
    #echo_event(event)
    if line_points is None:
        return
    num_points = len(line_points)
    #print(f'{num_points=}\n')
    canvas.itemconfig(brush_cursor_id, state='normal')
    canvas.tag_raise(brush_cursor_id)
    update_brush_cursor(event)
    on_canvas_resize(event)

    undo_stack.append(('line', (line_id,)))
    redo_stack.clear()


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

    set_brush_size(brush_size)


def echo_event(event):
    print(event)
    return "break"

def update_brush_cursor(event):
    #print(event)
    r = brush_size_on_canvas / 2
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    x0, y0 = x - r, y - r
    x1, y1 = x + r, y + r
    #canvas.itemconfig(brush_cursor_id, state='normal')
    canvas.coords(brush_cursor_id, x0, y0, x1, y1)


def motion(event):
    update_brush_cursor(event)

    #print(f'{current_tool=}')
    tool_spec = tools.get(current_tool, None)
    if tool_spec is None:
        return

    tool_fn = tools[current_tool].get('motion', None)
    if tool_fn is None:
        return

    tool_fn(event)


#canvas.config(cursor='crosshair')
canvas.config(cursor='none')

canvas.bind('<Configure>', on_canvas_resize)

canvas.bind('<Motion>', motion)

#canvas.bind('<ButtonPress-2>', echo_event)
#canvas.bind('<B2-Motion>', echo_event)
#canvas.bind('<ButtonRelease-2>', echo_event)

def start_panning(event):
    x, y = event.x, event.y
    canvas.scan_mark(x, y)

def motion_panning(event):
    x, y = event.x, event.y
    canvas.scan_dragto(x, y, gain=1)

canvas.bind('<ButtonPress-3>', start_panning)
canvas.bind('<B3-Motion>', motion_panning)


initial_brush_size = 0
brush_size_last_x = 0
brush_size_last_y = 0

def save_cursor_position(event):
    global brush_size_last_x
    global brush_size_last_y
    brush_size_last_x = event.x
    brush_size_last_y = event.y


def restore_cursor_position(event):
    print('warping cursor')
    canvas.event_generate(
            '<Motion>',
            warp=True,
            x=brush_size_last_x,
            y=brush_size_last_y)


def on_alt_b3_press(event):
    global initial_brush_size 
    initial_brush_size = brush_size

    save_cursor_position(event)


def on_alt_b3_motion(event):
    delta_x = (event.x - brush_size_last_x) / 4
    #delta_y = (event.y - brush_size_last_y) / 4

    set_brush_size(initial_brush_size + delta_x)

    event.x = brush_size_last_x
    event.y = brush_size_last_y

    update_brush_cursor(event)
    return 'break'



def on_alt_b3_release(event):
    print(f'{brush_size=}')
    restore_cursor_position(event)


#canvas.bind('<Alt-ButtonPress-3>', on_alt_b3_press, add='+')
#canvas.bind('<Alt-B3-Motion>', on_alt_b3_motion, add='+')
#canvas.bind('<Alt-B3-ButtonRelease>', on_alt_b3_release, add='+')

root.bind('<Alt_L>', lambda x: "break") # ignore key press


colour_pallete_visible = False
colour_pallete_pos = (0, 0)


def init_colour_pallete():
    global colour_pallete_visible
    global colour_pallete_pos

    colour_pallete_visible = False
    colour_pallete_pos = (0, 0)

    width  = 60
    height = 60
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

    #print(f'{(old_x, old_y)=}')
    #print(f'{(cursor_x, cursor_y)=}')
    #print(f'{(diff_x, diff_y)=}\n')

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


initial_zoom = 0

def start_zooming(event):
    global initial_zoom
    initial_zoom = zoom_level
    #print(f'{initial_zoom=}')
    pass


def motion_zooming(event):
    delta_x = (event.x - brush_size_last_x) // 4
    #print(f'{delta_x=}')

    delta_steps = delta_x // 20
    #print(f'{delta_steps=}')

    target_level = initial_zoom + delta_steps
    #print(f'{target_level=} = {initial_zoom=} + {delta_steps=}')

    x = canvas.canvasx(brush_size_last_x)
    y = canvas.canvasy(brush_size_last_y)


    if target_level > zoom_level:
        zoom(x, y, +1)
    elif target_level == zoom_level:
        pass
    else:
        zoom(x, y, -1)
        pass

    return 'break'


def start_tool(tool_name):
    def fn(event):
        global current_tool
        #print(f'start_tool {tool_name=} {current_tool=}')
        # TODO end old tool, then start
        if tool_name == current_tool:
            return
        current_tool = tool_name
        tool_fn = tools[tool_name]['start']
        tool_fn(event)
        save_cursor_position(event)
    return fn


def end_tool(tool_name, warp_back):
    def fn(event):
        global current_tool
        #print(f'end_tool {tool_name=}')
        if tool_name != current_tool:
            raise ValueError(f'end tool: {tool_name=} != {current_tool=}')

        current_tool = None

        tool_fn = tools[tool_name].get('end', None)
        if tool_fn is None:
            print(f'no end fn for: {tool_name}')
            return

        tool_fn(event)

        if warp_back:
            restore_cursor_position(event)

    return fn


def start_undoing(event):
    if not undo_stack:
        print('nothing to undo')
        return

    #print(undo_stack)
    action = undo_stack.pop()
    print(action)
    action_type, object_ids = action
    ##print(f'deleting{object_id=}')
    #canvas.delete(object_id)
    match action_type:
        case 'clear':
            new_state ='normal'
        case _:
            new_state = 'hidden'

    for object_id in object_ids:
        canvas.itemconfig(object_id, state=new_state)

    redo_stack.append(action)



def start_redoing(event):
    if not redo_stack:
        print('nothing to redo')
        return

    #print(redo_stack)
    action = redo_stack.pop()
    print(action)
    action_type, object_ids = action
    ##print(f'deleting{object_id=}')

    match action_type:
        case 'clear':
            new_state ='hidden'
        case _:
            new_state = 'normal'

    for object_id in object_ids:
        canvas.itemconfig(object_id, state=new_state)

    undo_stack.append(action)



tools = {
    'brush': {
        'start':  paint_start,
        'motion': paint_motion,
        'end':    paint_end,
    },
    'color_pallete': {
        'start':  show_colour_pallete,
        'end':    hide_colour_pallete,
    },
    'tool_pallete': {
        'start':  show_colour_pallete,
        'end':    hide_colour_pallete,
    },
    'brush_size': {
        'start':  on_alt_b3_press,
        'motion': on_alt_b3_motion,
        'end':    on_alt_b3_release,
    },
    'pan': {
        'start':  start_panning,
        'motion': motion_panning,
    },
    'zoom': {
        'start':  start_zooming,
        'motion': motion_zooming,
    },
}

clear_canvas()

def zoom_to_level(target_level):
    def fn(event):
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        delta = target_level - zoom_level
        zoom(x, y, delta)
        return
    return fn


root.bind('<ButtonPress-1>', start_tool('brush'))
root.bind('<ButtonRelease-1>', end_tool('brush', warp_back=False))

root.bind('<KeyPress-f>', start_tool('color_pallete'))
root.bind('<KeyRelease-f>', end_tool('color_pallete', warp_back=True))

root.bind('<KeyPress-d>', start_tool('tool_pallete'))
root.bind('<KeyRelease-d>', end_tool('tool_pallete', warp_back=True))

root.bind('<KeyPress-s>', start_tool('brush_size'))
root.bind('<KeyRelease-s>', end_tool('brush_size', warp_back=True))

root.bind('<KeyPress-v>', start_tool('zoom'))
root.bind('<KeyRelease-v>', end_tool('zoom', warp_back=True))

root.bind('<KeyPress-1>', zoom_to_level(3))
root.bind('<KeyPress-2>', zoom_to_level(5))
root.bind('<KeyPress-3>', zoom_to_level(7))
root.bind('<KeyPress-4>', zoom_to_level(9))
root.bind('<KeyPress-5>', zoom_to_level(13))

root.bind('<KeyPress-u>', start_undoing)
root.bind('<KeyPress-y>', start_redoing)

root.bind('<KeyPress-space>', start_tool('pan'))
root.bind('<KeyRelease-space>', end_tool('pan', warp_back=True))

root.bind('<KeyPress-Escape>', clear_canvas)

canvas.bind('<MouseWheel>', on_windows_zoom)

root.wm_state('zoomed')
root.mainloop()

