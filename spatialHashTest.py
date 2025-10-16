from Rewrite3 import *
from Rewrite3.tileManager import GridTileManager
from Rewrite3.displayDrivers import WaveShareDisplay
from random import randint
from picozero import Button
tileManager=GridTileManager(WaveShareDisplay(240,300),2,2)
game=GameHandler(ScriptScheduler(),tileManager,VectorMapFactory(lambda x: x+240//2, lambda y: -y+280//2))
GameObject.bind_game_handler(game)
""" Game.backgroundColor=rgb(0, 255, 242)
sprite=Image("Chicken.bmp")
pipe=Image("Pipe.bmp")
rect=GameObject(50,50,Sprite(sprite),Rectangle(5,5,rgb(52, 255, 1)))
pipe=GameObject(200,120,Sprite(pipe))
rect.velocity.speed=50
rect.velocity.angle=randint(0,360)
txt=Text("000")
text=GameObject(30,30,txt)
while True:
   txt.text=f"fps: {1/Game.delta:>5}"
   Game.update() """
game.backgroundColor= rgb(78, 161, 233 )
gravity=-1

buttonpressed=Button(21)
playerImg = Image ("Chicken.bmp")
player = GameObject(0,150,Sprite(playerImg))
pipeImg = Image ("Pipe.bmp")
downPipeImg=pipeImg.create_flipped_vertically()



@forever
def frameupdate():
   global gravity 
   player.pos.y+=gravity*game.delta*15
   gravity+=-0.75*game.delta*3
   yield
buttonState=True

@script
def cooldownButton():
   yield from wait(0.15)
   global buttonState
   buttonState=True

pipes = []

@forever
def createPipe():
   pipe = GameObject(120, -50, Sprite(pipeImg))
   down_pipe=GameObject(120,150,Sprite(downPipeImg))
   down_pipe.velocity.x=-30
   print(f"{down_pipe.sprite.Rect}")
   pipe.velocity.x=-30
   pipes.append(pipe)
   pipes.append(down_pipe)
   def destroy():
      yield from wait_until(lambda: pipe.pos.x<-120)
      game.remove(pipe)
      game.remove(down_pipe)
   game.taskmanager.start(destroy)
   yield from wait(4)
txt=Text("000")
text=GameObject(-90,90,txt)
game.taskmanager.start(createPipe,"Createpipe")
game.taskmanager.start(frameupdate,"chicken_gravity")
while True:
   txt.text=f"fps: {1/game.delta:>5}"
   game.update()
   if buttonpressed.is_active==True and buttonState:
      print("Knapp nedtryckt")
      gravity=2
      buttonState=False
      game.taskmanager.start(cooldownButton)

   for pipe in pipes:
      if player.is_colliding(pipe):
         game.stopped=True
         break


   if player.pos.y<=-150:
      print ("game.stop()")