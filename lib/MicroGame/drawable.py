from .viewportTileHandler import singleViewPort
import framebuf
from .util import *
class Image:
    """
    Loads and stores an image.
    """
    def __init__(self,src):
         """
        Load an image from a BMP file.

        Args:
            src (str): Path to the BMP file.
        """
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
    """
    A rectangle shape that can be drawn on the screen.
    """
    def __init__(self, x, y, w, h, z=0, color=rgb(255,0,0)):
        """
        Create a rectangle.

        Args:
            x (int): X position (left edge).
            y (int): Y position (top edge).
            w (int): Width in pixels.
            h (int): Height in pixels.
            z (int): Draw order (higher = drawn later).
            color (int): RGB565 color value.
        """
        super().__init__(x,y,w,h,z)
        self.color=color
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x,relative_y):
        fb.rect(relative_x, relative_y, self.w, self.h,self.color)

class Ellipse(Drawable):
    """
    An ellipse shape (circle-like) that can be drawn on the screen.
    """
    def __init__(self, x, y, radius_x, radius_y, z=0, color=rgb(0,255,0)):
        """
        Create an ellipse.

        Args:
            x (int): X position (left edge).
            y (int): Y position (top edge).
            diameter_x (int): Width of the ellipse.
            diameter_y (int): Height of the ellipse.
            z (int): Draw order (higher = drawn later).
            color (int): RGB565 color value.
        """
        super().__init__(x, y, radius_x, radius_y, z)
        self.color=color
    
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        fb.ellipse(relative_x+self.w*2,relative_y+self.h*2,self.w,self.h,self.color,True)

class SmallSprite(Drawable):
    """
    A small image that can be drawn onto the screen
    """
    def __init__(self, x, y, image:Image, z=0):
        """
        Create a small sprite.

        Args:
            x (int): X position.
            y (int): Y position.
            image (Image): The image to draw.
            z (int): Draw order.
        """
        super().__init__(x, y, image.w, image.h, z)
        self.img=image
    
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        fb.blit(self.img.fb, relative_x, relative_y,rgb(0,0,0))

class BigSprite(Drawable):
    def __init__(self, x, y, w, h, src, z=0):
        super().__init__(x, y, w, h, z)
        self.src=src
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

class Text(Drawable):
    """
    A piece of text that can be drawn on the screen.

    Each character is assumed to be 8 pixels wide and 8 pixels tall.
    """
    def __init__(self, x, y, text, color, z=0):
        """
        Create a text object.

        Args:
            x (int): X position on screen.
            y (int): Y position on screen.
            text (str): The text to display.
            color (int): RGB565 color value.
            z (int): Draw order.
        """
        self._text=text
        self.color=color
        super().__init__(x, y, len(text)*8, 8, z)
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self,other):
        self._text=other
        self.w=len(other)*8

    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        fb.text(self._text,relative_x,relative_y,self.color)
    
    


class OptimizedLine(Drawable):
    def __init__(self, x1, y1, x2, y2, z=0, color=rgb(0, 0, 255)):
        # Endpoints
        self._x1, self._y1 = x1, y1
        self._x2, self._y2 = x2, y2
        self.color = color

        # Compute initial bounding box
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        super().__init__(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1, z)

    @property
    def x1(self): return self._x1
    @x1.setter
    def x1(self, val):
        if val != self._x1:
            self._mark_partial_dirty(self._x1, self._y1, val, self._y1)
            self._x1 = val
            self._update_bbox()

    @property
    def y1(self): return self._y1
    @y1.setter
    def y1(self, val):
        if val != self._y1:
            self._mark_partial_dirty(self._x1, self._y1, self._x1, val)
            self._y1 = val
            self._update_bbox()

    @property
    def x2(self): return self._x2
    @x2.setter
    def x2(self, val):
        if val != self._x2:
            self._mark_partial_dirty(self._x2, self._y2, val, self._y2)
            self._x2 = val
            self._update_bbox()

    @property
    def y2(self): return self._y2
    @y2.setter
    def y2(self, val):
        if val != self._y2:
            self._mark_partial_dirty(self._x2, self._y2, self._x2, val)
            self._y2 = val
            self._update_bbox()

    def _update_bbox(self):
        """Recalculate full bounding box for this line."""
        min_x, max_x = min(self._x1, self._x2), max(self._x1, self._x2)
        min_y, max_y = min(self._y1, self._y2), max(self._y1, self._y2)
        self._x = min_x
        self._y = min_y
        self._w = max_x - min_x + 1
        self._h = max_y - min_y + 1
        self.has_moved = True

    def _mark_partial_dirty(self, old_x, old_y, new_x, new_y):
        """Mark tiles touched by only the changed segment as dirty and ensure drawable is in them."""
        view = singleViewPort.get_instance()

        # Determine affected bounding box
        min_x, max_x = min(old_x, new_x), max(old_x, new_x)
        min_y, max_y = min(old_y, new_y), max(old_y, new_y)

        # Mark tiles dirty
        view.mark_region_dirty(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

        # Make sure the line is present in those tiles
        x0, y0 = view.tile_coordinates(min_x, min_y)
        x1, y1 = view.tile_coordinates(max_x, max_y)
        for tx in range(x0, x1 + 1):
            for ty in range(y0, y1 + 1):
                tile_sprite_set:set = view.tile_sprite_sets[view.tile_coordinates_to_tile_index(tx, ty)]
                tile_sprite_set.add(self)

    def update(self):
        """Overrides Drawable update to avoid full re-store if only endpoints moved within same tiles."""
        view = singleViewPort.get_instance()
        if self.has_moved:
            # On first placement or if crossing tile boundaries, do full update
            if not (self.old_top_left and self.old_bottom_right):
                self.old_top_left, self.old_bottom_right = view.store_drawable_in_tiles_and_mark_dirty(self)
            else:
                # Check if full bbox change crosses new tiles
                new_tl = view.tile_coordinates(self.x, self.y)
                new_br = view.tile_coordinates(self.x + self.w, self.y + self.h)
                if new_tl != self.old_top_left or new_br != self.old_bottom_right:
                    view.remove_drawable_in_tiles_and_mark_dirty(self)
                    self.old_top_left, self.old_bottom_right = view.store_drawable_in_tiles_and_mark_dirty(self)
                else:
                    # Same tiles → only mark them dirty
                    view.mark_region_dirty(self.x, self.y, self.w, self.h)
            self.has_moved = False

    def draw_into(self, fb: framebuf.FrameBuffer, relative_x, relative_y):
        fb.line(
            self._x1 - relative_x,
            self._y1 - relative_y,
            self._x2 - relative_x,
            self._y2 - relative_y,
            self.color
        )