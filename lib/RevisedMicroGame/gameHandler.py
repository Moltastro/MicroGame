from coordinateSystem import *
from util import *
from gameObject import GameObject
from tileHandler import TileHandler
from collisionShape import *
from taskManager import ScriptScheduler
from time import sleep,ticks_ms,ticks_diff

class GameHandler():
    def __init__(self, taskmanager:ScriptScheduler, tileHandler:TileHandler, coordinateSystem:VectorMapFactory=VectorMapFactory()) -> None:
        self.game_objects=set()
        self.taskmanager=taskmanager
        self.tileHandler=tileHandler
        self.fps=30
        self.backgroundColor=rgb(255,255,255)
        self.stopped=False
        self.coordinateSystem=coordinateSystem

    def update(self):
        object:GameObject
        for object in self.game_objects:
            object.update(1/self.fps,self.tileHandler,self.coordinateSystem)
    