from .framebuffer import SingleFrameBufferDriver
from .util import *
class ViewPort:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(0,0,240,300,30)
        return cls._instance
    
    def __init__(self, x, y, width, height, tile_size=None,tiles_x=None,tiles_y=None,tile_size_x=None,tile_size_y=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if tile_size!=None:
            self.tile_size_x = tile_size
            self.tile_size_y = tile_size
            self.tiles_x=width//tile_size
            self.tiles_y=height//tile_size
        elif tiles_x!=None and tiles_y:
            self.tiles_x=tiles_x
            self.tiles_y=tiles_y
            self.tile_size_x=width//tiles_x
            self.tile_size_y=height//tiles_y
        elif tile_size_x!=None and tile_size_y!=None:
            self.tile_size_x=tile_size_x
            self.tile_size_y=tile_size_y
            self.tiles_x=width//tile_size_x
            self.tiles_y=height//tile_size_y
        
        self._backgroundC=rgb(255,255,255)
        #Holds all sprites for every tile
        self.tile_sprite_sets = [set() for _ in range(self.tiles_x * self.tiles_y)]
        # Uses tile coordinates to track dirty tiles which need changing
        self.dirty_tiles = set()
        # The framebuffer which is used to draw to the screen
        self.drawing_framebuffer=SingleFrameBufferDriver.create_framebuffer(self.tile_size_x,self.tile_size_y)
        self.draw_entire_screen()
    
    @property
    def backgroundColor(self):
        return self._backgroundC
    
    @backgroundColor.setter
    def backgroundColor(self,other):
        self._backgroundC=other
        self.draw_entire_screen()
    def mark_region_dirty(self, x, y, w, h):
        """Mark all tiles overlapped by given region as dirty."""
        x0, y0 = self.tile_coordinates(x, y)
        x1, y1 = self.tile_coordinates(x + w, y + h)
        x0 = max(0, min(x0, self.tiles_x - 1))
        x1 = max(0, min(x1, self.tiles_x - 1))
        y0 = max(0, min(y0, self.tiles_y - 1))
        y1 = max(0, min(y1, self.tiles_y - 1))
        for tx in range(x0, x1 + 1):
            for ty in range(y0, y1 + 1):
                self.dirty_tiles.add((tx, ty))
        
    def world_to_screen(self, world_x, world_y):
        return world_x - self.x, world_y - self.y
    
    def is_visible(self, drawable:"Drawable"):
        return not (drawable._screen_x + drawable.w < self.x or drawable._screen_x > self.x + self.width or drawable._screen_y + drawable.h < self.y or drawable._screen_y > self.y + self.height)
    
    def store_drawable_in_tiles_and_mark_dirty(self,drawable:"Drawable"):
        """Stores the drawable in the tiles it is visible in and marks those tiles dirty, 
        returns the bbox coordinates of the tile it was in or None if not visible
        """
        if self.is_visible(drawable):
            draw_x,draw_y,draw_w,draw_h=int(drawable._screen_x),int(drawable._screen_y),int(drawable.w),int(drawable.h)
            x0,y0 = self.tile_coordinates(draw_x,draw_y)
            x1,y1 = self.tile_coordinates(draw_x+draw_w, draw_y+draw_h)
            x0 = max(0, min(x0, self.tiles_x-1))
            x1 = max(0, min(x1, self.tiles_x-1))
            y0 = max(0, min(y0, self.tiles_y-1))
            y1 = max(0, min(y1, self.tiles_y-1))
            for tx in range(x0, x1 + 1):
                for ty in range(y0, y1 + 1):
                    self.dirty_tiles.add((tx, ty))
                    tile_sprite_set:set=self.tile_sprite_sets[self.tile_coordinates_to_tile_index(tx,ty)]
                    tile_sprite_set.add(drawable)
            return ((x0,y0),(x1,y1))
        return (None,None)
    
    def remove_drawable_in_tiles_and_mark_dirty(self,drawable:"Drawable"):
        if drawable.old_bottom_right and drawable.old_top_left:
            for tx in range(drawable.old_top_left[0],drawable.old_bottom_right[0]+1): # type: ignore
                for ty in range(drawable.old_top_left[1],drawable.old_bottom_right[1]+1): # type: ignore
                    tile_sprite_set:set=self.tile_sprite_sets[self.tile_index(tx,ty)]
                    tile_sprite_set.discard(drawable)
                    self.dirty_tiles.add((tx,ty))
    
    def clear_dirty(self):
        self.dirty_tiles.clear()
    
    def box_overlaps_tile(self, x, y, w, h, tile_x, tile_y):
        # Tile bounds
        tile_left = tile_x * self.tile_size_x
        tile_top = tile_y * self.tile_size_y
        tile_right = tile_left + self.tile_size_x
        tile_bottom = tile_top + self.tile_size_y

        # Drawable bounds
        drawable_left = x
        drawable_top = y
        drawable_right = x + w
        drawable_bottom = y + h

        # Check for no overlap conditions, then invert
        no_overlap = (
            drawable_right <= tile_left or
            drawable_left >= tile_right or
            drawable_bottom <= tile_top or
            drawable_top >= tile_bottom
        )
        return not no_overlap

    def tile_index(self, x, y):
        # Convert pixel coords to tile index
        tile_x = x // self.tile_size_x
        tile_y = y // self.tile_size_y
        return self.tile_coordinates_to_tile_index(tile_x,tile_y)
    
    def tile_coordinates_to_tile_index(self,tx,ty):
        return int(ty*self.tiles_x + tx)
    
    def tile_coordinates(self,x,y):
        # Convert pixel coords to tile coords
        tx = max(0, (x - self.x) // self.tile_size_x)
        ty = max(0, (y - self.y) // self.tile_size_y)

        return (tx,ty)
    
    def tile_coords_to_screen_coordinates(self,tx,ty):
        return (tx*self.tile_size_x,ty*self.tile_size_y)
    
    def push_changes(self):
        debug(f"Current dirty tiles {self.dirty_tiles}")
        #Loop through all dirty tiles and redraw them, then push them to the screen
        for dirty_tile_coord in self.dirty_tiles:
            debug(f"Drawing to tile coord {dirty_tile_coord}")
            
            self.draw_tile(*dirty_tile_coord)
            
        self.dirty_tiles.clear()
    
    def screenX_to_centerX_coordinates(self,x):
        return x-self.width/2
    def centerX_to_screenX_coordinates(self,x):
        return x+self.width/2
    def screenY_to_centerY_coordinates(self,y):
        return self.height/2-y
    def centerY_to_screenY_coordinates(self,y):
        return self.height/2-y
    
    def draw_tile(self,tx,ty):
        self.drawing_framebuffer.fill(self.backgroundColor)
        #Get the set with sprites within this tile
        sprite_set:set=self.tile_sprite_sets[self.tile_coordinates_to_tile_index(tx,ty)]
        drawable:"Drawable"
        x0,y0=self.tile_coords_to_screen_coordinates(tx,ty)
        for drawable in sorted(sprite_set, key=lambda sprite:sprite.z):
            drawable.draw_into(self.drawing_framebuffer, *drawable.framebuffer_relative_coordinates(x0,y0))
        #Set the window to focus the tile
        SingleFrameBufferDriver.set_window(x0,y0,self.tile_size_x,self.tile_size_y)
        #Send the bytearray contained within the framebuf
        SingleFrameBufferDriver.send_color_data(self.drawing_framebuffer.buffer)

    def draw_entire_screen(self):
        for tx in range(self.tiles_x):
            for ty in range(self.tiles_y):
                self.draw_tile(tx,ty)

singleViewPort=ViewPort(0,0,240,300,tiles_x=12,tiles_y=1)