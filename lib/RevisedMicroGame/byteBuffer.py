from framebuf import FrameBuffer,RGB565
from coordinateSystem import Vector2
class ByteBuffer(FrameBuffer):
    def __init__(self,size:Vector2):
        self.size=size
        self.buffer=bytearray(int(size.x)*int(size.y)*2)
        super().__init__(self.buffer,int(size.x),int(size.y),RGB565)