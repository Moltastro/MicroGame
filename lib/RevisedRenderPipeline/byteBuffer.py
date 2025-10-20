from framebuf import FrameBuffer,RGB565
from typing import TYPE_CHECKING # type: ignore
if TYPE_CHECKING:
    from .coordinateSystem import Vec2
try:
    from ulab import numpy as np # type: ignore
except:
    import numpy as np
DEBUG = False
class ByteBuffer(FrameBuffer):
    def __init__(self,size:'Vec2',buffer=None):
        self.size=size
        if buffer:
            self.buffer=buffer
        else:
            self.buffer=bytearray(int(size.x)*int(size.y)*2)
        if DEBUG: print(f"[ByteBuffer] Created with size {self.size}")
        super().__init__(self.buffer,int(size.x),int(size.y),RGB565)

    def scale(self, factor: float):
        if DEBUG: print(f"[ByteBuffer] Scaling by factor {factor}")
        arr = np.frombuffer(self.buffer, dtype=np.uint16).reshape((int(self.size.y), int(self.size.x)))
        # Simple nearest-neighbor scaling
        new_shape = (int(self.size.y * factor), int(self.size.x * factor))
        scaled = arr[::int(1/factor), ::int(1/factor)]
        # Copy back to buffer (if needed)
        self.buffer[:len(scaled.flatten())*2] = scaled.flatten().tobytes()

    def rotate(self, angle: int):
        if DEBUG: print(f"[ByteBuffer] Rotating by {angle} degrees")
        """
        Rotates the buffer by the specified angle (must be 90, 180, or 270 degrees).
        """
        arr = np.frombuffer(self.buffer, dtype=np.uint16).reshape((int(self.size.y), int(self.size.x)))
        if angle == 90:
            rotated = np.rot90(arr, k=1)
        elif angle == 180:
            rotated = np.rot90(arr, k=2)
        elif angle == 270:
            rotated = np.rot90(arr, k=3)
        else:
            raise ValueError("Angle must be 90, 180, or 270 degrees")
        # Update buffer and size
        self.size.x, self.size.y = rotated.shape[1], rotated.shape[0]
        self.buffer = bytearray(rotated.flatten().tobytes())
        super().__init__(self.buffer, int(self.size.x), int(self.size.y), RGB565)

    def flip_horizontal(self):
        if DEBUG: print("[ByteBuffer] Flipping horizontally")
        """
        Flips the buffer horizontally.
        """
        arr = np.frombuffer(self.buffer, dtype=np.uint16).reshape((int(self.size.y), int(self.size.x)))
        flipped = np.fliplr(arr)
        self.buffer = bytearray(flipped.flatten().tobytes())
        super().__init__(self.buffer, int(self.size.x), int(self.size.y), RGB565)

    def flip_vertical(self):
        if DEBUG: print("[ByteBuffer] Flipping vertically")
        """
        Flips the buffer vertically.
        """
        arr = np.frombuffer(self.buffer, dtype=np.uint16).reshape((int(self.size.y), int(self.size.x)))
        flipped = np.flipud(arr)
        self.buffer = bytearray(flipped.flatten().tobytes())
        super().__init__(self.buffer, int(self.size.x), int(self.size.y), RGB565)

    def __repr__(self):
        return f"ByteBuffer(size={self.size}, buffer_len={len(self.buffer)})"
