# https://pyglet.readthedocs.io/en/stable/programming_guide/graphics.html
import pyglet
from pyglet import gl
from pyglet.window import key
import math
import sounddevice as sd
import numpy

W, H = 780, 630
BG_COLOR = (.75, .75, .75, 1)

RED = (255, 0, 0, 255)
GREEN = (0, 128, 0, 255)
RADIUS = 20
SIZE = 30
SPEED_FACE = 300

speed_polygon = [30]
face_list = [None] * 4
list_y = [H // 2] * 20
penalty = [0]

playing_field = [
    '----------------------------------------------------------------------------------------------------------------------------------',
    '-                           -                          --                        ---                                  -          -',
    '-                                                      --                                                       -                -',
    '-                                                                                                                                -',
    '-            --                                                   -                                                              -',
    '-                                                                                                                                -',
    '--                                                                -                                                              -',
    '-                                                                                   ---                                          -',
    '-                                       --                                          ---                                     ---  -',
    '-                                                                                                                                -',
    '-                                                                                                                                -',
    '-                                                                                 -                                              -',
    '-                                                     -                                                                          -',
    '-   --------                                          -                                                                          -',
    '-                                                                                                                  -             -',
    '-                                                                  --                                              -             -',
    '-                   --                                                                                                           -',
    '-                                                                             -                                  --              -',
    '-                                   -          -                             -                                  ---              -',
    '-                                   -                                       -                           -                        -',
    '----------------------------------------------------------------------------------------------------------------------------------'
]

playing_field.reverse()

window = pyglet.window.Window(width=W, height=H, caption='Voice Control')
window.set_location(5, 30)
window.set_mouse_visible(visible=False)
counter = pyglet.window.FPSDisplay(window=window)

keys = key.KeyStateHandler()
window.push_handlers(keys)

# group = pyglet.graphics.Group()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
batch = pyglet.graphics.Batch()
'''
img = pyglet.image.load('img/1.png')
player = pyglet.sprite.Sprite(
    img, x=(W - img.width) // 2, y=(H - img.height) // 2, batch=batch)
'''
# text
penalty_label = pyglet.text.Label(
    text=f'Штраф: {penalty[0]}', font_name='Times New Roman', color=(255, 0, 0, 255),
    x=window.width // 2, anchor_x='center', y=window.height - SIZE, anchor_y='top',
    font_size=16, batch=batch, group=foreground)

# start QUADS
polygon_list = []
x = y = 0
for row in playing_field:
    for col in row:
        if col == '-':
            polygon = batch.add(
                4, pyglet.gl.GL_QUADS, background,
                ('v2f/stream', [x, y, x, y + SIZE, x + SIZE, y + SIZE, x + SIZE, y]),
                ('c3f/static', (0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0)))
            polygon_list.append(polygon)
        x += SIZE
    y += SIZE
    x = 0
# end QUADS


class FaceObject(object):
    def __init__(self, x_face, y_face, radius_face, color_face):
        super(FaceObject, self).__init__()
        self.x = x_face
        self.y = y_face
        self.radius = radius_face
        self.color = color_face
        self.index = 0

    def update(self):
        self.draw_face(0, 360, 6, self.x, self.y, self.radius, self.color)
        self.draw_face(
            0, 360, 36, self.x - self.radius * 0.42, self.y + self.radius * 0.2,
            self.radius // 6, self.color)
        self.draw_face(
            0, 360, 36, self.x + self.radius * 0.42, self.y + self.radius * 0.2,
            self.radius // 6, self.color)
        self.draw_face(210, 340, 10, self.x, self.y, self.radius * 0.6, self.color)

    def draw_face(self, a, b, c, x_elem, y_elem, radius_elem, color_elem):
        if self.index > 3:
            self.index = 0
            for i in face_list:
                i.delete()  # очищаем графику (batch)
        point_list = []
        for angle in range(a, b, c):
            radian = math.radians(angle)
            x_circle = radius_elem * math.cos(radian)
            y_circle = radius_elem * math.sin(radian)
            point_list.append(x_elem + x_circle)
            point_list.append(y_elem + y_circle)
        number_points = len(point_list) // 2
        face_list[self.index] = batch.add(
            number_points, pyglet.gl.GL_POINTS, foreground,
            ('v2f/stream', point_list),
            ('c4B/static', color_elem * number_points)
        )
        self.index += 1


def update(dt):
    face.update()
    if face.color == RED:
        face.color = GREEN
    # motion face
    if keys[key.LEFT] and face.x > RADIUS:
        face.x -= SPEED_FACE * dt
    if keys[key.RIGHT] and face.x < W - RADIUS:
        face.x += SPEED_FACE * dt
    if keys[key.UP] and face.y < H - RADIUS:
        face.y += SPEED_FACE * dt
    if keys[key.DOWN] and face.y > RADIUS:
        face.y -= SPEED_FACE * dt

    for ver in polygon_list:
        # motion QUADS
        ver.vertices = [
            elem - speed_polygon[0] * dt if e % 2 == 0 else elem
            for e, elem in enumerate(ver.vertices)]
        # collision
        nx = max(ver.vertices[0], min(face_list[0].vertices[0] - RADIUS, ver.vertices[0] + SIZE))
        ny = max(ver.vertices[1], min(face_list[0].vertices[1], ver.vertices[1] + SIZE))
        dtc = (nx - (face_list[0].vertices[0] - RADIUS)) ** 2 + (ny - face_list[0].vertices[1]) ** 2
        if dtc <= RADIUS ** 2 and face_list[0].vertices[0] < W - RADIUS * 2:
            penalty[0] += 0.1
            penalty_label.text = f'Штраф: {round(penalty[0], 1)}'
            face.color = RED

    if polygon_list[0].vertices[0] <= -W * 4:
        speed_polygon[0] = 0
        if face.x < W - RADIUS:
            face.x += SPEED_FACE // 10 * dt
        else:
            stream.stop(ignore_errors=True)
            stream.close(ignore_errors=True)


@window.event
def on_draw():
    window.clear()
    batch.draw()
    counter.draw()


def audio_callback(indata, frames, time, status):
    list_y.append(numpy.linalg.norm(indata) * 20)
    list_y.pop(0)
    volume = int(sum(list_y) / len(list_y))
    if face.x < W - RADIUS:
        face.y = volume
    if face.y > H - RADIUS:
        face.y = H - RADIUS
    # sd.sleep(10)


gl.glClearColor(*BG_COLOR)  # цвет окна
# включает прозрачность
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
gl.glPointSize(2)  # размер точек
gl.glEnable(gl.GL_POINT_SMOOTH)  # сглаживание точек
# gl.glLineWidth(4)
# gl.glEnable(gl.GL_LINE_SMOOTH)

face = FaceObject(W // 2, H // 2, RADIUS, GREEN)

stream = sd.InputStream(callback=audio_callback)
with stream:
    pyglet.clock.schedule_interval(update, 1 / 30.0)
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
