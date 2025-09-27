from .coordinateSystem import *
from .util import *
from .collisionShape import *
from .taskManager import ScriptScheduler
from time import sleep,ticks_ms,ticks_diff
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .gameObject import GameObject
    from .tileManager import TileManager
    from .coordinateSystem import VectorMapFactory

class GameHandler():
    def __init__(self, taskmanager:ScriptScheduler, tileHandler:'TileManager', coordinateSystem:'VectorMapFactory'=VectorMapFactory()) -> None:
        self.game_objects=set()
        self.taskmanager=taskmanager
        self.tileHandler=tileHandler
        self.fps=30
        self.backgroundColor=rgb(255,255,255)
        self.stopped=False
        self.coordinateSystem=coordinateSystem

    def update(self):
        object:'GameObject'
        for object in self.game_objects:
            object.update(1/self.fps,self.tileHandler,self.coordinateSystem)
    
    def add(self,gameObject:'GameObject'):
        self.game_objects.add(gameObject)