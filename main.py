from MicroGame..gameHandler import GameHandler
from MicroGame..drawable import *
from MicroGame..gameObject import *
from MicroGame.viewport.TileHandler import singleViewPort
from picozero import Pot,Button
from time import sleep
from random import randint
game=GameHandler()
pot=Pot(28)
shoot=Button(16)

GameObject(Ellipse(x=0,y=0))

aim=GameObject(Rectangle(x=0,y=0,w=10,h=10))

def spawn_bullet():
    bullet=GameObject(Rectangle(aim.x,aim.y,10,10))
    bullet.set_speed_in_direction((pot.value-0.002)*170*360,10)
    def remove_bullet():
        yield from game.taskmanager.wait_until(lambda : not bullet.is_visible())
        bullet.delete()
        print("Deleted")
    game.taskmanager.add(remove_bullet
                         )

    

shoot.when_activated=spawn_bullet
while True:
    aim.x,aim.y=0,0
    aim.step_in_direction((pot.value-0.002)*170*360,40)
    game.run()