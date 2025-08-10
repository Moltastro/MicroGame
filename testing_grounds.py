from MicroGame.gameHandler import GameHandler
from MicroGame.drawable import *
from MicroGame.gameObject import *
from MicroGame.viewportTileHandler import SingleFrameBufferDriver
from picozero import Pot
from time import sleep
from random import randint
import gc
def available_ram():
    gc.collect()  # Run garbage collection to free unused memory
    free_bytes = gc.mem_free()
    allocated_bytes = gc.mem_alloc()
    total_bytes = free_bytes + allocated_bytes
    print(f"Free RAM: {free_bytes} bytes")
    print(f"Allocated RAM: {allocated_bytes} bytes")
    print(f"Total RAM: {total_bytes} bytes")
    return free_bytes

pot=Pot(26)
game=GameHandler()

def spawn_rect():
    rect=GameObject(Rectangle(randint(0,230),randint(0,290),10,10,0,rgb(randint(0,255),randint(0,255),randint(0,255))))
    rect.velocity_x=randint(1,10)
    rect.velocity_y=randint(1,10)
    rect.boune=True

for i in range(20):
    spawn_rect()
rect = GameObject(SmallSprite(x=30,y=30,image=Image('abomination.bmp')))
while True:
    game.run()
    rect.y=int(pot.value*300)
    available_ram()
