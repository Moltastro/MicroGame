from .coordinateSystem import *
from .collisionShape import BBox
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .byteBuffer import ByteBuffer
class DisplayInterface:
    def __init__(self,width:int,height:int):
        self.width=width
        self.height=height
        self.bbox=BBox(Vec2(0,0),Vec2(width,height))
    
    def send_color_data(self,frameBuffer:ByteBuffer):
        raise NotImplementedError

    def set_window(self, BBox:BBox):
        raise NotImplementedError

    def show_region(self, BBox:BBox,frameBuffer:ByteBuffer):
        self.set_window(BBox)
        self.send_color_data(frameBuffer)

class DebugDispay(DisplayInterface):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)

    def send_color_data(self, frameBuffer: ByteBuffer):
        print(f"frame: {frameBuffer}")
    
    def set_window(self, BBox: BBox):
        print(f"Set view: {BBox}")
