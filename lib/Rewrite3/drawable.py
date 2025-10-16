from Rewrite3.collisionShape import Vec2, VectorMapFactory
from Rewrite3.coordinateSystem import VectorMapFactory
from .collisionShape import *
from .util import *
from .byteBuffer import ByteBuffer
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .tileManager import TileManager
    from .coordinateSystem import VectorMapFactory

DEBUG = False
        

class Drawable:
    def __init__(self, offset_x=0, offset_y=0, w=0, h=0, z=0):
        self.offset=Vec2(offset_x,offset_y)
        self.pos=Vec2(0,0,self._on_move)
        self.size=Vec2(w,h)
        self.z = z
        self.old_Rect=None
        self.has_moved=True

    @property
    def Rect(self):
        return Rect(self.pos+self.offset-self.size/2,self.size) 
    
    def _on_move(self):
        self.has_moved=True
        if DEBUG: print(f"[Drawable] Moved {self}")
    def remove(self):
        self.has_moved=True
        self.offset.move(1000000,1000000)
    def update(self,tileHandler:TileManager,coordinateSystem:VectorMapFactory):
        if self.has_moved:
            if DEBUG: print(f"[Drawable] Updating {self}")
            if self.old_Rect:
                tileHandler.remove_from_Rect(self,self.old_Rect)
            self.old_Rect=Rect(self.pos+self.offset,self.size)
            self.mark_dirty(tileHandler,coordinateSystem)
            self.has_moved=False
    
    def mark_dirty(self,tileHandler:TileManager,coordinateSystem:VectorMapFactory):
        tileHandler.add_Rect(self,self.Rect.transform(coordinateSystem))
    
    def draw_into_tile(self,bufferPos:Vec2,vectorMapFactory:VectorMapFactory, fb:ByteBuffer):
        relativePos=self.tile_relative_coordinates(bufferPos,vectorMapFactory)
        self.draw_into(fb,relativePos)

    def draw_into(self, fb:ByteBuffer, relativePos:Vec2):
        """Override in subclass: draw shape into given FrameBuffer"""
        pass

    def tile_relative_coordinates(self,bufferPos:Vec2,vectorMapFactory:VectorMapFactory):
        #Returns coordinates relative to the framebuffer coordinates
        return vectorMapFactory.map(self.Rect.pos+self.offset)-bufferPos

    def __repr__(self):
        return (f"Drawable(Rect={self.Rect}, z={self.z}, moved={self.has_moved}, ")

class Ellipse(Drawable):
    def __init__(self, x=0, y=0, w=0, h=0, color=0xFFFF, fill=True, z=0):
        super().__init__(x, y, w, h, z)
        self.color = color
        self.fill=fill

    def draw_into(self, fb:ByteBuffer, relativePos:Vec2):
        # Use Rect for position and size
        cx = int(relativePos.x)
        cy = int(relativePos.y)
        xr = int(self.Rect.size.x // 2)
        yr = int(self.Rect.size.y // 2)
        fb.ellipse(cx + xr, cy + yr, xr, yr, self.color, self.fill)

    def __repr__(self):
        return (f"Ellipse(Rect={self.Rect}, color={hex(self.color)}, z={self.z})")

class Rectangle(Drawable):
    def __init__(self, w=0, h=0, color=0xFFFF, fill=True, z=0):
        super().__init__(w//2, h//2, w, h, z)
        self.fill=fill
        self.color = color

    def draw_into(self, fb:ByteBuffer, relativePos:Vec2):
        if DEBUG:print(f"[Drawable] drawing rectangle at {relativePos}")
        x = int(relativePos.x)
        y = int(relativePos.y)
        w = int(self.Rect.size.x)
        h = int(self.Rect.size.y)
        fb.rect(x, y, w, h-1, self.color,self.fill) # type: ignore
    
    def tile_relative_coordinates(self, bufferPos: Vec2, vectorMapFactory: VectorMapFactory):
        return super().tile_relative_coordinates(bufferPos, vectorMapFactory)

    def __repr__(self):
        return (f"Rectangle(Rect={self.Rect}, color={hex(self.color)}, z={self.z})")

class Line(Drawable):
    def __init__(self, start_offset:Vec2, end_offset:Vec2, z=0,color=0xFFFF):
        self.color=color
        self._start_offset=start_offset.clone()
        self._start_offset.on_update=self._on_update
        self._end_offset=end_offset
        w,h=end_offset-start_offset
        super().__init__(start_offset.x, start_offset.y, w, h+1, z) # type: ignore
    
    def _on_update(self):
        self.pos=self._start_offset
        self.size=self._start_offset-self._end_offset
    
    def draw_into(self, fb: ByteBuffer, relativePos: Vec2):
        fb.line(*relativePos.toInt(),*(relativePos+self._end_offset).toInt(),self.color) # type: ignore
    
    
    


class Sprite(Drawable):
    def __init__(self,image:Image, offset_x=0, offset_y=0, w=0, h=0, z=0):
        super().__init__(offset_x, offset_y, image.w, image.h, z)
        self.image=image
    
    def draw_into(self, fb: ByteBuffer, relativePos: Vec2):
        fb.blit(self.image.fb,*relativePos.toInt(),0x0000) # type: ignore
        
class Text(Drawable):
    def __init__(self, text, offset_x=0, offset_y=0, color=0xFFFF, z=0):
        self._text=text
        self.color=color
        super().__init__(offset_x,offset_y,len(text)*8,8,z)
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self,other):
        self._text=str(other)
    def draw_into(self, fb: ByteBuffer, relativePos: Vec2):
        fb.text(self._text,*relativePos.toInt(),self.color)