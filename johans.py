from MicroGame.gameObject import *
from MicroGame.drawable import *
from picozero import Button
from MicroGame.gameHandler import GameHandler
from MicroGame.viewportTileHandler import singleViewPort
game=GameHandler()
singleViewPort.backgroundColor= rgb(78, 161, 233 )
gravity=-1
buttonpressed=Button(16)
playerImg = Image ("Chicken.bmp")
player = GameObject(SmallSprite(playerImg, 30,40, 0))
playerFlipped=playerImg.create_flipped_horizontally()


pipeImg = Image ("Pipe.bmp")
uppPipe= pipeImg.create_flipped_vertically()

def frameupdate():
    global gravity 
    player.y+=gravity
    gravity+=-0.75
buttonState=True

def cooldownButton():
    yield from game.taskmanager.wait(0.15)
    global buttonState
    buttonState=True
UpperPipe = GameObject(AnimatedSprite([playerImg,playerFlipped],3,0,20, -1))
pipes = []
def createPipe():
    
    lowerPipe = GameObject(SmallSprite(pipeImg,0, 0, -1))
    lowerPipe.velocity_x=-5
    #UpperPipe.velocity_x=-5
    pipes.append(lowerPipe)
    yield from game.taskmanager.wait(1)
    game.taskmanager.add(createPipe)

game.taskmanager.add(createPipe)

while True:
    game.run()
    frameupdate()
    if buttonpressed.is_active==True and buttonState:
        #print("Knapp nedtryckt")
        gravity=5
        buttonState=False
        game.taskmanager.add(cooldownButton)
   
    for pipe in pipes:
        if player.is_colliding_with(pipe):
            GameObject(Text(-20,50,"GAME OVER",rgb(255,0,0)))
            #game.run()
            #game.stop()
            break


    if player.y<=-150:
      pass
    #game.stop()
    