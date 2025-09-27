from .collisionShape import BBox
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .coordinateSystem import VectorMapFactory
    from .drawable import Drawable
    from .byteBuffer import ByteBuffer

DEBUG = True

class Tile:
    def __init__(self,bbox:BBox) -> None:
        self.bbox=bbox
        self.drawables=set()
    
    def draw(self,fb:'ByteBuffer',vectorMapFactory:'VectorMapFactory'):
        if DEBUG: print(f"[Tile] Drawing {len(self.drawables)} drawables in tile {self.bbox}")
        drawable:'Drawable'
        for drawable in self.drawables:
            vector=drawable.tile_relative_coordinates(self.bbox.pos,vectorMapFactory)
            drawable.draw_into(fb,vector)
    
    def __repr__(self):
        return f"Tile(bbox={self.bbox}, drawables={len(self.drawables)})"