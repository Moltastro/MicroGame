from collisionShape import BBox
from coordinateSystem import VectorMapFactory
from drawable import Drawable
from byteBuffer import ByteBuffer
class Tile:
    def __init__(self,bbox:BBox) -> None:
        self.bbox=bbox
        self.drawables=set()
    
    def draw(self,fb:ByteBuffer,vectorMapFactory:VectorMapFactory):
        drawable:Drawable
        for drawable in self.drawables:
            vector=drawable.tile_relative_coordinates(self.bbox.pos,vectorMapFactory)
            drawable.draw_into(fb,vector)