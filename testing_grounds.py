from MicroGame.gameHandler import GameHandler
from MicroGame.drawable import *
from MicroGame.gameObject import *
from MicroGame.viewportTileHandler import singleViewPort
from picozero import Pot
from time import sleep
from random import randint

pot=Pot(26)
game=GameHandler()
singleViewPort.backgroundColor=rgb(52, 152, 245)

#def spawn_rect():
#    rect=GameObject(Rectangle(randint(0,230),randint(0,290),10,10,0,rgb(randint(0,255),randint(0,255),randint(0,255))))
#    rect.velocity_x=randint(1,10)
#    rect.velocity_y=randint(1,10)
#    rect.boune=True
#for i in range(20):
#    spawn_rect()

line=GameObject(Rectangle(0,100,100,2,0,rgb(255,255,0)))
line.y=150
dir=1
def bounce():
    global dir
    dir=1
    yield from game.taskmanager.wait(1)
    dir=-1
    yield from game.taskmanager.wait_until(lambda: line.y<100)
    dir=1
    game.taskmanager.add(bounce)
game.taskmanager.add(bounce)
text=GameObject(Text(50,50,"Hello",rgb(255,0,0)))
circle=GameObject(Rectangle(0,0,50,50))
def bounce2():
    if circle.y>150:
        circle.velocity_y=-5
        game.taskmanager.add(move_up)
def inc():
    circle.y-=5
def move_up():
    yield from game.taskmanager.repeat(5 , inc)
circle.on_update=bounce2
while True:
    circle.y+=5
    line.sprite.w+=dir*5
    game.run()