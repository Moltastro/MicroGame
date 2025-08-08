from viewportTileHandler import *
import framebuf
from util import *
class Drawable:
    def __init__(self, x, y, w, h, z=0):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.z = z
        self._old_tiles = set()
        self.has_moved=True
        self.old_top_left = None
        self.old_bottom_right = None
        
    
    @property
    def bbox(self):
        return (self.x,self.y,self.w,self.h)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self,val):
        if val !=self._x:
            self._x=val
            self.has_moved = True

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self,val):
        if val!=self._y:
            self._y=val
            self.has_moved = True
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self,val):
        if val!=self._w:
            self._w=val
            self.has_moved = True
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self,val):
        if val!=self._h:
            self._h=val
            self.has_moved = True
    
    def update(self):
        if self.has_moved:
            view=Viewport.get_instance()
            if (self.old_top_left and self.old_bottom_right):
                view.remove_drawable_in_tiles_and_mark_dirty(self)
            
            self.old_top_left,self.old_bottom_right=view.store_drawable_in_tiles_and_mark_dirty(self)
            self.has_moved=False

    def draw_into(self, fb, relative_x, relative_y):
        """Override in subclass: draw shape into given FrameBuffer"""
        pass

    def framebuffer_relative_coordinates(self,buf_x,buf_y):
        #Returns coordinates relative to the framebuffer coordinates
        return self.x-buf_x,self.y-buf_y
    
    def __str__(self) -> str:
        return f"pos: ({self.x},{self.y})"

class Rectangle(Drawable):
    def __init__(self, x, y, w, h, z=0, color=rgb(255,0,0)):
        super().__init__(x,y,w,h,z)
        self.color=color
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x,relative_y):
        fb.rect(relative_x, relative_y, self.w, self.h,self.color)

class Ellipse(Drawable):
    def __init__(self, x, y, diameter_x, diameter_y, z=0, color=rgb(0,255,0)):
        super().__init__(x, y, diameter_x, diameter_y, z)
        self.color=color
    
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        fb.ellipse(relative_x-self.w//2,relative_y-self.h//2,self.w//2,self.h//2,self.color,True)