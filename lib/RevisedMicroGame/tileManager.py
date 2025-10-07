from RevisedMicroGame.displayInterface import DisplayInterface
from .collisionShape import BBox
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

DEBUG = False

class TileManager:
    def add_bbox(self,drawable:Drawable,bbox:BBox):
        raise NotImplementedError
    
    def remove_from_bbox(self,drawable:Drawable,bbox:BBox):
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

    def add_bbox(self, drawable: Drawable, bbox: BBox):
        self.tiles.add(drawable,bbox)
        self.dirty_regions.append(bbox)
    
    def remove_from_bbox(self, drawable, bbox):
        self.tiles.remove(drawable,bbox)
        self.dirty_regions.append(bbox)
    
    def draw(self,coordinateSystem:VectorMapFactory, color:int):
        region:BBox
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
        self.dirtyRegions=[]
        
    def add_bbox(self, drawable: Drawable, bbox: BBox):
        self.tiles.add(drawable,bbox)
        tileSlice=self.tiles.bbox_to_gridAligned_bbox(bbox)
        self.dirtyRegions.append(tileSlice)
    
    def remove_from_bbox(self, drawable: Drawable, bbox: BBox):
        self.tiles.remove(drawable,bbox)
        tileSlice=self.tiles.bbox_to_gridAligned_bbox(bbox)
        self.dirtyRegions.append(tileSlice)
    
    def draw(self, coordinateSystem: VectorMapFactory, color: int):
        region:BBox
        for region in self.dirtyRegions:
            drawables=self.tiles.local_areaRange(region)
            for drawable in drawables:

        