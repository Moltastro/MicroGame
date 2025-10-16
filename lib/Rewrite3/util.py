import math
from .byteBuffer import ByteBuffer
from .coordinateSystem import Vec2

def rgb(r, g, b, swap_bytes=True):
    """Returnerar färg med rött, grönt, blått 0-255"""
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F

    value = (r5 << 11) | (g6 << 5) | b5
    if swap_bytes:
        value = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)
    return value

class Image:
    """
    Loads and stores an image.
    """
    def __init__(self,src,_buf=None,_w=None,_h=None):
        """
        Load an image from a BMP file.

        Args:
            src (str): Path to the BMP file.
        """
        if _buf and _w and _h:
            self.fb=ByteBuffer(Vec2(_w,_h),_buf)
            self.w=_w
            self.h=_h
        else:
            self.buffer,self.w,self.h = Image.load_bmp_rgb565(src)
            self.fb =ByteBuffer(Vec2(self.w,self.h),self.buffer)

    @classmethod
    def _create(cls,buf,w,h):
        return cls(None,buf,w,h)
    
    @staticmethod
    def load_bmp_rgb565(path: str) -> tuple[bytearray, int, int]:
        """
        Load a 16-bit RGB565 BMP file and return (buffer, width, height) in big-endian order.
        """
        with open(path, 'rb') as f:
            # --- Read header ---
            f.seek(10)
            pixel_offset = int.from_bytes(f.read(4), 'little')  # Pixel data start

            f.seek(18)
            width = int.from_bytes(f.read(4), 'little')
            height_raw = int.from_bytes(f.read(4), 'little')

            top_down = height_raw < 0
            height = abs(height_raw)

            f.seek(28)
            bpp = int.from_bytes(f.read(2), 'little')
            if bpp != 16:
                raise ValueError(f"BMP is {bpp} bpp, expected 16-bit RGB565")

            # --- Read pixel data ---
            row_size_bytes = ((width * 2 + 3) // 4) * 4  # Rows padded to multiple of 4 bytes

            buffer = bytearray(width * height * 2)  # Big-endian output
            f.seek(pixel_offset)

            for row in range(height):
                # BMP stores bottom row first unless top_down is True
                dest_row = row if top_down else (height - 1 - row)

                row_data = f.read(row_size_bytes)  # Includes padding
                for col in range(width):
                    px_le = row_data[col * 2: col * 2 + 2]  # Little-endian in BMP
                    # Swap to big-endian for LCD
                    buffer[(dest_row * width + col) * 2] = px_le[1]
                    buffer[(dest_row * width + col) * 2 + 1] = px_le[0]

            return buffer, width, height
    
    @staticmethod
    def rotate_rgb565_buffer(buf: bytearray, width: int, height: int, angle_deg: float):
        #Rotate an RGB565 buffer by angle_deg clockwise.
        #Returns a tuple: (rotated buffer, new_width, new_height).
        #Areas rotated out of bounds are filled with 0x0000.
        angle = math.radians(angle_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Original corners (relative to center)
        corners = [
            (-width / 2, -height / 2),
            ( width / 2, -height / 2),
            (-width / 2,  height / 2),
            ( width / 2,  height / 2)
        ]

        # Rotate corners to find new bounding box
        rotated_corners = [
            (
                x * cos_a - y * sin_a,
                x * sin_a + y * cos_a
            )
            for (x, y) in corners
        ]

        min_x = min(x for x, y in rotated_corners)
        max_x = max(x for x, y in rotated_corners)
        min_y = min(y for x, y in rotated_corners)
        max_y = max(y for x, y in rotated_corners)

        new_width = int(math.ceil(max_x - min_x))
        new_height = int(math.ceil(max_y - min_y))

        # Centers
        cx_old, cy_old = (width - 1) / 2.0, (height - 1) / 2.0
        cx_new, cy_new = (new_width - 1) / 2.0, (new_height - 1) / 2.0

        new_buf = bytearray(new_width * new_height * 2)

        def read_px(sx, sy):
            idx = (sy * width + sx) * 2
            return buf[idx], buf[idx + 1]

        for y in range(new_height):
            for x in range(new_width):
                # Destination coordinates relative to center of new image
                dx = x - cx_new
                dy = y - cy_new

                # Apply inverse rotation to get source coordinates
                sx_f =  dx * cos_a - dy * sin_a + cx_old
                sy_f =  dx * sin_a + dy * cos_a + cy_old
                sx = int(round(sx_f))
                sy = int(round(sy_f))

                di = (y * new_width + x) * 2
                if 0 <= sx < width and 0 <= sy < height:
                    lo, hi = read_px(sx, sy)
                    new_buf[di] = lo
                    new_buf[di + 1] = hi
                else:
                    new_buf[di] = 0
                    new_buf[di + 1] = 0

        return new_buf, new_width, new_height

    def create_flipped_vertically(self):
        pixel_size = 2
        flipped = bytearray(len(self.fb.buffer))

        for y in range(self.h):
            for x in range(self.w):
                src_index = (y * self.w + x) * pixel_size
                dest_index = ((self.h - 1 - y) * self.w + x) * pixel_size

                flipped[dest_index] = self.fb.buffer[src_index]
                flipped[dest_index + 1] = self.fb.buffer[src_index + 1]

        return self._create(flipped, self.w, self.h)

    def create_flipped_horizontally(self):
        pixel_size = 2
        flipped = bytearray(len(self.fb.buffer))

        for y in range(self.h):
            for x in range(self.w):
                src_index = (y * self.w + x) * pixel_size
                dest_index = (y * self.w + (self.w - 1 - x)) * pixel_size

                # copy both bytes of the pixel
                flipped[dest_index] = self.fb.buffer[src_index]
                flipped[dest_index + 1] = self.fb.buffer[src_index + 1]

        return self._create(flipped, self.w, self.h)
    
    def create_rotation(self,angle):
        rotated=self.rotate_rgb565_buffer(self.fb.buffer,self.w,self.h,angle)
        return self._create(*rotated) 