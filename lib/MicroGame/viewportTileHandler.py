from .framebuffer import SingleFrameBufferDriver,FramebufferWrapper
from .util import *
from collections import deque
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
    
    def __init__(self, x, y, width, height, am_buffer_tiles=1, tile_size=None,tiles_x=None,tiles_y=None,tile_size_x=None,tile_size_y=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if tile_size!=None:
            self.tile_size_x = tile_size
            self.tile_size_y = tile_size
            self.tiles_x=width // tile_size
            self.tiles_y=height // tile_size
        elif tiles_x!=None and tiles_y:
            self.tiles_x=tiles_x
            self.tiles_y=tiles_y
            self.tile_size_x=width//tiles_x
            self.tile_size_y=height//tiles_y
        elif tile_size_x!=None and tile_size_y!=None:
            self.tile_size_x=tile_size_x
            self.tile_size_y=tile_size_y
            self.tiles_x=width // tile_size_x
            self.tiles_y=height // tile_size_y
        
        print(f"tile_size: {self.tile_size_x,self.tile_size_y},tile am: {self.tiles_x,self.tiles_y}")
        #Holds all sprites for every tile
        self.tile_sprite_sets = [set() for _ in range(self.tiles_x * self.tiles_y)]
        # Uses tile coordinates to track dirty tiles which need changing
        self.dirty_tiles = set()
        # The framebuffer which is used to draw to the screen
        print("Creating")
        self.available_framebuffers=deque([],am_buffer_tiles)
        print("Has created")
        self.queued_framebuffers=deque([],am_buffer_tiles-1)
        self.am_buffer_tiles=am_buffer_tiles
        for _ in range(self.am_buffer_tiles):
            framebuffer=SingleFrameBufferDriver.create_framebuffer(int(self.tile_size_x),int(self.tile_size_y))
            self.available_framebuffers.append(framebuffer)
        print(f"len framewrapper {len(self.available_framebuffers)}")
        
        self.draw_entire_screen()
    
    def world_to_screen(self, world_x, world_y):
        return world_x - self.x, world_y - self.y
    
    def is_visible(self, drawable:"Drawable"):
        return not (drawable.x + drawable.w < self.x or drawable.x > self.x + self.width or drawable.y + drawable.h < self.y or drawable.y > self.y + self.height)
    
    def store_drawable_in_tiles_and_mark_dirty(self,drawable:"Drawable"):
        """Stores the drawable in the tiles it is visible in and marks those tiles dirty, 
        returns the bbox coordinates of the tile it was in or None if not visible
        """
        if self.is_visible(drawable):
            x0,y0 = self.tile_coordinates(drawable.x,drawable.y)
            x1,y1 = self.tile_coordinates(drawable.x+drawable.w, drawable.y+drawable.h)
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
        return ty*self.tiles_x + tx
    
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
            #Draw tile
            fb = self.draw_tile(*dirty_tile_coord)
            #If queue is not full pass this statement
            if len(self.queued_framebuffers) > self.am_buffer_tiles - 1 or not SingleFrameBufferDriver.dma_busy():
                #Dma is ready for more, set new current and add the old to available framebuffers to draw to
                self.send_next_in_queue()

            self.queued_framebuffers.append(fb)

        #If there are queued framebuffers waiting to be sent go through all of them
        while len(self.queued_framebuffers):
            self.send_next_in_queue()

        self.dirty_tiles.clear()

    def send_next_in_queue(self):
        fb:FramebufferWrapper=self.queued_framebuffers.popleft()
        SingleFrameBufferDriver.show_region(fb.x,fb.y,self.tile_size_x,self.tile_size_y,fb.buffer)
        self.available_framebuffers.append(fb)
        
    def draw_tile(self,tx,ty):
        framebuffer:FramebufferWrapper=self.available_framebuffers.popleft()
        framebuffer.fill(rgb(0,0,0))
        #Get the set with sprites within this tile
        sprite_set:set=self.tile_sprite_sets[self.tile_coordinates_to_tile_index(tx,ty)]
        drawable:"Drawable"
        x0,y0=self.tile_coords_to_screen_coordinates(tx,ty)
        for drawable in sorted(sprite_set, key=lambda sprite:sprite.z,reverse=True):
            drawable.draw_into(framebuffer, *drawable.framebuffer_relative_coordinates(x0,y0))
        #Set the window to focus the tile
        framebuffer.x,framebuffer.y=x0,y0
        return framebuffer
        SingleFrameBufferDriver.set_window(x0,y0,self.tile_size_x,self.tile_size_y)
        #Send the bytearray contained within the framebuf
        SingleFrameBufferDriver.send_color_data(self.byteArray)

    def draw_entire_screen(self):
        for tx in range(self.tiles_x):
            for ty in range(self.tiles_y):
                fb=self.draw_tile(tx,ty)
                SingleFrameBufferDriver.spi_show_region(*self.tile_coords_to_screen_coordinates(tx,ty),self.tile_size_x,self.tile_size_y,fb)
                self.available_framebuffers.append(fb)

singleViewPort=ViewPort(0,0,240,300,tiles_x=1,tiles_y=15)