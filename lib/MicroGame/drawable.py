from .viewportTileHandler import singleViewPort
import framebuf
from .util import *
class Image:
    def __init__(self,src):
        buf,self.w,self.h = Image.load_bmp_rgb565(src)
        self.fb =framebuf.FrameBuffer(buf,self.w,self.h,framebuf.RGB565)
    
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



    
class Drawable:
    def __init__(self, x, y, w, h, z=0):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.z = z
        self._old_tiles = set()
        self.has_moved=True
        self.old_top_left = None
        self.old_bottom_right = None
        
    
    @property
    def bbox(self):
        return (self.x,self.y,self.w,self.h)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self,val):
        if val !=self._x:
            self._x=val
            self.has_moved = True

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self,val):
        if val!=self._y:
            self._y=val
            self.has_moved = True
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self,val):
        if val!=self._w:
            self._w=val
            self.has_moved = True
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self,val):
        if val!=self._h:
            self._h=val
            self.has_moved = True
    
    def update(self):
        if self.has_moved:
            view=singleViewPort.get_instance()
            if (self.old_top_left and self.old_bottom_right):
                view.remove_drawable_in_tiles_and_mark_dirty(self)
            
            self.old_top_left,self.old_bottom_right=view.store_drawable_in_tiles_and_mark_dirty(self)
            self.has_moved=False

    def draw_into(self, fb, relative_x, relative_y):
        """Override in subclass: draw shape into given FrameBuffer"""
        pass

    def framebuffer_relative_coordinates(self,buf_x,buf_y):
        #Returns coordinates relative to the framebuffer coordinates
        return self.x-buf_x,self.y-buf_y
    
    def __str__(self) -> str:
        return f"pos: ({self.x},{self.y})"

class Rectangle(Drawable):
    def __init__(self, x, y, w, h, z=0, color=rgb(255,0,0)):
        super().__init__(x,y,w,h,z)
        self.color=color
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x,relative_y):
        fb.rect(relative_x, relative_y, self.w, self.h,self.color)

class Ellipse(Drawable):
    def __init__(self, x, y, diameter_x, diameter_y, z=0, color=rgb(0,255,0)):
        super().__init__(x, y, diameter_x, diameter_y, z)
        self.color=color
    
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        fb.ellipse(relative_x-self.w//2,relative_y-self.h//2,self.w//2,self.h//2,self.color,True)

class SmallSprite(Drawable):
    def __init__(self, x, y, image:Image, z=0):
        super().__init__(x, y, image.w, image.h, z)
        self.img=image
    
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        fb.blit(self.img.fb, relative_x, relative_y,rgb(0,0,0))

class BigSprite(Drawable):
    def __init__(self, x, y, w, h, src, z=0):
        super().__init__(x, y, w, h, z)
        self.src=src
    @staticmethod
    def draw_bmp_section_to_fb_be(
    path: str,
    fb: bytearray,
    fb_width: int,
    fb_height: int,
    fb_x: int,
    fb_y: int,
    bmp_x: int,
    bmp_y: int,
    section_width: int,
    section_height: int
    ):
        """
        Draw a rectangular section of a 16-bit RGB565 BMP (big-endian) into a framebuffer.
        - fb: framebuffer bytearray (big-endian RGB565)
        - fb_width, fb_height: dimensions of the framebuffer
        - fb_x, fb_y: position in framebuffer where the section should be drawn
        - bmp_x, bmp_y: top-left of the BMP section to draw
        - section_width, section_height: size of the section to draw
        """
        with open(path, 'rb') as f:
            # --- Read BMP header ---
            f.seek(10)
            pixel_offset = int.from_bytes(f.read(4), 'little')

            f.seek(18)
            width = int.from_bytes(f.read(4), 'little')
            height_raw = int.from_bytes(f.read(4), 'little')
            top_down = height_raw < 0
            height = abs(height_raw)

            f.seek(28)
            bpp = int.from_bytes(f.read(2), 'little')
            if bpp != 16:
                raise ValueError(f"BMP is {bpp} bpp, expected 16-bit RGB565")

            row_size_bytes = ((width * 2 + 3) // 4) * 4  # Padded row size

            # --- Loop through only needed rows ---
            for row in range(section_height):
                bmp_row = bmp_y + row
                if bmp_row < 0 or bmp_row >= height:
                    continue  # Skip rows outside image

                # BMP bottom-up adjustment
                src_row_index = bmp_row if top_down else (height - 1 - bmp_row)

                # Seek to start of the part we want in that row
                row_start = pixel_offset + src_row_index * row_size_bytes + bmp_x * 2
                f.seek(row_start)
                raw_row_data = f.read(section_width * 2)  # Only the needed columns

                # Write into framebuffer at correct position
                fb_row_index = fb_y + row
                if 0 <= fb_row_index < fb_height:
                    fb_offset = (fb_row_index * fb_width + fb_x) * 2
                    for i in range(0, len(raw_row_data), 2):
                        # Convert to big-endian in place
                        fb[fb_offset + i] = raw_row_data[i + 1]
                        fb[fb_offset + i + 1] = raw_row_data[i]
