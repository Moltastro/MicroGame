from RevisedMicroGame.gameHandler import GameHandler
from RevisedMicroGame.taskManager import ScriptScheduler
from RevisedMicroGame.tileManager import VariableTileManager
from RevisedMicroGame.coordinateSystem import VectorMapFactory
from RevisedMicroGame.displayDrivers import WaveShareDisplay
from RevisedMicroGame.gameObject import GameObject
from RevisedMicroGame.drawable import *
from RevisedMicroGame.util import rgb
from random import randint
from time import ticks_ms,ticks_diff
WIDTH=240
HEIGHT=300
vectorMap=VectorMapFactory(lambda x: x+WIDTH//2, lambda y: -y+HEIGHT//2)
Game=GameHandler(ScriptScheduler(),VariableTileManager(WaveShareDisplay(),2,4,1),vectorMap)
GameObject.bind_game_handler(Game)
for i in range(20):
    rect=GameObject(Rectangle(0,0,40,40,rgb(34, 182, 59)))
    rect.velocity.speed=40
    rect.velocity.angle=-randint(0,360)
    rect.velocity.speed=40
while True:
    start=ticks_ms()
    Game.update()
    elapsed=ticks_diff(ticks_ms(),start)
    print(f"Frame took {elapsed/1000} s")