class Point:
    def __init__(self, x=False, y=False):
        self.x, self.y = x, y
        self.coo = [self.x, self.y]
class Data:
    def __init__(self, **kwargs):
        self.data = kwargs
class Value:
    def __init__(self, value=False, size=False, direction=1, speed=False, speed2=False, speed3=1, limit=False, limits=[], wait=False, initial_wait=0,
                 elements=[], data={}):
        self.value = value
        self.size = size
        self.direction = direction
        self.base_speed, self.speed, self.speed2, self.speed3 = speed, speed, speed2, speed3
        self.add_speed = 0
        self.limit, self.limits = limit, limits
        self.wait = [initial_wait, wait]
        self.mode = 0
        self.get = self.value
        self.elements = elements
        self.data = data
    def get_end_wait(self, factor, reset_wait=True, reset_value=False):
        if self.wait[0] + 1 * factor >= self.wait[1]:
            if reset_wait: self.wait[0] = 0
            if reset_value: self.value = 0
            return True
        else: self.wait[0] += 1 * factor
    def get_actual_speed(self):
        return self.speed*self.direction
    def get_limit(self):
        if self.limit: return self.limit
        else: return self.limits[0 if self.direction == 1 else 1]
    def get_limits(self, value):
        return self.limits

    def set_bounded_value(self, min_=float("+inf"), max_=float("-inf")):
        value = self.value
        self.value = min(max_, max(min_, self.value))
        return value != self.value
    def get_bounded_limits(self, value, factor=1):
        min_, max_ = min(self.limits)*factor, max(self.limits)*factor
        return min(max_, max(min_, value))
    def set_bounded_limits(self, factor=1):
        min_, max_ = min(self.limits)*factor, max(self.limits)*factor
        self.value =  min(max_, max(min_, self.value))
    def increase_value(self, factor):
        self.value += self.get_actual_speed()*factor