from viewportTileHandler import Viewport
from gameObject import GameObject
from drawable import *
from time import sleep
class Game():
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
    
    def update(self):
        for object in self.game_objects:
            object.update()
    
    def draw(self):
        Viewport.get_instance().push_changes()
        sleep(0.016)

if __name__ == "__main__":
    game=Game.get_instance()
    rect=GameObject(Rectangle(50,50,50,50))
    rect.velocity_x=5
    while True:
        game.update()
        game.draw()

        