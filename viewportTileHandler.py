from drawable import Drawable
from framebuffer import PartialFramebufferDriver
from util import *
class Viewport:
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
    
    def __init__(self, x, y, width, height, tile_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.tile_size = tile_size
        self.tiles_x=width//tile_size
        self.tiles_y=height//tile_size
        
        #Holds all sprites for every tile
        self.tile_sprite_sets = [set() for _ in range(self.tiles_x * self.tiles_y)]
        # Uses tile coordinates to track dirty tiles which need changing
        self.dirty_tiles = set()
        # The framebuffer which is used to draw to the screen
        self.drawing_framebuffer,self.byteArray=PartialFramebufferDriver.get_instance().create_framebuffer(tile_size,tile_size)
    
    def world_to_screen(self, world_x, world_y):
        return world_x - self.x, world_y - self.y
    
    def is_visible(self, drawable:Drawable):
        return not (drawable.x + drawable.w < self.x or drawable.x > self.x + self.width or drawable.y + drawable.h < self.y or drawable.y > self.y + self.height)
    
    def store_drawable_in_tiles_and_mark_dirty(self,drawable:Drawable):
        if self.is_visible(drawable):
            x0,y0 = self.tile_coordinates(drawable.x,drawable.y)
            x1,y1 = self.tile_coordinates(drawable.x+drawable.w, drawable.y+drawable.h)
            
            for tx in range(x0, x1 + 1):
                for ty in range(y0, y1 + 1):
                    self.dirty_tiles.add((tx, ty))
                    tile_sprite_set:set=self.tile_sprite_sets[self.tile_coordinates_to_tile_index(tx,ty)]
                    tile_sprite_set.add(drawable)
            return ((x0,y0),(x1,y1))
        return (None,None)
    
    def remove_drawable_in_tiles_and_mark_dirty(self,drawable:Drawable):
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
        tile_left = tile_x * self.tile_size
        tile_top = tile_y * self.tile_size
        tile_right = tile_left + self.tile_size
        tile_bottom = tile_top + self.tile_size

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
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        return self.tile_coordinates_to_tile_index(tile_x,tile_y)
    
    def tile_coordinates_to_tile_index(self,tx,ty):
        return ty*self.tiles_x + tx
    
    def tile_coordinates(self,x,y):
        # Convert pixel coords to tile coords
        tx = max(0, (x - self.x) // self.tile_size)
        ty = max(0, (y - self.y) // self.tile_size)

        return (tx,ty)
    
    def tile_coords_to_screen_coordinates(self,tx,ty):
        return (tx*self.tile_size,ty*self.tile_size)
    
    def push_changes(self):
        #Loop through all dirty tiles and redraw them, then push them to the screen
        framebufDriver=PartialFramebufferDriver.get_instance()
        for dirty_tile_coord in self.dirty_tiles:
            #clear framebuffer to prepare for drawing
            self.drawing_framebuffer.fill(rgb(0,0,0))
            #Get the set with sprites within this tile
            sprite_set:set=self.tile_sprite_sets[self.tile_coordinates_to_tile_index(*dirty_tile_coord)]
            drawable:Drawable
            x0,y0=self.tile_coords_to_screen_coordinates(*dirty_tile_coord)
            for drawable in sorted(sprite_set, key=lambda sprite:sprite.z,reverse=True):
                drawable.draw_into(self.drawing_framebuffer, *drawable.framebuffer_relative_coordinates(x0,y0))
            #Lower corner coordinates for the tile
            x1,y1=x0+self.tile_size, y0+self.tile_size
            #Set the window to focus the tile
            framebufDriver.set_window(x0,y0,x1,y1)
            #Send the bytearray contained within the framebuf
            framebufDriver.send_color_data(self.byteArray)
            
            self.dirty_tiles.clear()
            