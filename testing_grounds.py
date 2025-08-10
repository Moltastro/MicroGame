from MicroGame.gameHandler import GameHandler
from MicroGame.drawable import *
from MicroGame.gameObject import *
from MicroGame.viewportTileHandler import SingleFrameBufferDriver
from picozero import Pot
from time import sleep
from random import randint

pot=Pot(26)
game=GameHandler()

def spawn_rect():
    rect=GameObject(Rectangle(randint(0,230),randint(0,290),10,10,0,rgb(randint(0,255),randint(0,255),randint(0,255))))
    rect.velocity_x=randint(1,10)
    rect.velocity_y=randint(1,10)
    rect.boune=True

for i in range(20):
    spawn_rect()
rect = GameObject(Rectangle(x=30,y=30,w=30,h=30))

while True:
    game.run()
    rect.y=int(pot.value*300)
