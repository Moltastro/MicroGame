from coordinateSystem import *
from collisionShape import *
from tileHandler import TileHandler
class Drawable:
    def __init__(self, x=0, y=0, w=0, h=0, z=0):
        self.bbox=BBox(Vector2(x,y),Vector2(w,h),)
        self.z = z
        self.previous_tiles=set()
        
    def _on_move(self):
        self.has_moved=True

    def update(self,tileHandler:TileHandler,coordinateSystem:VectorMapFactory):
        if self.has_moved:
            tileHandler.remove_from_tiles(self,self.previous_tiles)
            self.previous_tiles=self.mark_dirty(tileHandler,coordinateSystem)
            self.has_moved=False
    
    def mark_dirty(self,tileHandler:TileHandler,coordinateSystem:VectorMapFactory):
        tiles=tileHandler.add_bbox(self,self.bbox.transform(coordinateSystem))
        return tiles
    
    def draw_into(self, fb, relativePos:Vector2):
        """Override in subclass: draw shape into given FrameBuffer"""
        pass

    def tile_relative_coordinates(self,bufferPos:Vector2,vectorMapFactory:VectorMapFactory):
        #Returns coordinates relative to the framebuffer coordinates
        return vectorMapFactory.map(self.bbox.pos)-bufferPos