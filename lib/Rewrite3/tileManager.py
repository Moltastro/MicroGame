from RevisedMicroGame.displayInterface import DisplayInterface
from .collisionShape import Rect
from .coordinateSystem import Vec2, VectorMapFactory
from .drawable import Drawable
from .coordinateSystem import *
from .util import rgb
from random import randint
from .byteBuffer import ByteBuffer  # <-- add this import
from typing import TYPE_CHECKING # type: ignore
from .spatialHash import SpatialHash
if TYPE_CHECKING:
    from .drawable import Drawable
    from .displayInterface import DisplayInterface
from time import ticks_ms,ticks_diff
DEBUG = False
DEBUG_FPS = False

class TileManager:
    def add_Rect(self,drawable:Drawable,Rect:Rect):
        raise NotImplementedError
    
    def remove_from_Rect(self,drawable:Drawable,Rect:Rect):
        raise NotImplementedError
    
    def draw(self, coordinateSystem:VectorMapFactory,color:int):
        raise NotImplementedError

class VariableTileManager(TileManager):
    def __init__(self, displayDriver: DisplayInterface, vTiles: int, hTiles: int, buffers: int = 1):
        self.displayDriver=displayDriver
        self.tileAm=Vec2(hTiles,vTiles)
        self.tiles=SpatialHash(displayDriver.width,displayDriver.height,hTiles,vTiles)
        self.dirty_regions=[]
        self.mergeGrid=SpatialHash(displayDriver.width,displayDriver.height,hTiles,vTiles)

    def add_Rect(self, drawable: Drawable, Rect: Rect):
        self.tiles.add(drawable,Rect)
        self.dirty_regions.append(Rect)
    
    def remove_from_Rect(self, drawable, Rect):
        self.tiles.remove(drawable,Rect)
        self.dirty_regions.append(Rect)
    
    def draw(self,coordinateSystem:VectorMapFactory, color:int):
        region:Rect
        for region in self.dirty_regions:
            buff=ByteBuffer(region.size)
            drawable:Drawable
            for drawable in self.tiles[region]:
                drawable.draw_into(buff,region.pos)
            self.displayDriver.show_region(region,buff)
        self.dirty_regions.clear()

class GridTileManager(TileManager):
    def __init__(self,displayDriver:DisplayInterface,vTiles,hTiles,buffers:int = 1) -> None:
        self.displayDriver=displayDriver
        self.vTiles=vTiles
        self.hTiles=hTiles
        self.tiles=SpatialHash(displayDriver.width,displayDriver.height,hTiles,vTiles)
        self.dirtyRegions=set()
        self.buffer=ByteBuffer(Vec2(displayDriver.width/hTiles,displayDriver.height/vTiles))
        
    def add_Rect(self, drawable: Drawable, Rect: Rect):
        index=self.tiles.add(drawable,Rect)
        if DEBUG: print(f"[TILEMANAGER] Added rects {index}")
        self.dirtyRegions.update(index)
        if DEBUG: print(f"[TILEMANAGER] all regions {self.dirtyRegions}")
    
    def remove_from_Rect(self, drawable: Drawable, Rect: Rect):
        
        tiles=self.tiles.remove(drawable,Rect)
        if DEBUG: print(f"[TILEMANAGER] Removed rects {tiles}")
        self.dirtyRegions.update(tiles)
    
    def draw(self, coordinateSystem: VectorMapFactory, color: int):
        if DEBUG:print(f"[TILEMANAGER] Beginning drawing {self.dirtyRegions}")
        region:int
        tot=0
        for region in self.dirtyRegions:
            self.buffer.fill(color)
            drawables=self.tiles[region]
            
            buffer_pos=self.tiles.rect_at_index(region)
            if DEBUG: print(f"[TILEMANAGER] Drawing region {region} with pos {buffer_pos}")
            drawable:Drawable
            for drawable in drawables:
                drawable.draw_into_tile(buffer_pos.pos,coordinateSystem,self.buffer)
            start=ticks_ms()
            self.displayDriver.show_region(buffer_pos,self.buffer)
            tot+=ticks_diff(start,ticks_ms())
        out=f"screen time {tot}"
        if DEBUG_FPS:print(f"{out:>16}")
        self.dirtyRegions.clear()
        