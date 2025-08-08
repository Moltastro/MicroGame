from drawable import Drawable
from viewportTileHandler import *
from game import Game
class GameObject():
    def __init__(self,sprite:Drawable):
        self.sprite=sprite
        self.velocity_x=0
        self.velocity_y=0
        Game.get_instance().game_objects.add(self)

    @property
    def x(self):
        return self.sprite.x

    @x.setter
    def x(self, value):
        self.sprite.x = value

    @property
    def y(self):
        return self.sprite.y

    @y.setter
    def y(self, value):
        self.sprite.y = value
    
    def update(self):
        self.x+=self.velocity_x
        self.y+=self.velocity_y
        self.sprite.update()
    
    def __str__(self):
        return self.sprite.__str__()

