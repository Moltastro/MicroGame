from dataclasses import dataclass
from typing import Protocol
#from framebuff import FrameBuffer
class Vec2:
  def __init__(self,x,y):
    self.x=x
    self.y=y
  def __add__(self,other):
    return Vec2(self.x+other.x,self.y+other.y)
  def __repr__(self):
    return f"{self.x,self.y}"
  
class DrawCallable(Protocol):
  def __call__(self, fb,pos)->None: ...
    
@dataclass(order=True)
class RenderAction:
  action:DrawCallable
  z:int

class DrawAction:
  def __init__(self,offset,z=0):
    self.offset=offset
    self.z=z

  def build(self,WorldCoordinatePos) ->DrawCallable:
    return RenderAction(lambda fb,pos:self.draw(self.offset+WorldCoordinatePos,fb),self.z)

  def draw(self, pos, fb:'ByteBuffer'):
    raise NotImplementedError
  
  def __lt__(self,other:'DrawAction'):
    return self.z<other.z

class Rectangle(DrawAction):
  def __init__(self, offset, size, z=0):
    super().__init__(offset, z)
    self.size=size

  def draw(self,pos,fb):
    print(f"Drawing rectangle at {pos} with size {self.size}")

    
class Node:
  def __init__(self,pos):
    self.pos=pos
    self.children=set()
  def add_child(self,other:'Node'):
    self.children.add(other)
  def remove_child(self,other:'Node'):
    self.children.discard(other)
  def gatherDrawCalls(self,pos=Vec2(0,0),draw=[]):
    child:'Node'
    for child in self.children:
      child.gatherDrawCalls(pos+self.pos,draw)

class GameObject(Node):
  def __init__(self, pos,sprite:DrawAction):
    super().__init__(pos)
    self.velocity=Vec2(0,0)
    self.debug_visual=True
    self.sprite=sprite

  def gatherDrawCalls(self, pos=Vec2(0, 0), draw:list=[]):
    draw.append(self.sprite.build(self.pos+pos))
    return super().gatherDrawCalls(pos, draw)
  
class Drawable(GameObject):
  def __init__(self, pos:Vec2):
    super().__init__(pos)

  def __call__(self,pos:Vec2):
    self.pos=pos

  def gatherDrawCalls(self, pos=Vec2(0, 0), draw=[]):
    draw.append(Rectangle(pos))
    return super().gatherDrawCalls(pos, draw)


class ImageCompiler:
  def __init__(self):
    self.actions=[]
  def draw(self,fb):
    sortedActions=sorted(self.actions)
    action:RenderAction
    for action in sortedActions:
      action.action(fb,Vec2(0,0))
    self.actions.clear()

def compile_and_draw(root:Node):
  compiler=ImageCompiler()
  root.gatherDrawCalls(draw=compiler.actions)
  print(compiler.actions)
  compiler.draw("")
root=Node(Vec2(0,0))
rectangle=GameObject(Vec2(0,0),Rectangle(Vec2(10,10),Vec2(5,5)))
root.add_child(rectangle)
compile_and_draw(root)
print(rectangle.pos)
rectangle.pos+=Vec2(5,5)
print(rectangle.pos)
compile_and_draw(rectangle)