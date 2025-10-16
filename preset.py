from Rewrite3 import *
from Rewrite3.tileManager import GridTileManager
from Rewrite3.displayDrivers import WaveShareDisplay
tileManager=GridTileManager(WaveShareDisplay(240,280),2,2)
game=GameHandler(ScriptScheduler(),tileManager,VectorMapFactory(lambda x: x-3+240//2, lambda y: -y+280//2))
GameObject.bind_game_handler(game)

"""step_size=4
for x in range(step_size+1):
    for y in range(step_size+1):
        xcor=x*240/step_size-120
        ycor=150-y*300/step_size
        GameObject(xcor,ycor,Rectangle(5,5,color=rgb(0, 195, 255)))
        offset=20
        if x%2:
            offset*=-1
        GameObject(xcor,ycor+offset,Text(f"{int(xcor)},{int(ycor)}",color=rgb(255, 0, 0)))
        """