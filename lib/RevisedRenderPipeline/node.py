from .coordinateSystem import *
from .drawable import *
class Node:
  root:'Node'=None
  def __init__(self):
    self.children=set()
    self.parent:Node=None
    if Node.root!=None:
      self.parent=Node.root

  def remove_me(self):
    self.parent.remove_child(self)

  def reparent(self,other:'Node'):
    self.children.add(other)
    if other.parent!=None:
      other.parent.remove_child(other)
    other.parent=self
  def remove_child(self,other:'Node'):
    self.children.discard(other)
  def gatherDrawCalls(self,pos=Vec2(0,0),draw=[]):
    child:'Node'
    for child in self.children:
      child.gatherDrawCalls(pos,draw)

class Node2D(Node):
  def __init__(self,pos:Vec2):
    super().__init__()
    self.pos:Vec2=pos
  def gatherDrawCalls(self,pos=Vec2(0,0),draw=[]):
    child:'Node'
    for child in self.children:
      child.gatherDrawCalls(pos+self.pos,draw)

class GameObject(Node2D):
  def __init__(self, pos,sprite:DrawAction):
    super().__init__(pos)
    self.velocity=Vec2(0,0)
    self.debug_visual=True
    self.sprite=sprite
    self.collision_size=Vec2(0,0)
    self.debug_collision=True

  def gatherDrawCalls(self, pos=Vec2(0, 0), draw:list=[]):
    self.pos+=self.velocity
    draw.append(self.sprite.build(self.pos+pos))
    if self.debug_collision:
      draw.append(Rectangle(Vec2(0,0),self.collision_size).build(pos))
    return super().gatherDrawCalls(pos, draw)
  
