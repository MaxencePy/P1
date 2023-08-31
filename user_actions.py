from kivy.uix.relativelayout import RelativeLayout


def on_touch_down(self, touch):
    """if not self.state_game_over and self.state_game_has_started:
        self.offset.direction_x = 1 if touch.x < self.width / 2 else -1
    return super(RelativeLayout, self).on_touch_down(touch)"""
    if self.first_wait[0] >= self.first_wait[1] and self.Player.mode in [0, 2]:
        if touch.x < self.width / 2:
            self.offset.x.get = self.offset.x.value + self.get_spacing_vertical_lines()
            self.offset.x.direction = 1
        else:
            self.offset.x.get = self.offset.x.value - self.get_spacing_vertical_lines()
            self.offset.x.direction = -1
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    """if self.Player.mode in [0, 2]:
        self.offset.x.direction = 1 if touch.x < self.width / 2 else -1
        if touch.x < self.width / 2 and self.offset.x.direction == 1:
            self.offset.x.direction = 0
        elif self.offset.x.direction == -1:
            self.offset.x.direction = 0"""
    if self.Player.mode != 2:
        if touch.x < self.width / 2 and self.offset.x.direction == 1:
            self.offset.x.direction = 0
        elif self.offset.x.direction == -1: self.offset.x.direction = 0


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if self.first_wait[0] >= self.first_wait[1] and self.Player.mode in [0, 2]:
        if keycode[1] == 'left':
            self.offset.x.get = self.offset.x.value + self.get_spacing_vertical_lines()
            self.offset.x.direction = 1
        elif keycode[1] == 'right':
            self.offset.x.get = self.offset.x.value - self.get_spacing_vertical_lines()
            self.offset.x.direction = -1
    return True
def on_keyboard_up(self, keyboard, keycode):
    if keycode[1] == 'left' and self.offset.x.direction == 1:self.offset.x.direction = 0
    if keycode[1] == 'right' and self.offset.x.direction == -1: self.offset.x.direction = 0
    return True
