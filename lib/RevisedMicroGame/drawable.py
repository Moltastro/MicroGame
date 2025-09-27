from .collisionShape import *
from byteBuffer import ByteBuffer
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .tileManager import TileManager
    from .coordinateSystem import VectorMapFactory

class Drawable:
    def __init__(self, x=0, y=0, w=0, h=0, z=0):
        self.bbox=BBox(Vec2(x,y),Vec2(w,h),)
        self.z = z
        self.previous_tiles=set()
        
    def _on_move(self):
        self.has_moved=True

    def update(self,tileHandler:TileManager,coordinateSystem:VectorMapFactory):
        if self.has_moved:
            tileHandler.remove_from_tiles(self,self.previous_tiles)
            self.previous_tiles=self.mark_dirty(tileHandler,coordinateSystem)
            self.has_moved=False
    
    def mark_dirty(self,tileHandler:TileManager,coordinateSystem:VectorMapFactory):
        tiles=tileHandler.add_bbox(self,self.bbox.transform(coordinateSystem))
        return tiles
    
    def draw_into(self, fb:ByteBuffer, relativePos:Vec2):
        """Override in subclass: draw shape into given FrameBuffer"""
        pass

    def tile_relative_coordinates(self,bufferPos:Vec2,vectorMapFactory:VectorMapFactory):
        #Returns coordinates relative to the framebuffer coordinates
        return vectorMapFactory.map(self.bbox.pos)-bufferPos

class Ellipse(Drawable):
    def __init__(self, x=0, y=0, w=0, h=0, color=0xFFFF, z=0):
        super().__init__(x, y, w, h, z)
        self.color = color

    def draw_into(self, fb:ByteBuffer, relativePos:Vec2):
        # Use bbox for position and size
        cx = int(relativePos.x)
        cy = int(relativePos.y)
        xr = int(self.bbox.size.x // 2)
        yr = int(self.bbox.size.y // 2)
        fb.ellipse(cx + xr, cy + yr, xr, yr, self.color, f=True)

class Rectangle(Drawable):
    def __init__(self, x=0, y=0, w=0, h=0, color=0xFFFF, z=0):
        super().__init__(x, y, w, h, z)
        self.color = color

    def draw_into(self, fb:ByteBuffer, relativePos:Vec2):
        x = int(relativePos.x)
        y = int(relativePos.y)
        w = int(self.bbox.size.x)
        h = int(self.bbox.size.y)
        fb.rect(x, y, w, h, self.color, f=True) # type: ignore


