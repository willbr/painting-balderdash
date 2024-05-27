from tkinter import *
from tkinter.ttk import *
from math import sqrt

background_colour = '#aaa'

toolbox_font_spec = ('georgia 16 bold')
menu_font_spec    = ('georgia 16 bold')

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

colours = {
    'Black': '#333',
    'Dark-Gray': '#5f574f',
    'Light-Grey': '#c2c3c7',
    'White': '#eee',
    'Yellow': '#ffd817',
    'Orange': '#ff4f00',
    'Red': '#e33',
    'Green': '#8BEF88',
    'Blue': '#88f',
    'Purple': '#A349A4',
}



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

toolbox_style = Style()
toolbox_style.configure('Custom.TFrame', background='#888')

toolbox_label_style = Style()
toolbox_label_style.configure('Custom.TLabel', background='#888')

toolbox = Frame(root, style='Custom.TFrame')

brush_label = Label(toolbox, text=f'N', font=toolbox_font_spec, style='Custom.TLabel')
brush_label.pack(side=TOP, padx=10, pady=10)

tool_label = Label(toolbox, text=f'tool', font=toolbox_font_spec, style='Custom.TLabel')
tool_label.pack(side=TOP, padx=10, pady=10)

layer_label = Label(toolbox, text=f'layer', font=toolbox_font_spec, style='Custom.TLabel')
layer_label.pack(side=TOP, padx=10, pady=10)

zoom_label = Label(toolbox, text=f' 100.00%', font=toolbox_font_spec, style='Custom.TLabel')
zoom_label.pack(side=TOP, padx=10, pady=10)

toolbox.place(x=10, y=10)

hscrollbar.config(command=canvas.xview)
vscrollbar.config(command=canvas.yview)

brush_size = None
brush_size_on_canvas = None
brush_color = '#8B88EF'

current_tool = None
current_layer = None

tool_pallete = None

undo_stack = []
redo_stack = []

layer = {
        'outline': {'visible': True},
        'colour': {'visible': True},
        'sketch': {'visible': True},
        'background': {'visible': True},
        }

brush_cursor_id = canvas.create_oval(0, 0, 0, 0, outline='grey', fill=brush_color, width=0)

def set_brush_size(new_size):
    global brush_size
    global brush_size_on_canvas
    brush_size = int(min(max(2, new_size), 200))
    brush_label.configure(text=f'{brush_size:3d}')
    brush_size_on_canvas = int(max(2, brush_size * zoom_scales[zoom_level]))
    brush_size_on_canvas -= brush_size_on_canvas % 2 # bugfix; removes shimmering artifacts
    #print(f'{brush_size_on_canvas=}')


def get_visible_ids(tag_name=None, ignore_tags=None):
    ignore_list = []
    ignore_list.extend(canvas.find_withtag('colours'))
    ignore_list.extend(canvas.find_withtag('info'))
    ignore_list.append(brush_cursor_id)
    ignore_list.append(brush_cursor_id)

    #visible_ids = set(canvas.find_all()) - set(ignore_list)
    all_items = canvas.find_all() if tag_name is None else canvas.find_withtag(tag_name)
    visible_ids = {item for item in all_items if canvas.itemcget(item, 'state') != 'hidden'} - set(ignore_list)
    return visible_ids


def get_live_ids(tag_name=None):
    all_items = canvas.find_all() if tag_name is None else canvas.find_withtag(tag_name)
    deleted_ids = canvas.find_withtag('deleted')
    live_layer_ids = tuple(set(all_items) - set(deleted_ids))
    return live_layer_ids


def clear_canvas(event=None):
    visible_ids = get_visible_ids()
    #print(visible_ids)
    for object_id in visible_ids:
        canvas.itemconfig(object_id, state='hidden')
        canvas.addtag_withtag('deleted', object_id)

    undo_stack.append(('clear', visible_ids))

    canvas.focus_set()

    target_level = 5
    diff = target_level - zoom_level

    zoom(0, 0, diff)

    select_layer('sketch')

    layer['outline']['visible'] = True
    layer['colour']['visible'] = True
    layer['sketch']['visible'] = True
    layer['background']['visible'] = True

    set_brush_size(14)


def sort_objects_by_layer():
    for layer_name in ['background', 'sketch', 'colour', 'outline']:
        canvas.tag_raise(layer_name)


def paint_start(event):
    global line_points
    global line_id
    #echo_event(event)

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    line_points = [x,y, x,y]


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
            tags=current_layer,
            )

    sort_objects_by_layer()

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

    layer_state = 'normal' if layer[current_layer]['visible'] else 'hidden'
    canvas.itemconfig(line_id, state=layer_state)

    undo_stack.append(('line', (line_id,)))
    redo_stack.clear()


def start_polygon(event):
    global line_points
    global line_id
    #echo_event(event)

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    line_points = [x,y, x,y]


    canvas.itemconfig(brush_cursor_id, state='hidden')
    canvas.config(cursor='crosshair')

    line_id = canvas.create_polygon(
            x, y,
            x, y,
            fill=brush_color,
            width=brush_size_on_canvas,
            joinstyle='round',
            smooth=True, # it's too slow, once you have lots of things on screen
                          # maybe try disabling it while scrolling?
            tags=current_layer,
            )

    sort_objects_by_layer()

    motion_polygon(event)


def motion_polygon(event):
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


def end_polygon(event):
    #echo_event(event)
    if line_points is None:
        return
    canvas.config(cursor='none')

    #num_points = len(line_points)
    #print(f'{num_points=}\n')
    canvas.itemconfig(brush_cursor_id, state='normal')
    canvas.tag_raise(brush_cursor_id)
    update_brush_cursor(event)
    on_canvas_resize(event)

    layer_state = 'normal' if layer[current_layer]['visible'] else 'hidden'
    canvas.itemconfig(line_id, state=layer_state)

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
    #print('warping cursor')
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


def show_colour_pallete(event):
    canvas.config(cursor='crosshair')

    width  = 60
    height = 60
    step_x = width // 2
    step_y = height // 2
    pallete_width = (len(colours) * width)
    pallete_height = height

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    x -= (pallete_width // 2) - (step_x)

    for name, colour in colours.items():
        canvas.create_rectangle(
                x - step_x,
                y - step_y,
                x+step_x,
                y+step_y,
                fill=colour,
                tags='colour_pallete',
                )
        x += width


def hide_colour_pallete(event):
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

    canvas.delete('colour_pallete')
    canvas.config(cursor='none')


def select_layer(name):
    global current_layer
    current_layer = name
    layer_label.configure(text=f'{name}')


def render_layer_menu(x, y, step_x, step_y, name):
    tag_show = f'show_layer_{name}'
    tag_select  = f'select_layer{name}'
    tag_clear   = f'clear_layer_{name}'

    show_colour   = '#88f'
    select_colour = '#eee' if name == current_layer else '#8e8'
    clear_colour  = '#e33'

    font_colour = '#333'

    show_label = 'hide' if layer[name]['visible'] else 'show'

    # show

    canvas.create_rectangle(
            x - step_x - (step_x//2),
            y - step_y,
            x+step_x,
            y+step_y,
            fill=show_colour,
            tags=f'layer_pallete {tag_show}')

    canvas.create_text(
            x - step_x - (step_x//4),
            y,
            text=show_label,
            fill=font_colour,
            font=menu_font_spec,
            tags=f'layer_pallete {tag_show}')

    # select

    canvas.create_rectangle(
            x - step_x,
            y - step_y,
            x+step_x,
            y+step_y,
            fill=select_colour,
            tags=f'layer_pallete {tag_select}')

    canvas.create_text(
            x,
            y,
            text=name,
            fill=font_colour,
            font=menu_font_spec,
            tags=f'layer_pallete {tag_select}')

    # clear

    canvas.create_rectangle(
            x + step_x,
            y - step_y,
            x+step_x+(step_x//2),
            y+step_y,
            fill=clear_colour,
            tags=f'layer_pallete {tag_clear}')

    canvas.create_text(
            x + step_x+(step_x//4),
            y,
            text='x',
            fill=font_colour,
            font=('georgia 32 bold'),
            tags=f'layer_pallete {tag_clear}')


def show_layer_pallete(event):
    layer_object_ids = tuple(canvas.find_withtag('layer_pallete'))
    #print(layer_object_ids)

    if layer_object_ids:
        print('skipping show layer pallete')
        return

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    width = 320
    height = 60
    step_x = width // 2
    step_y = height // 2
    gap = 20

    render_layer_menu(x, y, step_x, step_y, name='outline')
    y += height + gap
    render_layer_menu(x, y, step_x, step_y, name='colour')
    y += height + gap
    render_layer_menu(x, y, step_x, step_y, name='sketch')
    y += height + gap
    render_layer_menu(x, y, step_x, step_y, name='background')

    canvas.config(cursor='crosshair')


def clear_layer(layer_name):
    print(f'clear_layer {layer_name=}')
    layer_ids = get_live_ids(layer_name)

    if not layer_ids:
        return

    for object_id in layer_ids:
        canvas.addtag_withtag('deleted', object_id)
        canvas.itemconfig(object_id, state='hidden')

    undo_stack.append(('clear_layer', layer_name, layer_ids))


def toggle_layer_visible(layer_name):
    print(f'toggle_layer_visible {layer_name=}')
    is_visible = layer[layer_name]['visible']
    layer[layer_name]['visible'] = not is_visible
    layer_ids = canvas.find_withtag(layer_name)
    new_state = 'hidden' if is_visible else 'normal'

    layer_ids = get_live_ids(layer_name)

    for object_id in layer_ids:
        canvas.itemconfig(object_id, state=new_state)


def end_layer_pallete(event):
    current = canvas.find_withtag("current")
    object_id = current[0] if current != () else None

    canvas.config(cursor='none')

    #print(f'{object_id=}')
    if object_id is None:
        pass
    elif object_id != brush_cursor_id:
        tags = tuple(set(canvas.itemcget(object_id, 'tags').split(' ')) - set(('layer_pallete', 'current')))
        tag = tags[0]
        #print(f'{object_id=} {tag=}')

        layer_ids = None

        action, layer_name = tag.rsplit('_', 1)

        match action:
            case 'show_layer':
                toggle_layer_visible(layer_name)
                undo_stack.append(('toggle_layer_visible', layer_name))
            case 'select_layer':
                select_layer(layer_name)
            case 'clear_layer':
                clear_layer(layer_name)
            case _:
                print(f'unknown {action}')

    hide_layer_pallete()


def hide_layer_pallete():
    canvas.delete('layer_pallete')


def select_brush_tool():
    #print('select_brush_tool')
    tool_label.configure(text=f'brush')
    canvas.config(cursor='none')
    root.bind('<ButtonPress-1>', start_tool('brush'))
    root.bind('<ButtonRelease-1>', end_tool('brush', warp_back=False))


def select_polygon_tool():
    #print('select_polygon_tool')
    tool_label.configure(text=f'polygon')
    canvas.config(cursor='crosshair')
    root.bind('<ButtonPress-1>', start_tool('polygon'))
    root.bind('<ButtonRelease-1>', end_tool('polygon', warp_back=False))


def show_tool_pallete(event):
    global tool_pallete
    tool_pallete = {}

    tool_object_ids = tuple(canvas.find_withtag('tool_pallete'))

    if tool_object_ids:
        print('skipping show tool pallete')
        return

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    width = 320
    height = 60
    step_x = width // 2
    step_y = height // 2
    gap = 20

    create_tool_menu(x, y, step_x, step_y, name='brush', func=select_brush_tool)
    y += height + gap
    create_tool_menu(x, y, step_x, step_y, name='polygon', func=select_polygon_tool)

    canvas.config(cursor='crosshair')


def hide_tool_pallete():
    #print('hide tool pallete')
    canvas.delete('tool_pallete')
    canvas.config(cursor='none')


def end_tool_pallete(event):
    #print('end tool pallete')
    current_ids = canvas.find_withtag('current')
    tool_ids = canvas.find_withtag('tool_pallete')

    current_tool_ids = tuple(set(current_ids) & set(tool_ids))
    if current_tool_ids:
        current_tool_id = current_tool_ids[0]
        fn = tool_pallete[current_tool_id]
        fn(event)
    hide_tool_pallete()


def create_tool_menu(x, y, step_x, step_y, name, func):
    global tool_pallete

    button_colour = '#8e8'
    highlight_colour = '#eee'
    font_colour = '#333'

    background_id = canvas.create_rectangle(
            x - step_x,
            y - step_y,
            x+step_x,
            y+step_y,
            fill=button_colour,
            tags=f'tool_pallete')

    text_id = canvas.create_text(
            x,
            y,
            text=name,
            fill=font_colour,
            font=('georgia 16 bold'),
            tags=f'tool_pallete')

    def click_button(event):
        hide_tool_pallete()
        func()
        return 'break'

    def enter_button(event):
        canvas.itemconfig(background_id, fill=highlight_colour)

    def leave_button(event):
        canvas.itemconfig(background_id, fill=button_colour)

    tool_pallete[background_id] = click_button
    tool_pallete[text_id]       = click_button

    canvas.tag_bind(background_id, '<Button-1>', click_button)
    canvas.tag_bind(text_id, '<Button-1>', click_button)

    canvas.tag_bind(background_id, '<Enter>', enter_button)
    canvas.tag_bind(text_id, '<Enter>', enter_button)

    canvas.tag_bind(background_id, '<Leave>', leave_button)


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

        if tool_name == current_tool:
            return
        elif current_tool is not None:
            return

        #print(f'start_tool {tool_name=} {current_tool=}')
        current_tool = tool_name

        tool_fn = tools[tool_name]['start']
        tool_fn(event)

        save_cursor_position(event)

    return fn


def end_tool(tool_name, warp_back):
    def fn(event):
        global current_tool
        if tool_name != current_tool:
            #print(f'end tool: {tool_name=} != {current_tool=}')
            return
        #print(f'end_tool {tool_name=}')

        current_tool = None

        tool_fn = tools[tool_name].get('end', None)
        if tool_fn is None:
            print(f'no end fn for: {tool_name}')
            return

        tool_fn(event)

        if warp_back:
            restore_cursor_position(event)

    return fn


def apply_change(action, change_type):
    match action:
        case 'clear_layer', layer_name, object_ids:
            new_state = 'normal' if change_type == 'undo' else 'hidden'
            #print(f'{change_type=} clear layer {layer_name=} {object_ids}')

        case 'toggle_layer_visible', layer_name:
            toggle_layer_visible(layer_name)
            object_ids = ()

        case _, object_ids:
            new_state = 'hidden' if change_type == 'undo' else 'normal'
            pass

    for object_id in object_ids:
        #print(f'apply {object_id=} {new_state=}')
        if new_state == 'hidden':
            canvas.addtag_withtag('deleted', object_id)
        else:
            canvas.dtag(object_id, 'deleted')
        canvas.itemconfig(object_id, state=new_state)


def start_undoing(event):
    if not undo_stack:
        print('nothing to undo')
        return

    action = undo_stack.pop()
    apply_change(action, 'undo')
    redo_stack.append(action)


def start_redoing(event):
    if not redo_stack:
        print('nothing to redo')
        return

    action = redo_stack.pop()
    apply_change(action, 'redo')
    undo_stack.append(action)


def start_background_mode(event):
    select_layer('background')
    set_brush_size(128)


def start_sketch_mode(event):
    global brush_color

    select_layer('background')

    brush_color = colours['Blue']
    canvas.itemconfig(brush_cursor_id, fill=brush_color)

    set_brush_size(14)
    select_brush_tool()


def start_colour_mode(event):
    select_layer('colour')
    set_brush_size(28)


def start_outline_mode(event):
    global brush_color

    select_layer('outline')

    brush_color = colours['Black']
    canvas.itemconfig(brush_cursor_id, fill=brush_color)

    set_brush_size(10)
    select_brush_tool()


tools = {
    'brush': {
        'start':  paint_start,
        'motion': paint_motion,
        'end':    paint_end,
    },
    'polygon': {
        'start':  start_polygon,
        'motion': motion_polygon,
        'end':    end_polygon,
    },
    'color_pallete': {
        'start':  show_colour_pallete,
        'end':    hide_colour_pallete,
    },
    'layer_pallete': {
        'start':  show_layer_pallete,
        'end':    end_layer_pallete,
    },
    'tool_pallete': {
        'start':  show_tool_pallete,
        'end':    end_tool_pallete,
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

select_brush_tool()

canvas.bind('<Enter>', lambda e: canvas.itemconfig(brush_cursor_id, state='normal'))
canvas.bind('<Leave>', lambda e: canvas.itemconfig(brush_cursor_id, state='hidden'))

root.bind('<KeyPress-f>', start_tool('color_pallete'))
root.bind('<KeyRelease-f>', end_tool('color_pallete', warp_back=True))

root.bind('<KeyPress-g>', start_tool('layer_pallete'))
root.bind('<KeyRelease-g>', end_tool('layer_pallete', warp_back=True))

root.bind('<KeyPress-d>', start_tool('tool_pallete'))
root.bind('<KeyRelease-d>', end_tool('tool_pallete', warp_back=False))

root.bind('<KeyPress-s>', start_tool('brush_size'))
root.bind('<KeyRelease-s>', end_tool('brush_size', warp_back=True))

root.bind('<KeyPress-v>', start_tool('zoom'))
root.bind('<KeyRelease-v>', end_tool('zoom', warp_back=True))

root.bind('<KeyPress-1>', zoom_to_level(3))
root.bind('<KeyPress-2>', zoom_to_level(5))
root.bind('<KeyPress-3>', zoom_to_level(7))
root.bind('<KeyPress-4>', zoom_to_level(9))
root.bind('<KeyPress-5>', zoom_to_level(13))

root.bind('<KeyPress-q>', start_background_mode)
root.bind('<KeyPress-w>', start_sketch_mode)
root.bind('<KeyPress-e>', start_colour_mode)
root.bind('<KeyPress-r>', start_outline_mode)

root.bind('<KeyPress-u>', start_undoing)
root.bind('<KeyPress-y>', start_redoing)

root.bind('<KeyPress-space>', start_tool('pan'))
root.bind('<KeyRelease-space>', end_tool('pan', warp_back=True))

root.bind('<KeyPress-Escape>', clear_canvas)

canvas.bind('<MouseWheel>', on_windows_zoom)

#root.wm_state('zoomed')
root.mainloop()

