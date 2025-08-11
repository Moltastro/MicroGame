from .drawable import Drawable
from .viewportTileHandler import *
from .gameHandler import GameHandler
import math
if __name__ == "__main__":
    from typing import Callable

class GameObject():
    """
    Represents an object in the game world that can move and be drawn.

    A GameObject has:
    - a `sprite` (something that can be drawn on the screen),
    - a position (`x`, `y`),
    - a velocity (`velocity_x`, `velocity_y`),
    - and an optional "bounce" behavior.

    It automatically adds itself to the game's list of objects.
    """
    def __init__(self,sprite:Drawable):
        """
        Create a new GameObject.

        Args:
            sprite (Drawable): The visual representation of the object.
        """
        self.sprite=sprite
        self.velocity_x=0
        self.velocity_y=0
        GameHandler.get_instance().game_objects.add(self)
        self.boune=False
        self.on_update=lambda: None

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

    def is_colliding_with(self,gameObject):
        return (self.x < gameObject.x + gameObject.sprite.w and
    self.x + self.sprite.w > gameObject.x and
    self.y < gameObject.y + gameObject.sprite.h and
    self.y + self.sprite.h > gameObject.y)

    def distance_to_object(self,gameObject):
        return self.distance_to_coordinate(gameObject.x,gameObject.y)
    
    def distance_to_coordinate(self,x,y):
        return math.sqrt(abs(self.x-x)**2+abs(self.y-y)**2)
    def update(self):
        
        self.x+=self.velocity_x
        self.y+=self.velocity_y
        if self.boune:
            if self.x+self.sprite.w>SingleFrameBufferDriver.width or self.x<0:
                self.velocity_x=self.velocity_x*-1
            if self.y+self.sprite.h>SingleFrameBufferDriver.height or self.y<0:
                self.velocity_y=self.velocity_y*-1
        if self.on_update:
            self.on_update()
        self.sprite.update()
    
    def __str__(self):
        return self.sprite.__str__()

