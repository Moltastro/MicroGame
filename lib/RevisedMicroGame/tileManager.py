from .coordinateSystem import *
from .collisionShape import *
from .tile import Tile
from .byteBuffer import ByteBuffer  # <-- add this import
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .drawable import Drawable
    from .displayInterface import DisplayInterface,DebugDispay

class TileManager:
    def __init__(self,displayDriver:'DisplayInterface',vTiles:int,hTiles:int,buffers:int=1):
        self.displayDriver=displayDriver
        self.vTiles=vTiles
        self.hTiles=hTiles
        self.size=Vec2(displayDriver.width//hTiles,displayDriver.height//vTiles)
        tiles=[]
        for ty in range(vTiles):
            row=[]
            for tx in range(hTiles):
                bbox=BBox(Vec2(tx*self.size.x,ty*self.size.y),self.size)
                row.append(Tile(bbox))
            tiles.append(row)
        self.tiles=tiles  # <-- use normal list of lists
        self.dirty_tiles=set()
        self.framebuffers=[ByteBuffer(self.size) for _ in range(buffers)]

    def tile_coordinates(self,pos:Vec2)->tuple[int,int]:
        return (int(int(pos.x)//self.size.x),int(int(pos.y)//self.size.y))
        
    def add_bbox(self,drawable:'Drawable',bbox:BBox):
        clamped=bbox.clone().clamp(self.displayDriver.bbox)
        topRight = self.tile_coordinates(clamped.pos)
        bottomRight = self.tile_coordinates(clamped.pos + clamped.size)
        dirty_tiles = set()
        for tx in range(topRight[0], bottomRight[0] + 1):
            for ty in range(topRight[1], bottomRight[1] + 1):
                tile=self.tiles[ty][tx]  # <-- access as [row][col]
                tile.drawables.add(drawable)
                dirty_tiles.add(tile)
        self.dirty_tiles.update(dirty_tiles)
        return dirty_tiles

    def add_coord(self,drawable:'Drawable',pos:Vec2) -> 'Tile':
        tx,ty=self.tile_coordinates(pos)
        tile:'Tile'=self.tiles[ty][tx]  # <-- access as [row][col]
        tile.drawables.add(drawable)
        self.dirty_tiles.add(tile)
        return tile

    def draw(self,coordinateSystem:'VectorMapFactory'):
        tile:'Tile'
        for tile in self.dirty_tiles:
            fb=self.framebuffers[0]
            fb.fill(0)
            tile.draw(fb,coordinateSystem)
            self.displayDriver.show_region(tile.bbox,fb)

    def remove_from_tiles(self,drawable:'Drawable',tiles:set):
        tile:'Tile'
        for tile in tiles:
            tile.drawables.discard(drawable)
            self.dirty_tiles.add(tile)