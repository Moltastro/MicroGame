from RevisedMicroGame.gameHandler import *
from RevisedMicroGame.displayInterface import DebugDisplay
from RevisedMicroGame.tileManager import TileManager
from RevisedMicroGame.gameObject import GameObject
from RevisedMicroGame.util import rgb
from RevisedMicroGame.drawable import Rectangle
import time 
debug=DebugDisplay(16,16)
Game=GameHandler(ScriptScheduler(),TileManager(debug,2,2),VectorMapFactory())
GameObject.bind_game_handler(Game)
rect=GameObject(Rectangle(0,0,2,2))
rect2=GameObject(Rectangle(x=3,y=1,w=1,h=1,color=rgb(233, 9, 9)))
rect2.velocity=Vec2(-1,0)
rect.velocity.x=1
rect.velocity.y=1
for i in range(10):
    start = time.ticks_ms()
    Game.update()
    print("--------------Output:-----------------")
    debug.display()
    print("--------------------------------------")
    elapsed = time.ticks_diff(time.ticks_ms(), start)
    print(f"frame took {elapsed} ms")
    time.sleep(0.5)
    
""" 
if __name__ == "__main__":
    from RevisedMicroGame.coordinateSystem import Vec2
    from RevisedMicroGame.displayInterface import DebugDisplay
    from RevisedMicroGame.byteBuffer import ByteBuffer
    import struct

    dbg = DebugDisplay(8, 4)

    # Fill a 4x2 subregion (window)
    sub_buf = ByteBuffer(Vec2(4, 2))
    for y in range(2):
        for x in range(4):
            r = int((x / 3) * 31)
            g = int((y / 1) * 63)
            b = 15
            rgb565 = (r << 11) | (g << 5) | b
            idx = (y * 4 + x) * 2
            sub_buf.buffer[idx:idx+2] = struct.pack("<H", rgb565)

    dbg.set_window(BBox(Vec2(2, 1), Vec2(4, 2)))
    dbg.send_color_data(sub_buf)

    # Show entire display (with only that window filled)
    dbg.display() """