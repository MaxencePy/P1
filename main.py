from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Rectangle, Triangle
from kivy.properties import Clock
from kivy.core.window import Window
from kivy import platform
from kivy.lang import Builder
from kivy.graphics.texture import Texture
import random

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

class Player(RelativeLayout):
    color = (.2, 0, .3)
    base_size = (60, 100)
    def __init__(self, main_widget, **kwargs): ###
        super().__init__(**kwargs)
        self.MainWidget = main_widget
        with self.canvas:
            Color(*self.color)
            #self.Rectangle = Image(source="images/FP.bmp", allow_stretch=True)
            self.Rectangle = Rectangle()
            #Color(1, 1, 1)
    def init(self):
        self.MainWidget.add_widget(self)

    def get_points(self):
        q = 14
        size = self.Rectangle.size

        return [coo for coo in[
                (self.pos[0] + size[0]/2, self.pos[1] + self.MainWidget.get_spacing_horizontal_lines()),
                (self.pos[0] + size[0] / 2 + size[0] / q, self.pos[1]),
                (self.pos[0] + size[0] / 2 - size[0] / q, self.pos[1])
                ]]

    def update(self):
        r_x, r_y = self.MainWidget.get_ratios()
        size = [self.base_size[0]*r_x, self.base_size[1]*r_y]
        self.Rectangle.size = size
        self.pos = ((self.MainWidget.width-self.Rectangle.size[0])/2, 20)

class MenuWidget(Widget):
    pass
class MainWidget(RelativeLayout):
    menu_widget = ObjectProperty(None)
    triangles = []
    menu_title, menu_button_title = StringProperty("P   A   U   C   H   O   T"), StringProperty("START")
    perspective_point_x, perspective_point_y = NumericProperty(0), NumericProperty(0)
    speed_perspective_x, speed_perspective_y = .7, 0
    direction_perspective = [1, 1]
    limit_perspective_x = 0.1

    line_color, tile_color = (.7, .1, .5), (.7, .1, .5)
    tile_color2 = (1, 1, 1)
    nb_horizontal_lines, nb_vertical_lines = 9, 10-2
    spacing_horizontal_lines, spacing_vertical_lines = .1, .3
    lines_x, lines_y = [], []
    current_offset_x, current_offset_y = 0, 0
    SPEED_X, SPEED_Y = 22, 3.7
    direction_x = 0

    nb_tiles = nb_horizontal_lines * 2
    tiles, tiles_coo = [], [(0, i) for i in range(int(nb_horizontal_lines*1.5))]
    current_y_loop, current_front_x = 0, 0

    state_game_over = False
    state_game_has_started = False

    FPS = 60
    def __init__(self, **kwargs): ###
        super().__init__(**kwargs) # MainWidget, self

        self.Player = Player(self)

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        self.init_lines()
        self.init_tiles()
        self.Player.init()
        self.generate_tiles_coo()
        #self.size_hint = (None, None)
        Clock.schedule_interval(self.update, 1.0 / self.FPS)

    def reset_game(self):
        self.current_y_loop, self.current_offset_y, self.current_offset_x, self.current_front_x = 0, 0, 0, 0
        self.tiles_coo = [(0, i) for i in range(int(self.nb_horizontal_lines*2))]
        self.generate_tiles_coo()
        self.state_game_over = False

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard.unbind(on_key_up=self.on_keyboard_up)
        self._keyboard = None
    @staticmethod
    def is_desktop():
        return platform in ('linux', 'win', 'macosx')

    def init_lines(self):
        with self.canvas:
            Color(*self.line_color)
            self.lines_y = [Line(width=0.5) for _ in range(self.nb_vertical_lines)]
            self.lines_x = [Line(width=0.5) for _ in range(self.nb_horizontal_lines)]
    def init_tiles(self):
        with self.canvas:
            Color(*self.tile_color)
            self.tiles = [Quad() for _ in range(self.nb_tiles)]
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

    def generate_tiles_coo(self):
        for i in reversed(range(len(self.tiles_coo))):
            ti_x, ti_y = self.tiles_coo[i]
            if ti_y < self.current_y_loop:
                del self.tiles_coo[i]
        last_y = self.tiles_coo[-1][1]+1 if len(self.tiles_coo) else 0
        for _ in range(len(self.tiles_coo), self.nb_tiles):
            r = random.randint(-1 if self.current_front_x > -self.nb_vertical_lines/2 + 1 else 0,
                               1 if self.current_front_x < self.nb_vertical_lines/2 - 1 else 0)
            self.tiles_coo.append((self.current_front_x, last_y))
            if r != 0:
                last_y += 1
                self.tiles_coo.append((self.current_front_x, last_y))
                self.tiles_coo.append((self.current_front_x+r, last_y))
                #self.tiles_coo.append((self.current_front_x+r, last_y))
                self.current_front_x += r
            last_y += 1
    def get_ratios(self):
        return self.width/900, self.height/400

    def get_spacing_vertical_lines(self):
        return self.width*self.spacing_vertical_lines
    def get_spacing_horizontal_lines(self):
        return self.height*self.spacing_horizontal_lines
    def get_line_x_from_index(self, i):
        i += self.nb_vertical_lines / 2 - 1
        spacing_lines_y = self.get_spacing_vertical_lines()
        X = (self.width - spacing_lines_y * (self.nb_vertical_lines - 1)) / 2 + self.current_offset_x
        return int(X + spacing_lines_y*i)
    def get_line_y_from_index(self, i):
        spacing_lines_x = self.get_spacing_horizontal_lines()
        return int(spacing_lines_x*i - self.current_offset_y)
    def get_tile_coo(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x, y = self.get_line_x_from_index(ti_x), self.get_line_y_from_index(ti_y)
        return x, y
    def player_on_the_way(self):
        for x, y in self.Player.get_points():
            x, y = self.reverse_transform(x, y)
            X = round((x-self.width/2 - self.current_offset_x)/self.get_spacing_vertical_lines())
            Y = int((y + self.current_offset_y)/self.get_spacing_horizontal_lines() + self.current_y_loop)
            if (X, Y) in self.tiles_coo:
                return True

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
        for i, tile in enumerate(self.tiles):
            ti_x, ti_y = self.tiles_coo[i]
            xmin, ymin = self.get_tile_coo(ti_x, ti_y)
            xmax, ymax = self.get_tile_coo(ti_x + 1, ti_y + 1)
            tile.points = [*self.transform(xmin, ymin), *self.transform(xmin, ymax),
                                *self.transform(xmax, ymax), *self.transform(xmax, ymin)]
        self.triangles[0].points = [0, self.perspective_point_y,
                                    0, 0,
                                    *self.lines_y[0].points]
        self.triangles[1].points = [self.width, self.perspective_point_y,
                                    self.width, 0,
                                    *self.lines_y[-1].points]

        self.triangles[2].points = [self.perspective_point_x, self.perspective_point_y,
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*0.5, 0),
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*0, 0)]
        self.triangles[3].points = [self.perspective_point_x, self.perspective_point_y,
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*0.5, 0),
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*0, 0)]

        self.triangles[4].points = [self.perspective_point_x, self.perspective_point_y,
                                    0, self.perspective_point_y,
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*3, 0)]
        self.triangles[5].points = [self.perspective_point_x, self.perspective_point_y,
                                    self.width, self.perspective_point_y,
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*3, 0)]

        coo = self.perspective_point_x, self.perspective_point_y+3
        self.triangles[6].points = [*coo,
                                    *(self.lines_y[0].points[0]-self.get_spacing_vertical_lines()*10, 0),
                                    0, self.perspective_point_y+(self.height-self.perspective_point_y)/5,
                                    self.perspective_point_x/2, self.perspective_point_y+(self.height-self.perspective_point_y)/2]
        self.triangles[7].points = [*coo,
                                    *(self.lines_y[-1].points[0]+self.get_spacing_vertical_lines()*10, 0),
                                    self.width, self.perspective_point_y+(self.height-self.perspective_point_y)/5,
                                    self.perspective_point_x/2*3, self.perspective_point_y+(self.height-self.perspective_point_y)/2]
        self.triangles[8].points = [*coo,
                                    0, self.perspective_point_y-1,
                                    self.width, self.perspective_point_y-1]
    def update(self, dt):
        time_factor = dt * self.FPS

        #self.perspective_point_y -= 0.1*time_factor
        #self.perspective_point_x += 0.1*time_factor
        if not self.state_game_over and self.state_game_has_started:
            r_x, r_y = self.get_ratios()
            self.current_offset_y += self.SPEED_Y * r_y * time_factor
            spacing_horizontal_tile = self.get_spacing_horizontal_lines()
            if self.current_offset_y > spacing_horizontal_tile:
                quotient, rest = divmod(self.current_offset_y, spacing_horizontal_tile)
                self.current_offset_y = rest
                self.current_y_loop += quotient
                self.generate_tiles_coo()
            self.current_offset_x += self.SPEED_X * r_x * self.direction_x * time_factor
            self.current_offset_x = min(self.get_spacing_vertical_lines() * (self.nb_vertical_lines / 2 - 0.5) - self.Player.Rectangle.size[0]/2, self.current_offset_x)
            self.current_offset_x = max(-self.get_spacing_vertical_lines() * (self.nb_vertical_lines / 2 - 0.5) + self.Player.Rectangle.size[0]/2, self.current_offset_x)

        self.update_lines()
        self.update_tiles()
        self.Player.update()

        self.perspective_point_x += self.speed_perspective_x*self.direction_perspective[0]
        if abs(self.perspective_point_x - self.width/2) > self.width*self.limit_perspective_x:
            self.perspective_point_x = self.width/2 + self.width*self.limit_perspective_x*self.direction_perspective[0]
            self.direction_perspective[0] *= -1



        if not self.player_on_the_way() and not self.state_game_over:
            self.state_game_over = True
            self.menu_widget.opacity = 1
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "RESTART"

    def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def reverse_transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.reverse_transform_perspective(x, y)

    def transform_2D(self, x, y):
        return x, y

    def transform_perspective(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = (
                               diff_y / self.perspective_point_y)**5  # 1 when diff_y == self.perspective_point_y / 0 when diff_y = 0
        # factor_y = pow(factor_y, 4)

        tr_x = self.perspective_point_x + diff_x * factor_y
        tr_y = (1 - factor_y) * self.perspective_point_y

        return tr_x, tr_y

    def reverse_transform_perspective(self, x, y):
        factor_y = 1 - y / self.perspective_point_y
        diff_x = (x - self.perspective_point_x) / factor_y

        diff_y = (factor_y**(1 / 4)) * self.perspective_point_y
        lin_y = self.perspective_point_y - diff_y

        b_x = diff_x + self.perspective_point_x
        b_y = lin_y / self.perspective_point_y * self.height

        return b_x, b_y
    def on_menu_button_pressed(self):
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0

    def on_touch_down(self, touch):
        if not self.state_game_over and self.state_game_has_started:
            self.direction_x = 1 if touch.x < self.width / 2 else -1
        return super(RelativeLayout, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        self.direction_x = 1 if touch.x < self.width / 2 else -1
        if touch.x < self.width / 2 and self.direction_x == 1:
            self.direction_x = 0
        elif self.direction_x == -1:
            self.direction_x = 0

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.direction_x = 1
        elif keycode[1] == 'right':
            self.direction_x = -1
        return True

    def on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == 'left' and self.direction_x == 1: self.direction_x = 0
        if keycode[1] == 'right' and self.direction_x == -1: self.direction_x = 0
        return True

class GalaxyApp(App):
    pass

GalaxyApp().run()