from RevisedMicroGame.gameHandler import GameHandler
from RevisedMicroGame.taskManager import ScriptScheduler
from RevisedMicroGame.tileManager import TileManager
from RevisedMicroGame.coordinateSystem import VectorMapFactory
from RevisedMicroGame.displayDrivers import WaveShareDisplay
WIDTH=240
HEIGHT=300
vectorMap=VectorMapFactory(lambda x: x+WIDTH//2, lambda y: -y+HEIGHT//2)
Game=GameHandler(ScriptScheduler(),TileManager(WaveShareDisplay(),2,4,1),vectorMap)