# https://pyglet.readthedocs.io/en/stable/programming_guide/graphics.html
import pyglet
from pyglet.window import key
from pyglet import gl
import math

W, H = 780, 630
BG_COLOR = (0.75, 0.75, 0.75, 1)

NV = 4
COLOR = [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0]  # * NV
SIZE = 30
SPEED_POLYGON = 1

SPEED_CIRCLE = 5
RADIUS = 18
x1, y1 = W // 2, H // 2
keys = dict(Left=False, Right=False, Up=False, Down=False, Fire=False)

level = [
    '--------------------------',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-            --          -',
    '-             --         -',
    '-              --        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '-                        -',
    '--------------------------'
]
level.reverse()

window = pyglet.window.Window(width=W, height=H, caption='DRAW')
window.set_location(5, 30)
window.set_mouse_visible(visible=False)
counter = pyglet.window.FPSDisplay(window=window)

# group = pyglet.graphics.Group()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
batch = pyglet.graphics.Batch()
'''
img = pyglet.image.load('img/1.png')
player = pyglet.sprite.Sprite(
    img, x=(W - img.width) // 2, y=(H - img.height) // 2, batch=batch)
'''
# QUADS
polygon_list = []
x = y = 0
for row in level:
    for col in row:
        if col == '-':
            polygon = batch.add(
                NV, pyglet.gl.GL_QUADS, background,
                ('v2f/stream', [x, y, x, y + SIZE, x + SIZE, y + SIZE, x + SIZE, y]),
                ('c3f/static', COLOR))
            polygon_list.append(polygon)
        x += SIZE
    y += SIZE
    x = 0
vertex_list_length = len(polygon.vertices)
# end QUADS
# circle
point_list = []
for angle in range(0, 360, 10):
    rads = math.radians(angle)
    s = RADIUS * math.sin(rads)
    c = RADIUS * math.cos(rads)
    point_list.append(x1 + c)
    point_list.append(y1 + s)
NP = len(point_list) // 2
circle_list = batch.add(
    NP, pyglet.gl.GL_TRIANGLE_FAN, foreground,
    ("v2f", point_list),
    ("c4f/static", [.0, 1., .0, .5] * NP)
)
point_list_length = len(point_list)
# end circle


def update(dt):
    # circle
    if keys['Left']:
        for i1 in range(point_list_length):
            if i1 % 2 == 0:
                point_list[i1] -= SPEED_CIRCLE
    if keys['Right']:
        for i2 in range(point_list_length):
            if i2 % 2 == 0:
                point_list[i2] += SPEED_CIRCLE
    if keys['Up']:
        for i3 in range(point_list_length):
            if i3 % 2 != 0:
                point_list[i3] += SPEED_CIRCLE
    if keys['Down']:
        for i4 in range(point_list_length):
            if i4 % 2 != 0:
                point_list[i4] -= SPEED_CIRCLE
    circle_list.vertices = point_list
    # end circle
    # QUADS
    for ver in polygon_list:
        new_ver = ver.vertices[:vertex_list_length]
        for n, _ in enumerate(new_ver):
            if n % 2 == 0:
                new_ver[n] -= SPEED_POLYGON
        ver.vertices = new_ver
    # end QUADS


@window.event
def on_draw():
    window.clear()
    batch.draw()
    counter.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.UP:
        keys['Up'] = True
    if symbol == key.DOWN:
        keys['Down'] = True
    if symbol == key.LEFT:
        keys['Left'] = True
    if symbol == key.RIGHT:
        keys['Right'] = True


@window.event
def on_key_release(symbol, modifiers):
    if symbol == key.UP:
        keys['Up'] = False
    if symbol == key.DOWN:
        keys['Down'] = False
    if symbol == key.LEFT:
        keys['Left'] = False
    if symbol == key.RIGHT:
        keys['Right'] = False


# цвет окна
gl.glClearColor(*BG_COLOR)
# включить прозрачность
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

pyglet.clock.schedule_interval(update, 1 / 60.0)
pyglet.app.run()
'''
NV = 4
COLOR = [255, 0, 0] * NV
pyglet.graphics.draw(
    NV, pyglet.gl.GL_POLYGON,
    ('v2i', [x, y, x, y + SIZE, x + SIZE, y + SIZE, x + SIZE, y]),
    ('c3B', COLOR))
NV - первый аргумент (кол-во вершин QUADS или POLYGON)
v2i (v - вершины, 2-а значения (x, y), i - int)
c3B (c - цвет, 3-и значения RGB (для каждой вершины отдельно),
     B - формат (255, 255, 255) или f - формат (1.0, 1.0, 1.0))
'''
'''
from pyglet.gl import *
# круг с радиусом RADIUS и координатами x, y (в def on_draw():)
glLoadIdentity()
glColor4f(1, 0, 0, .75)
glBegin(GL_TRIANGLE_FAN)
for angle in range(0, 360, 10):
    rads = math.radians(angle)
    s = RADIUS * math.sin(rads)
    c = RADIUS * math.cos(rads)
    glVertex3f(x + c, y + s, 0)
glEnd()
'''
