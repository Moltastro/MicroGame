from RevisedMicroGame.gameHandler import GameHandler
from RevisedMicroGame.taskManager import ScriptScheduler
from RevisedMicroGame.tileHandler import TileHandler
from RevisedMicroGame.coordinateSystem import VectorMapFactory
from RevisedMicroGame.displayDrivers import WaveShareDisplay
WIDTH=240
HEIGHT=300
vectorMap=VectorMapFactory(lambda x,width: x+width//2, lambda y,height: -y+height//2)
Game=GameHandler(ScriptScheduler(),TileHandler(WaveShareDisplay(),2,4,1),vectorMap)