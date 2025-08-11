from .viewportTileHandler import singleViewPort
from .taskmanager import TaskManager
from .drawable import *
from time import sleep,ticks_ms,ticks_diff

class GameHandler():
    _instance=None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self) -> None:
        if hasattr(self, '_initialized'):
            return
        self.game_objects=set()
        
        self.last_time=ticks_ms()
        self.taskmanager=TaskManager()
        self.fps=30
        self.backgroundColor=rgb(255,255,255)

    @property
    def fps(self):
        return 1/self._frame_time
    
    @fps.setter
    def fps(self,other):
        self._frame_time=1/other
        self.taskmanager.dt=1/other

    def update(self):
        
        for object in self.game_objects:
            debug(object)
            object.update()
        self.taskmanager.update()
    
    def draw(self):
        singleViewPort.push_changes()
        sleep(0.016)

    def run(self):
        frame_start = ticks_ms()
        self.update()
        self.draw()

        frame_end = ticks_ms()
        elapsed = ticks_diff(frame_end,frame_start)/1000
        if elapsed< self._frame_time:
            sleep(self._frame_time-elapsed)

game=GameHandler()