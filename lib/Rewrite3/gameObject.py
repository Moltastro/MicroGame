from .coordinateSystem import *
from .collisionShape import Rect
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .tileManager import TileManager
    from .drawable import Drawable
    from .gameHandler import GameHandler
    from .coordinateSystem import VectorMapFactory

DEBUG = False

class GameObject:
    gameHandler=None
    def __init__(self,x,y,sprite:Drawable):
        self.sprite=sprite
        self.collider=sprite.Rect
        self.pos=Vec2(x,y,self._on_pos_changed)
        self.velocity=Vec2(0, 0)
        if DEBUG: print(f"[GameObject] Created with sprites {sprite}")
        if GameObject.gameHandler:
            GameObject.gameHandler.add(self)
        self._on_pos_changed()
    def is_colliding(self,other:'GameObject'):
        return self.collider.overlaps(other.collider)


    def _remove(self):
        self.sprite.remove()
    def _on_pos_changed(self):
        self.sprite.pos.set(self.pos)
        self.collider.pos=self.pos-self.collider.size/2

    def update(self,delta:float,tileHandler:'TileManager',coordinateSystem:'VectorMapFactory'):
        if DEBUG: print(f"[GameObject] Updating pos={self.pos} vel={self.velocity} delta={delta}")
        self.pos+=self.velocity*delta
        if DEBUG: print(f"[GAMEOBJECT] pos after {self.pos}")
        self.sprite.update(tileHandler,coordinateSystem)

    @classmethod
    def bind_game_handler(cls,handler:'GameHandler'):
        if DEBUG: print(f"[GameObject] Bound game handler {handler}")
        cls.gameHandler=handler

    def __repr__(self):
        return f"GameObject(pos={self.pos}, velocity={self.velocity}, sprite={self.sprite})"


