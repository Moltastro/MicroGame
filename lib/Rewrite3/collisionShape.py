from .coordinateSystem import Vec2,VectorMapFactory
from typing import Self,TYPE_CHECKING

class Rect:
    def __init__(self,pos:Vec2,size:Vec2) -> None:
        self.pos=pos
        self.size=size
    
    @property
    def end(self):
        return self.pos+self.size
    
    @end.setter
    def end(self,other):
        self.size.set(other-self.pos)
    
    def overlaps(self, square:'Rect') -> bool:
        return not (
            square.pos.x + square.size.x < self.pos.x or
            square.pos.x > self.pos.x + self.size.x or
            square.pos.y + square.size.x < self.pos.y or
            square.pos.y > self.pos.y + self.size.y
        )
    def clone(self):
        return Rect(self.pos.clone(),self.size.clone())
    
    def transform(self,transform:VectorMapFactory):
        clone=self.clone()
        clone.pos=transform.map(self.pos)
        return clone
    
    def clamp(self,clamp_box:"Rect"):
        # Clamp position
        new_x = max(clamp_box.pos.x, min(self.pos.x, clamp_box.pos.x + clamp_box.size.x))
        new_y = max(clamp_box.pos.y, min(self.pos.y, clamp_box.pos.y + clamp_box.size.y))

        # Clamp size so the bbox does not exceed the clamp_box
        new_w = min(self.size.x, (clamp_box.pos.x + clamp_box.size.x) - new_x)-1
        new_h = min(self.size.y, (clamp_box.pos.y + clamp_box.size.y) - new_y)-1

        self.pos = Vec2(new_x, new_y)
        self.size = Vec2(new_w, new_h)
        return self
    def __
    def __repr__(self)-> str:
        return f"BBox: [pos {self.pos}, size {self.size}]"
    
