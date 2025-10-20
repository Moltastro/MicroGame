from typing import Protocol
from .coordinateSystem import *
from .byteBuffer import ByteBuffer
from .util import rgb,timed_function
class DrawCallable(Protocol):
    def __call__(self, fb, pos) -> None: ...

class RenderAction:
  def __init__(self,action, size, z) -> None:
    self.action:DrawCallable=action
    self.size:Vec2=size
    self.z:int=z
  
  def __lt__(self,other):
     return self.z<other.z

class DrawAction:
  def __init__(self,offset,z=0):
    self.offset=offset
    self.z=z

  @property
  def size(self):
     raise NotImplementedError
  
  @size.setter
  def size(self,new):
     raise NotImplementedError
  @timed_function
  def build(self,WorldCoordinatePos) ->RenderAction:
    return RenderAction(lambda fb,pos:timed_function(self.draw(self.offset+WorldCoordinatePos-pos,fb)),self.size,self.z)

  def draw(self, pos, fb:ByteBuffer):
    raise NotImplementedError

class Rectangle(DrawAction):
  def __init__(self, offset, size, z=0):
    super().__init__(offset, z)
    self._size=size

  @property
  def size(self):
     return self._size
  
  @size.setter
  def size(self,other):
     self._size=other

  def draw(self,pos,fb):
    fb.rect(*pos,*self.size,rgb(45, 226, 136))
""" 

class Translated(DrawAction):
    def __init__(self, wrapped: DrawAction, delta: Vec2):
        super().__init__()
        self.wrapped = wrapped
        self.delta = delta

    def get_size(self):
        return self.wrapped.get_size()

    def build(self, world_pos: Vec2) -> RenderAction:
        return self.wrapped.build(world_pos + self.delta) """