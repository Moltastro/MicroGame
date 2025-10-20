from RevisedRenderPipeline import *
from time import sleep
from utime import ticks_us,ticks_diff
from random import randint
from RevisedRenderPipeline.util import profile

Game=GameHandler(ScriptScheduler(),Renderer(2,2,WaveShareDisplay()))

rect=Rectangle(Vec2(0,0),Vec2(50,50))
for i in range(20):
  object=GameObject(Vec2(120,140),sprite=rect)
  object.velocity=Vec2(randint(-5,5),randint(-5,5))
  Game.reparent(object)
def main():
  t1=ticks_us()
  Game.update()
  diff=ticks_diff(ticks_us(),t1)
  print(diff/1000)
profile(main())