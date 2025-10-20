from .drawable import *
from .node import *
from .displayInterface import *
from .collisionShape import *
from .coordinateSystem import *
from .byteBuffer import *
from .util import timed_function
#drawActions->renderer
""" class FrameTile:
  def __init__(self,AABB) -> None:
    self.AABB=AABB
  def intersect(self,renderAction:RenderAction):
    if renderAction. """
class Renderer:
  def __init__(self,vTiles:int,hTiles:int,displayDriver:DisplayInterface) -> None:
    print("Creating renderer")
    self.tileSize=Vec2(displayDriver.width//hTiles,displayDriver.height//vTiles)
    #self.initialize_buckets()
    self.vTiles=vTiles
    self.hTiles=hTiles
    self.fb=ByteBuffer(self.tileSize)
    self.displayDriver=displayDriver

  """ def initialize_buckets(self):
    self.buckets=[[] for i in range(self.vTiles*self.hTiles)] """
  @timed_function
  def draw(self,color:int,drawCommands:list):
    drawCommands.sort()
    for v in range(self.vTiles):
      for h in range(self.hTiles):
        pos=Vec2(h*self.tileSize.x,v*self.tileSize.y)
        self.fb.fill(color)
        print(f"{pos}")
        action:RenderAction
        for action in drawCommands:
          action.action(self.fb,pos)
        aabb=AABB(pos,self.tileSize)
        
        self.displayDriver.show_region(aabb,self.fb)
    
