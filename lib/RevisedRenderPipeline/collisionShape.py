from .coordinateSystem import Vec2

class AABB:
  def __init__(self,pos:Vec2,size:Vec2) -> None:
    self.pos=pos
    self.size=size
  def right(self): return self.pos.x + self.size.x
  def bottom(self): return self.pos.y + self.size.y
  def overlaps(self,other:'AABB'):
    return not (
        self.right() <= other.pos.x or
        self.pos.x >= other.right() or
        self.bottom() <= other.pos.y or
        self.pos.y >= other.bottom()
    )
  def __str__(self):
    return self.__repr__()
  def __repr__(self) -> str:
    return f"[{self.pos},{self.size}]"