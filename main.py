from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'orientation', 'landscape')
from kivy.app import App
from kivy.core.audio import SoundLoader
#from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Rectangle, Triangle
from kivy.properties import Clock
from kivy.core.window import Window
from kivy import platform
from kivy.lang import Builder
from kivy.graphics.texture import Texture
import random
from pre import *

class Gradient(object):
    @staticmethod
    def horizontal(rgba_left, rgba_right):
        texture = Texture.create(size=(2, 1), colorfmt="rgba")
        # Convertir les valeurs des pixels en octets
        pixels = rgba_left + rgba_right
        pixel_bytes = [int(v * 255) for v in pixels]
        # Creer le buffer de pixels en utilisant struct.pack
        buffer_data = bytes(pixel_bytes)
        # Utiliser le buffer de pixels pour remplir la texture
        texture.blit_buffer(buffer_data, colorfmt='rgba', bufferfmt='ubyte')
        return texture

    @staticmethod
    def vertical(rgba_top, rgba_bottom):
        texture = Texture.create(size=(1, 2), colorfmt="rgba")
        pixels = rgba_bottom + rgba_top
        pixel_bytes = [int(v * 255) for v in pixels]
        buffer_data = bytes(pixel_bytes)
        texture.blit_buffer(buffer_data, colorfmt='rgba', bufferfmt='ubyte')
        return texture
class ColorQuad(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.Color = Color(*color)  # Couleur initiale (rouge)
            self.Quad = Quad()
    def set_points(self, points):
        self.Quad.points = points
    def set_color(self, r, g, b, a=1):
        self.Color.rgba = (r, g, b, a)

resolution = (Window.width, Window.height)
def dp(value):
    return value#value*resolution[0]/900

Builder.load_file("menu.kv")
class Player(Widget):
    color = (.4, 0, .6)
    color = Data(up=(.4, 0, .6), side=(.2, 0, .3),
                 up_=(.6, .05, .1), side_=(.3, .025, .05),
                 up2=(.2, .5, .2), side2=(.1, .25, .1))
    base_size = (dp(90), dp(17))
    base_depth = dp(30)
    depth = base_depth
    limit_depth = dp(20)
    speed_depth = dp(1)
    direction_depth = 1
    mode = 0
    Y = dp(3)
    y_ = 1
    def __init__(self, main_widget, **kwargs): ###
        super().__init__(**kwargs)
        self.MainWidget = main_widget
        self.init_rectangles()

    def init_rectangles(self):
        with self.canvas:
            self.Rectangle = ColorQuad(self.color.data["up"])
            self.RectangleU = ColorQuad(self.color.data["up"])

            self.RectangleL = ColorQuad(self.color.data["side"])
            self.RectangleR = ColorQuad(self.color.data["side"])
    def init(self):
        self.MainWidget.add_widget(self)

    def get_points(self):
        return [self.MainWidget.transform(self.pos[0]+self.size_[0]/2, self.pos[1]),
                self.MainWidget.transform(self.pos[0]+self.size_[0]/2, self.pos[1]+self.size_[1])]

    def switch_mode(self):
        self.MainWidget.offset.y.add_speed += dp(0.05)
        self.mode = (self.mode+1)%4
        if self.mode == 0:
            self.RectangleU.set_color(*self.color.data["up"])
            self.RectangleL.set_color(*self.color.data["side"])
            self.RectangleR.set_color(*self.color.data["side"])
        elif self.mode in [1, 3]:
            self.RectangleU.set_color(*self.color.data["up_"])
            self.RectangleL.set_color(*self.color.data["side_"])
            self.RectangleR.set_color(*self.color.data["side_"])
        elif self.mode == 2:
            self.RectangleU.set_color(*self.color.data["up2"])
            self.RectangleL.set_color(*self.color.data["side2"])
            self.RectangleR.set_color(*self.color.data["side2"])
    def reset_mode(self):
        self.mode = 0
        self.RectangleU.set_color(*self.color.data["up"])
        self.RectangleL.set_color(*self.color.data["side"])
        self.RectangleR.set_color(*self.color.data["side"])

    def update(self, time_factor):
        self.Y += self.y_*dp(0.1)
        if not dp(-3) < self.Y < dp(12):
            self.y_ *= -1


        self.depth += (self.depth**1.5)/100*self.direction_depth*time_factor
        if abs(self.depth - self.base_depth) > self.limit_depth:
            self.depth = self.base_depth + self.limit_depth*self.direction_depth
            self.direction_depth *= -1

        r_x, r_y = self.MainWidget.get_ratios()
        size = [self.base_size[0]*r_x, self.base_size[1]*r_y]
        self.size_ = size
        self.pos = ((self.MainWidget.width-size[0])/2, self.Y)
        #self.Rectangle.pos = self.pos
        points = [
            self.pos[0]+size[0]/2, self.pos[1],
            self.pos[0], self.pos[1]+size[1]/2,
            self.pos[0]+size[0]/2, self.pos[1]+size[1],
            self.pos[0]+size[0], self.pos[1]+size[1]/2
        ]
        real_points = []
        up = []
        for i, value in enumerate(points):
            if i%2 != 0:
                point = self.MainWidget.transform(points[i-1], value)
                real_points.append(point[0])
                real_points.append(point[1])
                up.append(point[0])
                up.append(point[1]+self.depth)

        self.Rectangle.set_points(real_points)
        self.RectangleU.set_points(up)
        self.RectangleL.set_points([*self.Rectangle.Quad.points[2:4], *self.Rectangle.Quad.points[0:2], *self.RectangleU.Quad.points[0:2], *self.RectangleU.Quad.points[2:4]])
        self.RectangleR.set_points([*self.Rectangle.Quad.points[6:8], *self.Rectangle.Quad.points[0:2], *self.RectangleU.Quad.points[0:2], *self.RectangleU.Quad.points[6:8]])
class Tile:
    def __init__(self, main_widget, x, y, turn=False, long=False, switch=False):
        self.MainWidget = main_widget
        self.x, self.y = x, y
        self.Quad = None

        self.turn = turn
        self.long = long
        self.switch = switch
        self.used = False
    def get_coo(self):
        return self.x, self.y

class MainWidget(RelativeLayout):
    from transforms import transform, reverse_transform, transform_2D, transform_perspective, reverse_transform_perspective
    from user_actions import on_touch_down, on_touch_up, on_keyboard_down, on_keyboard_up

    menu_widget = ObjectProperty(None)
    score = NumericProperty(0)
    perspective_point_x, perspective_point_y = NumericProperty(0), NumericProperty(0)

    triangles = []
    glint = Value(value=9999, speed=dp(25), wait=150, elements=[])
    text = Data(title_start="[color=E6331A]RetroRide[/color][color=B21980]LaserRoad[/color]",
                title_game_over="End of the Road",
                button_start="START",
                button_game_over="RESTART")
    menu_title, menu_button_title = StringProperty(text.data["title_start"]),\
                                    StringProperty(text.data["button_start"])
    perspective = Point(x=Value(speed=dp(.6), direction=1, limit=0.1, wait=150),
                        y=Value(speed=dp(2), direction=0, limits=[.75, .55]))
    offset = Point(x=Value(value=0, speed=dp(25), direction=0, speed2=50, speed3=dp(5)),
                  y=Value(value=0, speed=dp(3.4), data={"speed2": dp(6)}))

    color = Data(line=(.7, .1, .5), tile=(.7, .1, .5), glint=(1, 1, 1, .2))
    nb_horizontal_lines, nb_vertical_lines = 9, 10-2
    spacing_horizontal_lines, spacing_vertical_lines = .1, .3
    lines_x, lines_y = [], []

    nb_tiles = int(nb_horizontal_lines * 2)
    tiles_quad, tiles_coo = [], []
    current_y_loop, current_front_x = 0, 0
    last_y, step_y, start_y = 0, 0, 0

    state_game_over = False
    state_game_has_started = False

    first_wait = [0, 60]

    FPS = 60
    def __init__(self, **kwargs): ###
        super().__init__(**kwargs) # MainWidget, self

        self.Player = Player(self)

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        #self.init_audio()
        self.init_lines()
        self.init_tiles()
        self.init_landscape()
        self.init_glint()
        self.Player.init()
        self.generate_tiles_coo()
        #self.size_hint = (None, None)
        Clock.schedule_interval(self.update, 1.0 / self.FPS)

    def set_game(self):
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.start_y = self.last_y
    def set_game_over(self):
        self.state_game_over = True
        self.menu_widget.opacity = 1
        self.menu_title = self.text.data["title_game_over"]
        self.menu_button_title = self.text.data["button_game_over"]

    def reset_game(self):
        self.perspective_point_x = self.width/2
        self.score = 0
        self.perspective.x.direction = 1
        self.perspective.x.wait[0] = 0
        self.menu_title = self.text.data["title_start"]
        self.menu_button_title = self.text.data["button_start"]
        self.current_y_loop, self.offset.y.value, self.offset.x.value, self.current_front_x = 0, 0, 0, 0
        self.last_y = 0
        self.start_y = 0
        self.step_y = 0
        self.offset.y.add_speed = 0
        self.offset.x.direction = 0
        self.first_wait[0] = 0
        self.tiles_coo = []
        self.generate_tiles_coo()
        self.state_game_over, self.state_game_has_started = False, False

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard.unbind(on_key_up=self.on_keyboard_up)
        self._keyboard = None
    @staticmethod
    def is_desktop():
        return platform in ('linux', 'win', 'macosx')

    def init_audio(self):
        self.sound_music1 = SoundLoader.load("audio/retro.mp3")
        self.sound_music1.volume = 0.5
        self.sound_music1.loop = True
        self.sound_music1.play()
    def init_lines(self):
        with self.canvas:
            Color(*self.color.data["line"])
            self.lines_y = [Line(width=0.5) for _ in range(self.nb_vertical_lines)]
            self.lines_x = [Line(width=0.5) for _ in range(self.nb_horizontal_lines)]
    def init_tiles(self):
        with self.canvas:
            #Color(*self.color.data["tile"])
            self.tiles_quad = [ColorQuad(self.color.data["tile"]) for _ in range(self.nb_tiles)]
    def init_landscape(self):
        with self.canvas:
            Color(.15, .0, .15, 1)
            self.triangles = [Quad(), Quad()]
            Color(.7, .1, .5)
            self.triangles.append(Triangle())
            self.triangles.append(Triangle())
            Color(.08, .0, .08, 1)
            self.triangles.append(Triangle())
            self.triangles.append(Triangle())
            Color(.02, .0, .02)
            self.triangles.append(Quad())
            self.triangles.append(Quad())
            self.triangles.append(Triangle())
    def init_glint(self):
        with self.canvas.after:
            Color(*self.color.data["glint"])
            self.glint.elements.append(Quad())
            self.glint.elements.append(Quad())

    def generate_tiles_coo(self):
        for i in reversed(range(len(self.tiles_coo))):
            ti_x, ti_y = self.tiles_coo[i].get_coo()
            if ti_y < self.current_y_loop:
                del self.tiles_coo[i]
        last_y = self.last_y
        n = self.step_y < int((last_y-self.start_y)/80)
        if not self.state_game_over and self.state_game_has_started:
            for i in range(self.nb_tiles-len(self.tiles_coo)):
                if n:
                    self.step_y += 1
                    n = False
                    for _ in range(1):
                        self.tiles_coo.append(Tile(self, self.current_front_x, last_y, long=True, switch=True))
                        last_y += 1
                    for _ in range(13):
                        self.tiles_coo.append(Tile(self, self.current_front_x, last_y, long=True))
                        last_y += 1
                    for _ in range(1):
                        self.tiles_coo.append(Tile(self, self.current_front_x, last_y, switch=True))
                        last_y += 1
                    for _ in range(2):
                        self.tiles_coo.append(Tile(self, self.current_front_x, last_y))
                        last_y += 1
                else:
                    if self.Player.mode in [0, 1, 3]:
                        r = random.randint(-1 if self.current_front_x > -self.nb_vertical_lines/2 + 1 else 0,
                                           1 if self.current_front_x < self.nb_vertical_lines/2 - 1 else 0)
                    elif self.Player.mode == 2:
                        r = random.randint(-4 if self.current_front_x > -self.nb_vertical_lines/2 + 1 else 0,
                                           4 if self.current_front_x < self.nb_vertical_lines/2 - 1 else 0)
                    self.tiles_coo.append(Tile(self, self.current_front_x, last_y))
                    if r != 0:
                        r = r/abs(r)
                        last_y += 1
                        self.tiles_coo.append(Tile(self, self.current_front_x, last_y, turn=True))
                        self.tiles_coo.append(Tile(self, self.current_front_x+r, last_y))
                        #self.tiles_coo.append((self.current_front_x+r, last_y))
                        self.current_front_x += r
                    last_y += 1
        else:
            for _ in range(len(self.tiles_coo), self.nb_tiles):
                self.tiles_coo.append(Tile(self, self.current_front_x, last_y))
                last_y += 1
        self.last_y = last_y
    def get_ratios(self):
        return self.width/900, self.height/400

    def get_spacing_vertical_lines(self):
        return self.width*self.spacing_vertical_lines
    def get_spacing_horizontal_lines(self):
        return self.height*self.spacing_horizontal_lines
    def get_line_x_from_index(self, i):
        i += self.nb_vertical_lines / 2 - 1
        spacing_lines_y = self.get_spacing_vertical_lines()
        X = (self.width - spacing_lines_y * (self.nb_vertical_lines - 1)) / 2 + self.offset.x.value
        return int(X + spacing_lines_y*i)
    def get_line_y_from_index(self, i):
        spacing_lines_x = self.get_spacing_horizontal_lines()
        return int(spacing_lines_x*i - self.offset.y.value)
    def get_tile_coo(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x, y = self.get_line_x_from_index(ti_x), self.get_line_y_from_index(ti_y)
        return x, y
    def player_on_the_way(self):
        on_the_way = False
        long = False
        for x, y in self.Player.get_points():
            x, y = self.reverse_transform(x, y)
            X = round((x-self.width/2 - self.offset.x.value)/self.get_spacing_vertical_lines())
            Y = int((y + self.offset.y.value)/self.get_spacing_horizontal_lines() + self.current_y_loop)
            for tile in self.tiles_coo:
                if (X, Y) == tile.get_coo():
                    on_the_way = True
                    if tile.switch and not tile.used:
                        tile.used = True
                        self.Player.switch_mode()
                    if tile.long: long = True
        if long:
            self.offset.y.speed = self.offset.y.data["speed2"] + self.offset.y.add_speed
            self.perspective.y.direction = -1

        else:
            self.offset.y.speed = self.offset.y.base_speed + self.offset.y.add_speed
            self.perspective.y.direction = 1
        self.perspective_point_y = self.perspective.y.get_bounded_limits(self.perspective_point_y, self.height)
        self.perspective_point_y += self.perspective.y.get_actual_speed()

        return on_the_way

    def update_lines(self):
        for i, line in enumerate(self.lines_y):
            x = self.get_line_x_from_index(i - self.nb_vertical_lines / 2 + 1)
            line.points = [*self.transform(x, 0), *self.transform(x, self.height)]

        first_line_x, last_line_x = self.get_line_x_from_index(-self.nb_vertical_lines / 2 + 1),\
                                    self.get_line_x_from_index(self.nb_vertical_lines / 2)
        for i, line in enumerate(self.lines_x):
            y = self.get_line_y_from_index(i)
            line.points = [*self.transform(first_line_x, y), *self.transform(last_line_x, y)]
    def update_tiles(self):
        for i, quad in enumerate(self.tiles_quad):
            ti_x, ti_y = self.tiles_coo[i].get_coo()
            xmin, ymin = self.get_tile_coo(ti_x, ti_y)
            xmax, ymax = self.get_tile_coo(ti_x + 1, ti_y + 1)
            quad.set_points([*self.transform(xmin, ymin), *self.transform(xmin, ymax),
                             *self.transform(xmax, ymax), *self.transform(xmax, ymin)])
            if self.tiles_coo[i].turn: quad.set_color(.9, .1, .5)
            elif self.tiles_coo[i].long: quad.set_color(1, 1, 1)
            quad.set_color(*self.color.data["tile"])
    def update_landscape(self):
        x, y = self.perspective_point_x, self.perspective_point_y
        self.triangles[0].points = [0, y,
                                    0, 0,
                                    *self.lines_y[0].points]
        self.triangles[1].points = [self.width, y,
                                    self.width, 0,
                                    *self.lines_y[-1].points]

        self.triangles[2].points = [x, y,
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*0.5, 0),
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*0, 0)]
        self.triangles[3].points = [x, y,
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*0.5, 0),
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*0, 0)]

        self.triangles[4].points = [x, y,
                                    0, y,
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*3, 0)]
        self.triangles[5].points = [x, y,
                                    self.width, y,
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*3, 0)]

        coo = x, y+dp(3)
        h = dp(35)+(self.height-self.perspective_point_y)/3
        self.triangles[6].points = [*coo,
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*10, 0),
                                    0, y+(self.height-self.perspective_point_y)/5,
                                    x/2, y+h - (self.width/2-x)/5]
        self.triangles[7].points = [*coo,
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*10, 0),
                                    self.width, y+(self.height-y)/5,
                                    self.width/2+x/2, y+h + (self.width/2-x)/5]
        #self.perspective_point_x/2*3
        self.triangles[8].points = [*coo,
                                    0, y-1,
                                    self.width, y-1]
    def update_glint(self):
        size = dp(250)
        deca = self.width/3 + self.glint.value/4
        space = size*1.4
        x = self.glint.value - (size+space+deca)
        self.glint.elements[0].points = [
            x+size, 0,
            x+size+deca, self.height,
            x+deca, self.height,
            x, 0,
        ]
        self.glint.elements[1].points = [
            x+size+space, 0,
            x+size+deca+space, self.height,
            x+deca+space, self.height,
            x+space, 0,
        ]
    def update(self, dt):
        time_factor = min(5, dt * self.FPS)
        if self.state_game_has_started:
            if self.first_wait[0] < self.first_wait[1]: self.first_wait[0] += time_factor

        if not self.state_game_over:   # Quand il n'y a pas eu d'accident
            r_x, r_y = self.get_ratios()
            self.offset.y.value += self.offset.y.speed * r_y * time_factor
            spacing_horizontal_tile = self.get_spacing_horizontal_lines()
            if self.offset.y.value > spacing_horizontal_tile:
                quotient, rest = divmod(self.offset.y.value, spacing_horizontal_tile)
                self.offset.y.value = rest
                self.current_y_loop += quotient
                self.generate_tiles_coo()
                if self.state_game_has_started: self.score += 50

            if self.state_game_has_started:   # Quand la partie joue
                if self.Player.mode == 0:
                    self.offset.x.limits = [self.get_spacing_vertical_lines() * (self.nb_vertical_lines / 2 - 0.5) - self.Player.size_[0]/2,
                                            -self.get_spacing_vertical_lines() * (self.nb_vertical_lines / 2 - 0.5) + self.Player.size_[0]/2]
                    self.offset.x.increase_value(r_x * time_factor)
                    self.offset.x.set_bounded_limits()
                elif self.Player.mode in [1, 3]:
                    x = self.Player.pos[0] + self.Player.size_[0] / 2
                    X = round((x - self.width / 2 - self.offset.x.value) / self.get_spacing_vertical_lines())
                    self.offset.x.get = -X * self.get_spacing_vertical_lines()
                    s = self.offset.x.value - self.offset.x.get
                    if s != 0:
                        s = s / abs(s)
                        self.offset.x.direction = -s
                    if self.offset.x.direction != 0:
                        self.offset.x.value += self.offset.x.speed3*self.offset.x.direction
                        if self.offset.x.value*self.offset.x.direction >= self.offset.x.get*self.offset.x.direction:
                            self.offset.x.value = self.offset.x.get
                            self.offset.x.direction = 0
                elif self.Player.mode == 2:
                    self.offset.x.limits = [self.get_spacing_vertical_lines() * (self.nb_vertical_lines / 2 - 1),
                                            -self.get_spacing_vertical_lines() * (self.nb_vertical_lines / 2 - 1)]
                    if self.offset.x.direction != 0:
                        self.offset.x.value += 50*self.offset.x.direction
                        if self.offset.x.value*self.offset.x.direction >= self.offset.x.get*self.offset.x.direction:
                            self.offset.x.value = self.offset.x.get
                            self.offset.x.direction = 0
                    if self.offset.x.set_bounded_limits():
                        self.offset.x.direction = 0


                if self.perspective.x.get_end_wait(time_factor, reset_wait=False):
                    self.perspective_point_x += self.perspective.x.get_actual_speed() * time_factor
                    if abs(self.perspective_point_x - self.width/2) > self.width*self.perspective.x.limit:
                        self.perspective_point_x = self.width/2 + self.width*self.perspective.x.limit*self.perspective.x.direction
                        self.perspective.x.direction *= -1
                        self.perspective.x.wait[0] = 0


        self.update_lines()
        self.update_tiles()
        self.update_landscape()
        self.update_glint()
        if not self.state_game_over: self.Player.update(time_factor)

        if not self.state_game_has_started or self.state_game_over or self.glint.value!=0:
            self.glint.increase_value(time_factor)
            self.glint.get_end_wait(time_factor, reset_value=True)

        if not self.player_on_the_way() and not self.state_game_over:
            self.set_game_over()
        self.offset.y.base_speed

    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.reset_game()
        else:
            self.set_game()

class ProjectApp(App):
    pass

ProjectApp().run()
