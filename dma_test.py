from rp2 import DMA, PIO
from machine import SPI
d = DMA()
#18 DREQ_SPI1_TX
c = d.pack_ctrl(size=1,inc_write=False,treq_sel=18)
#SPI DTR pin:
SPI1_BASE = 0x40040000
TXDR_OFFSET = 0x008
SPI1_TXDR = SPI1_BASE+TXDR_OFFSET
from RevisedMicroGame.displayDrivers import WaveShareDisplay
from RevisedMicroGame.byteBuffer import ByteBuffer
from RevisedMicroGame.collisionShape import BBox
from RevisedMicroGame.coordinateSystem import Vec2
from RevisedMicroGame.util import rgb
lcd=WaveShareDisplay()
buf=ByteBuffer(Vec2(10,10))
buf.fill(rgb(46, 121, 207))
lcd.set_window(bbox=BBox(Vec2(0,0),Vec2(10,10)))
def send_data(buffer:ByteBuffer):
    lcd.cs(1)
    lcd.dc(1)
    lcd.cs(0)
    
    d.config(read=buf.buffer, write=SPI1_TXDR, count=len(buf.buffer)//2, ctrl=c, trigger=True)
    lcd.cs(1)
# Wait for completion
while d.active():
    pass