from RevisedMicroGame.gameHandler import *
from RevisedMicroGame.displayInterface import DebugDispay
from RevisedMicroGame.tileManager import TileManager
from RevisedMicroGame.gameObject import GameObject
import time  # <-- add this import

Game=GameHandler(ScriptScheduler(),TileManager(DebugDispay(16,16),1,1),VectorMapFactory())
GameObject.bind_game_handler(Game)
GameObject(Drawa)
for i in range(10):
    start = time.ticks_ms()
    Game.update()
    elapsed = time.ticks_diff(time.ticks_ms(), start)