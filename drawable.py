
class Drawable:
    def __init__(self, x, y, w, h, color, z=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.z = z
        self._old_tiles = set()

    def mark_dirty(self):
        tiles = set()
        tx1 = self.x // TILE_W
        ty1 = self.y // TILE_H
        tx2 = (self.x + self.w - 1) // TILE_W
        ty2 = (self.y + self.h - 1) // TILE_H
        for ty in range(ty1, ty2 + 1):
            for tx in range(tx1, tx2 + 1):
                tiles.add(tile_index(tx, ty))
        for idx in tiles | self._old_tiles:
            dirty_tiles.add(idx)
        self._old_tiles = tiles

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.mark_dirty()

    def draw_into(self, fb, buf_x, buf_y):
        """Override in subclass: draw shape into given FrameBuffer"""
        pass


def tile_index(tx, ty):
    return ty * TILES_X + tx