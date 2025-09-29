from .coordinateSystem import *
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .tileManager import TileManager
    from .drawable import Drawable
    from .gameHandler import GameHandler
    from .coordinateSystem import VectorMapFactory

DEBUG = False

class GameObject:
    gameHandler=None
    def __init__(self,sprite:'Drawable'):
        self.sprite=sprite
        self.pos=sprite.bbox.pos    
        self.velocity=Vec2(0, 0)
        if DEBUG: print(f"[GameObject] Created with sprite {sprite}")
        if GameObject.gameHandler:
            GameObject.gameHandler.add(self)
    
    @property
    def pos(self):
        return self.sprite.bbox.pos

    @pos.setter
    def pos(self,other:Vec2):
        self.sprite.bbox.pos.set(other)

    def update(self,delta:float,tileHandler:'TileManager',coordinateSystem:'VectorMapFactory'):
        if DEBUG: print(f"[GameObject] Updating pos={self.pos} vel={self.velocity} delta={delta}")
        self.pos.x += self.velocity.x*delta
        self.pos.y += self.velocity.y*delta
        self.sprite.update(tileHandler,coordinateSystem)

    @classmethod
    def bind_game_handler(cls,handler:'GameHandler'):
        if DEBUG: print(f"[GameObject] Bound game handler {handler}")
        cls.gameHandler=handler

    def __repr__(self):
        return f"GameObject(pos={self.pos}, velocity={self.velocity}, sprite={self.sprite})"


