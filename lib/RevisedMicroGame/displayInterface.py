from coordinateSystem import *
from collisionShape import BBox
from RevisedMicroGame.byteBuffer import ByteBuffer
from abc import ABC, abstractmethod
class DisplayInterface(ABC):
    def __init__(self,width:int,height:int):
        self.width=width
        self.height=height
        self.bbox=BBox(Vector2(0,0),Vector2(width,height))
    
    @abstractmethod
    def send_color_data(self,frameBuffer:ByteBuffer):
        pass

    @abstractmethod
    def set_window(self, BBox:BBox):
        pass

    @abstractmethod
    def show_region(self, BBox:BBox,frameBuffer:ByteBuffer):
        self.set_window(BBox)
        self.send_color_data(frameBuffer)
