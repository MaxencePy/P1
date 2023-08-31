

def transform(self, x, y):
    #return self.transform_2D(x, y)
    return self.transform_perspective(x, y)
def reverse_transform(self, x, y):
    #return self.transform_2D(x, y)
    return self.reverse_transform_perspective(x, y)
def transform_2D(self, x, y):
    return x, y
def transform_perspective(self, x, y):
    lin_y = y * self.perspective_point_y / self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor_y = (diff_y / self.perspective_point_y)**5  # 1 when diff_y == self.perspective_point_y / 0 when diff_y = 0
    # factor_y = pow(factor_y, 4)

    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = (1 - factor_y) * self.perspective_point_y

    return tr_x, tr_y
def reverse_transform_perspective(self, x, y):
    factor_y = 1 - y/self.perspective_point_y
    diff_x = (x - self.perspective_point_x)/factor_y

    diff_y = (factor_y**(1/4))*self.perspective_point_y
    lin_y = self.perspective_point_y - diff_y

    b_x = diff_x + self.perspective_point_x
    b_y = lin_y/self.perspective_point_y*self.height

    return b_x, b_y

