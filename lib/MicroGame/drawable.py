from .viewportTileHandler import singleViewPort
from . framebuffer import SingleFrameBufferDriver,FramebufferWrapper
import framebuf
from .util import *
import math

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
            self.fb=FramebufferWrapper(_buf,_w,_h)
            self.w=_w
            self.h=_h
        else:
            self.buffer,self.w,self.h = Image.load_bmp_rgb565(src)
            self.fb =FramebufferWrapper(self.buffer,self.w,self.h)

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



    
class Drawable:
    def __init__(self, x=0, y=0, w=0, h=0, z=0):
        self._screen_x = singleViewPort.centerX_to_screenX_coordinates(x)
        self._screen_y = singleViewPort.centerY_to_screenY_coordinates(y)
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
        return singleViewPort.screenX_to_centerX_coordinates(self._screen_x)
    
    @x.setter
    def x(self,val):
        if val !=self.x:
            self._screen_x=singleViewPort.centerX_to_screenX_coordinates(val)
            self.has_moved = True

    @property
    def y(self):
        return singleViewPort.screenY_to_centerY_coordinates(self._screen_y)
    
    @y.setter
    def y(self,val):
        if val!=self.y:
            self._screen_y=singleViewPort.centerY_to_screenY_coordinates(val)
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
        return int(self._screen_x)-buf_x,int(self._screen_y)-buf_y
    
    def __str__(self) -> str:
        return f"pos: ({self.x},{self.y})"

class Rectangle(Drawable):
    """
    A rectangle shape that can be drawn on the screen.
    """
    def __init__(self, x=0, y=0, w=30, h=30, color=rgb(255,0,0),z=0):
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
    def __init__(self, x=0, y=0, radius_x=10, radius_y=10, color=rgb(0,255,0), z=0):
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
    def __init__(self, image:Image, x=0, y=0, z=0):
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

class AnimatedSprite(Drawable):
    """
    
    """
    def __init__(self, imageList:list[Image], frame_hold_time=3, x=0, y=0, z=0):
        max_w=0
        max_h=0
        for image in imageList:
            if image.w>max_w:
                max_w=image.w
            if image.h>max_h:
                max_h=image.h
        self.image_list=imageList
        self._incr=0
        self.frame_hold_time=frame_hold_time
        super().__init__(x, y, max_w, max_h, z)
    
    def draw_into(self, fb:framebuf.FrameBuffer, relative_x, relative_y):
        current_buff=self.image_list[self.current_image_index()].fb
        fb.blit(current_buff, relative_x, relative_y,rgb(0,0,0))
    
    def current_image_index(self):
        return (self._incr//self.frame_hold_time)
    
    def update(self):
        if self._incr%self.frame_hold_time==0:
            self.has_moved=True
        if not self._incr==(len(self.image_list)-1)*self.frame_hold_time+(self.frame_hold_time-1):
            self._incr+=1
        else:
            self._incr=0
            
        
        return super().update()
    
# class BigSprite(Drawable):
#     def __init__(self, x=0, y=0, w, h, src, z=0):
#         super().__init__(x, y, w, h, z)
#         self.src=src
#     def draw_bmp_section_to_fb_be(
#     path: str,
#     fb: bytearray,
#     fb_width: int,
#     fb_height: int,
#     fb_x: int,
#     fb_y: int,
#     bmp_x: int,
#     bmp_y: int,
#     section_width: int,
#     section_height: int
#     ):
#         """
#         Draw a rectangular section of a 16-bit RGB565 BMP (big-endian) into a framebuffer.
#         - fb: framebuffer bytearray (big-endian RGB565)
#         - fb_width, fb_height: dimensions of the framebuffer
#         - fb_x, fb_y: position in framebuffer where the section should be drawn
#         - bmp_x, bmp_y: top-left of the BMP section to draw
#         - section_width, section_height: size of the section to draw
#         """
#         with open(path, 'rb') as f:
#             # --- Read BMP header ---
#             f.seek(10)
#             pixel_offset = int.from_bytes(f.read(4), 'little')

#             f.seek(18)
#             width = int.from_bytes(f.read(4), 'little')
#             height_raw = int.from_bytes(f.read(4), 'little')
#             top_down = height_raw < 0
#             height = abs(height_raw)

#             f.seek(28)
#             bpp = int.from_bytes(f.read(2), 'little')
#             if bpp != 16:
#                 raise ValueError(f"BMP is {bpp} bpp, expected 16-bit RGB565")

#             row_size_bytes = ((width * 2 + 3) // 4) * 4  # Padded row size

#             # --- Loop through only needed rows ---
#             for row in range(section_height):
#                 bmp_row = bmp_y + row
#                 if bmp_row < 0 or bmp_row >= height:
#                     continue  # Skip rows outside image

#                 # BMP bottom-up adjustment
#                 src_row_index = bmp_row if top_down else (height - 1 - bmp_row)

#                 # Seek to start of the part we want in that row
#                 row_start = pixel_offset + src_row_index * row_size_bytes + bmp_x * 2
#                 f.seek(row_start)
#                 raw_row_data = f.read(section_width * 2)  # Only the needed columns

#                 # Write into framebuffer at correct position
#                 fb_row_index = fb_y + row
#                 if 0 <= fb_row_index < fb_height:
#                     fb_offset = (fb_row_index * fb_width + fb_x) * 2
#                     for i in range(0, len(raw_row_data), 2):
#                         # Convert to big-endian in place
#                         fb[fb_offset + i] = raw_row_data[i + 1]
#                         fb[fb_offset + i + 1] = raw_row_data[i]

class Text(Drawable):
    """
    A piece of text that can be drawn on the screen.

    Each character is assumed to be 8 pixels wide and 8 pixels tall.
    """
    def __init__(self, x=0, y=0, text="Hello", color=rgb(0,0,0), z=0):
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
    
    


# class OptimizedLine(Drawable):
#     def __init__(self, x1, y1, x2, y2, z=0, color=rgb(0, 0, 255)):
#         # Endpoints
#         self._x1, self._y1 = x1, y1
#         self._x2, self._y2 = x2, y2
#         self.color = color

#         # Compute initial bounding box
#         min_x, max_x = min(x1, x2), max(x1, x2)
#         min_y, max_y = min(y1, y2), max(y1, y2)
#         super().__init__(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1, z)

#     @property
#     def x1(self): return self._x1
#     @x1.setter
#     def x1(self, val):
#         if val != self._x1:
#             self._mark_partial_dirty(self._x1, self._y1, val, self._y1)
#             self._x1 = val
#             self._update_bbox()

#     @property
#     def y1(self): return self._y1
#     @y1.setter
#     def y1(self, val):
#         if val != self._y1:
#             self._mark_partial_dirty(self._x1, self._y1, self._x1, val)
#             self._y1 = val
#             self._update_bbox()

#     @property
#     def x2(self): return self._x2
#     @x2.setter
#     def x2(self, val):
#         if val != self._x2:
#             self._mark_partial_dirty(self._x2, self._y2, val, self._y2)
#             self._x2 = val
#             self._update_bbox()

#     @property
#     def y2(self): return self._y2
#     @y2.setter
#     def y2(self, val):
#         if val != self._y2:
#             self._mark_partial_dirty(self._x2, self._y2, self._x2, val)
#             self._y2 = val
#             self._update_bbox()

#     def _update_bbox(self):
#         """Recalculate full bounding box for this line."""
#         min_x, max_x = min(self._x1, self._x2), max(self._x1, self._x2)
#         min_y, max_y = min(self._y1, self._y2), max(self._y1, self._y2)
#         self._x = min_x
#         self._y = min_y
#         self._w = max_x - min_x + 1
#         self._h = max_y - min_y + 1
#         self.has_moved = True

#     def _mark_partial_dirty(self, old_x, old_y, new_x, new_y):
#         """Mark tiles touched by only the changed segment as dirty and ensure drawable is in them."""
#         view = singleViewPort.get_instance()

#         # Determine affected bounding box
#         min_x, max_x = min(old_x, new_x), max(old_x, new_x)
#         min_y, max_y = min(old_y, new_y), max(old_y, new_y)

#         # Mark tiles dirty
#         view.mark_region_dirty(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

#         # Make sure the line is present in those tiles
#         x0, y0 = view.tile_coordinates(min_x, min_y)
#         x1, y1 = view.tile_coordinates(max_x, max_y)
#         for tx in range(x0, x1 + 1):
#             for ty in range(y0, y1 + 1):
#                 tile_sprite_set:set = view.tile_sprite_sets[view.tile_coordinates_to_tile_index(tx, ty)]
#                 tile_sprite_set.add(self)

#     def update(self):
#         """Overrides Drawable update to avoid full re-store if only endpoints moved within same tiles."""
#         view = singleViewPort.get_instance()
#         if self.has_moved:
#             # On first placement or if crossing tile boundaries, do full update
#             if not (self.old_top_left and self.old_bottom_right):
#                 self.old_top_left, self.old_bottom_right = view.store_drawable_in_tiles_and_mark_dirty(self)
#             else:
#                 # Check if full bbox change crosses new tiles
#                 new_tl = view.tile_coordinates(self.x, self.y)
#                 new_br = view.tile_coordinates(self.x + self.w, self.y + self.h)
#                 if new_tl != self.old_top_left or new_br != self.old_bottom_right:
#                     view.remove_drawable_in_tiles_and_mark_dirty(self)
#                     self.old_top_left, self.old_bottom_right = view.store_drawable_in_tiles_and_mark_dirty(self)
#                 else:
#                     # Same tiles → only mark them dirty
#                     view.mark_region_dirty(self.x, self.y, self.w, self.h)
#             self.has_moved = False

#     def draw_into(self, fb: framebuf.FrameBuffer, relative_x, relative_y):
#         fb.line(
#             self._x1 - relative_x,
#             self._y1 - relative_y,
#             self._x2 - relative_x,
#             self._y2 - relative_y,
#             self.color
#         )