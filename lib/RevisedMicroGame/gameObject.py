from coordinateSystem import *
from tileHandler import TileHandler
from drawable import Drawable
class GameObject:
    def __init__(self,sprite:Drawable):
        self.sprite=sprite
        self.pos=sprite.bbox.pos    
        self.velocity=Vector2(0, 0)
    
    def update(self,delta:float,tileHandler:TileHandler,coordinateSystem:VectorMapFactory):
        self.pos.x += self.velocity.x*delta
        self.pos.y += self.velocity.y*delta
        self.sprite.update(tileHandler,coordinateSystem)
    

