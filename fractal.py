import math 

class Fractal:
    def __init__(self, item_type, direction):
        self.init_params(item_type, direction)
        self.init_maths()

    def init_params(self, item_type, direction):
        self.limit = 2
        self.color = 'r'
        self.item_type = item_type
        self.direction = direction

    def init_maths(self):
        if self.item_type == 0:
            n1, n2, n3 = 3, 4, 5
        elif self.item_type == 1:
            n1, n2, n3 = 5, 12, 13
        elif self.item_type == 2:
            n1, n2, n3 = 8, 15, 17
        elif self.item_type == 3:
            n1, n2, n3 = 16, 25, 29
        else:
            raise Exception('bad selector')

        if self.direction == 0:
            self.cos_theta   = n2 / n3
            self.sin_theta   = n1 / n3
        elif self.direction == 1:
            self.cos_theta   = n1 / n3
            self.sin_theta   = n2 / n3

        self.theta_left  = math.acos(self.sin_theta) * 180 / math.pi
        self.theta_right = math.acos(self.sin_theta) * 180 / math.pi

    def compute_next_left(self, item_x, item_y, item_size):
        x = item_x
        y = item_y - item_size * self.cos_theta
        r = item_size * self.cos_theta
        return x, y, r

    def compute_next_right(self, item_x, item_y, item_size):
        x = item_size * (1 - self.sin_theta) + item_x
        y = item_y - item_size * self.sin_theta
        r = item_size * self.sin_theta
        return x, y, r
