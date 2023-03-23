import arcade
from math import sqrt

class PlayerCar(arcade.Sprite):
    def __init__(self, filename: str = None, scale: float = 1,center_x=5, center_y=5):
        super().__init__(filename, scale,center_x=center_x,center_y=center_y)
        self.meow = 'meow'
    @property
    def speed(self):
        # return euclidian distance * current fps (60 default)
        return int(sqrt(pow(self.change_x, 2) + pow(self.change_y, 2)) * 60)