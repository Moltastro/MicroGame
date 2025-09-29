from .displayInterface import DisplayInterface
from .byteBuffer import ByteBuffer
from machine import Pin, SPI, PWM
from .collisionShape import BBox
import time
DC = 8
CS = 9
SCK = 10
MOSI = 11
RST = 12
BL = 13

DEBUG = False

class WaveShareDisplay(DisplayInterface):
    def __init__(self, width=240, height=300):
        super().__init__(width,height)
        if DEBUG: print(f"[WaveShareDisplay] Initializing display {width}x{height}")
        self.width = width
        self.height = height

        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)

        self.cs(1)
        self.spi = SPI(1, 20_000_000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI))
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        # Initialize display hardware
        self.init_display()
        self.pwm = PWM(Pin(BL))
        self.pwm.freq(5000)
        self.pwm.duty_u16(65535) 

    def write_cmd(self, cmd):
        if DEBUG: print(f"[WaveShareDisplay] Write CMD: {cmd:#04x}")
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, data):
        if DEBUG: print(f"[WaveShareDisplay] Write DATA: {data}")
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([data]) if isinstance(data, int) else data)
        self.cs(1)

    def set_window(self, bbox:BBox):
        x,y=bbox.pos.toInt()
        w,h=bbox.size.toInt()
        if DEBUG: print(f"[WaveShareDisplay] Set window x={x}, y={y}, w={w}, h={h}")
        # Set column address
        self.write_cmd(0x2A)
        self.write_data(bytearray([x >> 8, x & 0xFF, (x + w - 1) >> 8, (x + w - 1) & 0xFF]))

        # Set row address
        self.write_cmd(0x2B)
        self.write_data(bytearray([y >> 8, y & 0xFF, (y + h - 1) >> 8, (y + h - 1) & 0xFF]))

        # Write memory command
        self.write_cmd(0x2C)

    def send_color_data(self, buffer:ByteBuffer):
        data=buffer.buffer
        if DEBUG: print(f"[WaveShareDisplay] Send color data, len={len(data) if hasattr(data,'__len__') else 1}")
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([data]) if isinstance(data, int) else data)
        self.cs(1)

    def set_bl_pwm(self, duty):
        if DEBUG: print(f"[WaveShareDisplay] Set BL PWM: {duty}")
        self.pwm.duty_u16(duty)

    def show_region(self,bbox:BBox, buf:ByteBuffer):
        # Push the framebuffer region to the display at (x, y)
        self.set_window(bbox)
        self.send_color_data(buf)

    def init_display(self):
        if DEBUG: print("[WaveShareDisplay] Initializing display hardware")
        """Initialize dispaly"""  
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        time.sleep(0.05)
        
        self.write_cmd(0x36)
        self.write_data(0x08)

        self.write_cmd(0xfd)
        self.write_data(0x06)
        self.write_data(0x08)

        self.write_cmd(0x61)
        self.write_data(0x07)
        self.write_data(0x04)

        self.write_cmd(0x62)
        self.write_data(0x00)
        self.write_data(0x44)
        self.write_data(0x45)

        self.write_cmd(0x63)
        self.write_data(0x41)
        self.write_data(0x07)
        self.write_data(0x12)
        self.write_data(0x12)

        self.write_cmd(0x64)
        self.write_data(0x37)

        self.write_cmd(0x65)
        self.write_data(0x09)
        self.write_data(0x10)
        self.write_data(0x21)
        
        self.write_cmd(0x66) 
        self.write_data(0x09) 
        self.write_data(0x10) 
        self.write_data(0x21)
        
        self.write_cmd(0x67)
        self.write_data(0x20)
        self.write_data(0x40)

        
        self.write_cmd(0x68)
        self.write_data(0x90)
        self.write_data(0x4c)
        self.write_data(0x7C)
        self.write_data(0x66)

        self.write_cmd(0xb1)
        self.write_data(0x0F)
        self.write_data(0x02)
        self.write_data(0x01)

        self.write_cmd(0xB4)
        self.write_data(0x01) 
        
        self.write_cmd(0xB5)
        self.write_data(0x02)
        self.write_data(0x02)
        self.write_data(0x0a)
        self.write_data(0x14)

        self.write_cmd(0xB6)
        self.write_data(0x04)
        self.write_data(0x01)
        self.write_data(0x9f)
        self.write_data(0x00)
        self.write_data(0x02)

        self.write_cmd(0xdf)
        self.write_data(0x11)

        self.write_cmd(0xE2)	
        self.write_data(0x13)
        self.write_data(0x00) 
        self.write_data(0x00)
        self.write_data(0x30)
        self.write_data(0x33)
        self.write_data(0x3f)

        self.write_cmd(0xE5)	
        self.write_data(0x3f)
        self.write_data(0x33)
        self.write_data(0x30)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x13)

        self.write_cmd(0xE1)	
        self.write_data(0x00)
        self.write_data(0x57)

        self.write_cmd(0xE4)	
        self.write_data(0x58)
        self.write_data(0x00)

        self.write_cmd(0xE0)
        self.write_data(0x01)
        self.write_data(0x03)
        self.write_data(0x0e)
        self.write_data(0x0e)
        self.write_data(0x0c)
        self.write_data(0x15)
        self.write_data(0x19)

        self.write_cmd(0xE3)	
        self.write_data(0x1a)
        self.write_data(0x16)
        self.write_data(0x0C)
        self.write_data(0x0f)
        self.write_data(0x0e)
        self.write_data(0x0d)
        self.write_data(0x02)
        self.write_data(0x01)
        
        self.write_cmd(0xE6)
        self.write_data(0x00)
        self.write_data(0xff)

        self.write_cmd(0xE7)
        self.write_data(0x01)
        self.write_data(0x04)
        self.write_data(0x03)
        self.write_data(0x03)
        self.write_data(0x00)
        self.write_data(0x12)

        self.write_cmd(0xE8) 
        self.write_data(0x00) 
        self.write_data(0x70) 
        self.write_data(0x00)
        
        self.write_cmd(0xEc)
        self.write_data(0x52)

        self.write_cmd(0xF1)
        self.write_data(0x01)
        self.write_data(0x01)
        self.write_data(0x02)


        self.write_cmd(0xF6)
        self.write_data(0x09)
        self.write_data(0x10)
        self.write_data(0x00)
        self.write_data(0x00)

        self.write_cmd(0xfd)
        self.write_data(0xfa)
        self.write_data(0xfc)

        self.write_cmd(0x3a)
        self.write_data(0x05)

        self.write_cmd(0x35)
        self.write_data(0x00)


        self.write_cmd(0x21)

        self.write_cmd(0x11)
        time.sleep(0.2)
        self.write_cmd(0x29)
        time.sleep(0.01)

    def __repr__(self):
        return f"WaveShareDisplay(width={self.bbox.size.x}, height={self.bbox.size.y})"