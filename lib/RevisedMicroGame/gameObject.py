from .coordinateSystem import *
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .tileManager import TileManager
    from .drawable import Drawable
    from .gameHandler import GameHandler
    from .coordinateSystem import VectorMapFactory

class GameObject:
    gameHandler=None
    def __init__(self,sprite:'Drawable'):
        self.sprite=sprite
        self.pos=sprite.bbox.pos    
        self.velocity=Vec2(0, 0)
        if GameObject.gameHandler:
            GameObject.gameHandler.add(self)
    
    def update(self,delta:float,tileHandler:'TileManager',coordinateSystem:'VectorMapFactory'):
        self.pos.x += self.velocity.x*delta
        self.pos.y += self.velocity.y*delta
        self.sprite.update(tileHandler,coordinateSystem)

    @classmethod
    def bind_game_handler(cls,handler:'GameHandler'):
        cls.gameHandler=handler


