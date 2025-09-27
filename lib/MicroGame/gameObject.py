from ..drawable import Drawable
from .viewport.TileHandler import *
from ..gameHandler import GameHandler
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
    import math

    def step_in_direction(self,ang,px):
        self.x,self.y=GameObject.step_relative_to(self.x,self.y,ang,px)
    @staticmethod
    def step_relative_to(x, y, ang, px):
        """
        Compute a new point px units away from (x, y) at angle ang (in degrees),
        using screen coordinates (0° = right, 90° = down).

        Parameters:
            x (float): starting x coordinate
            y (float): starting y coordinate
            ang (float): angle of movement (degrees, can be any float)
            px (float): distance to move

        Returns:
            (float, float): new coordinates (x2, y2)
        """
        rad = math.radians(ang)
        x2 = x + px * math.cos(rad)
        y2 = y + px * math.sin(rad)  # positive sin goes down
        return x2, y2

    def is_visible(self):
        """
        Check if entity is at least partially visible within screen bounds.

        Parameters:
            screen_width (int or float): width of the screen
            screen_height (int or float): height of the screen

        Returns:
            bool: True if visible, False otherwise
        """
        # Object bounds
        left = self.x
        top = self.y
        right = self.x + self.sprite.w
        bottom = self.y + self.sprite.h
        width=singleViewPort.width
        height=singleViewPort.height
        # Screen bounds
        screen_left =-width/2
        screen_top = height/2
        screen_right = width/2
        screen_bottom = -height/2
        # Check overlap (axis-aligned bounding box intersection)
        return not (right <= screen_left or
                    left >= screen_right or
                    bottom >= screen_top or 
                    top <= screen_bottom) 

    def delete(self):
        self.x,self.y=singleViewPort.height*2,singleViewPort.width*2
        game=GameHandler.get_instance()
        def delete():
            yield from game.taskmanager.repeat(2,lambda:None)
            game.game_objects.remove(self)
        game.taskmanager.add(delete)

    def set_speed_in_direction(self,ang,vel):
        """
        Set velocity vector so that its magnitude is vel
        in direction ang (degrees, screen convention).

        Parameters:
            ang (float): direction in degrees (0° = right, 90° = down)
            vel (float): speed magnitude
        """
        rad = math.radians(ang)
        self.velocity_x = vel * math.cos(rad)
        self.velocity_y = vel * math.sin(rad)  # positive = down
        singleViewPort.height
    
    def __str__(self):
        return self.sprite.__str__()

