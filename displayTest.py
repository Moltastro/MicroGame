from RevisedRenderPipeline.displayDrivers import WaveShareDisplay
from RevisedRenderPipeline.byteBuffer import ByteBuffer
from RevisedRenderPipeline.collisionShape import AABB
from RevisedRenderPipeline.coordinateSystem import Vec2
from RevisedRenderPipeline.util import rgb
from RevisedRenderPipeline.renderer import Renderer


buf=ByteBuffer(Vec2(100,100))
buf.fill(rgb(39, 212, 68))
disp=WaveShareDisplay()
rend=Renderer(2, 2,disp)
rend.draw(rgb(72, 255, 0),[])
#y offset is 20
disp.show_region(AABB(Vec2(160,180),Vec2(100,100)),buf)