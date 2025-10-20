from .coordinateSystem import *
from .collisionShape import AABB
import struct
from .byteBuffer import ByteBuffer
DEBUG = True
class DisplayInterface:
    def __init__(self,width:int,height:int):
        self.width=width
        self.height=height
        self.Rect=AABB(Vec2(0,0),Vec2(width,height))
    
    def send_color_data(self,frameBuffer:ByteBuffer):
        if DEBUG: print("[DisplayInterface] Sending color data")
        raise NotImplementedError

    def set_window(self, Rect:AABB):
        if DEBUG: print(f"[DisplayInterface] Setting window {Rect}")
        raise NotImplementedError

    def show_region(self, Rect:AABB,frameBuffer:ByteBuffer):
        if DEBUG: print(f"[DisplayInterface] Showing region {Rect}")
        self.set_window(Rect)
        self.send_color_data(frameBuffer)
    def __repr__(self):
        return f"DisplayInterface(width={self.width}, height={self.height})"
import struct

_EMPTY_CHAR = "  "  # double-space per pixel block

def rgb565_to_rgb888(value: int) -> tuple[int, int, int]:
    """Convert 16-bit RGB565 pixel to (r,g,b) tuple 0..255."""
    r = (value >> 11) & 0x1F
    g = (value >> 5) & 0x3F
    b = value & 0x1F
    return (r * 255) // 31, (g * 255) // 63, (b * 255) // 31

class DebugDisplay(DisplayInterface):
    """
    Debug display with an internal retained framebuffer.
    - set_window() selects a writable region.
    - send_color_data() writes into that region relative to its top-left.
    - display() prints the entire retained framebuffer.
    """

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        # Create our own retained framebuffer
        self.framebuffer = ByteBuffer(Vec2(width, height))
        self.current_window = self.Rect  # initially full screen

    def set_window(self, Rect: AABB):
        """Select a writable region inside the retained framebuffer."""
        if DEBUG:
            print(f"[DebugDisplay] set_window {Rect}")
        # clamp window to display size
        #self.current_window = Rect.clone().clamp(self.Rect)

    def send_color_data(self, frameBuffer: ByteBuffer):
        """Write the incoming ByteBuffer's contents into the current window region."""
        win = self.current_window
        win_w, win_h = int(win.size.x), int(win.size.y)

        src_w, src_h = int(frameBuffer.size.x), int(frameBuffer.size.y)
        if src_w != win_w or src_h != win_h:
            raise ValueError(
                f"ByteBuffer size {src_w}x{src_h} does not match window size {win_w}x{win_h}"
            )

        if DEBUG:
            print(f"[DebugDisplay] Writing {src_w}x{src_h} into window at {win.pos}")

        dest_w = int(self.framebuffer.size.x)
        dest_buf = self.framebuffer.buffer
        src_buf = frameBuffer.buffer

        row_bytes = win_w * 2
        dest_stride = dest_w * 2

        for row in range(win_h):
            dest_start = ((int(win.pos.y) + row) * dest_stride) + int(win.pos.x) * 2
            dest_buf[dest_start:dest_start + row_bytes] = src_buf[row * row_bytes: (row + 1) * row_bytes]

    def display(self):
        """Print out the entire internal framebuffer as ANSI-colored grid."""
        w, h = int(self.framebuffer.size.x), int(self.framebuffer.size.y)
        buf = self.framebuffer.buffer

        print(f"DebugDisplay: full framebuffer ({w}x{h})")
        row_stride = w * 2
        for y in range(h):
            row_bytes = memoryview(buf)[y * row_stride : (y + 1) * row_stride]
            row_chars = []
            for px_off in range(0, len(row_bytes), 2):
                px_val = struct.unpack_from("<H", row_bytes, px_off)[0]
                r, g, b = rgb565_to_rgb888(px_val)
                row_chars.append(f"\033[48;2;{r};{g};{b}m{_EMPTY_CHAR}\033[0m")
            print("".join(row_chars))


