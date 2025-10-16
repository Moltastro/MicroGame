from machine import SPI, Pin
from rp2 import DMA
from uctypes import addressof
import struct

# --- SPI setup (mode 1 = CPOL 0, CPHA 1)
spi = SPI(1, baudrate=20_000_000, polarity=0, phase=0, bits=16,
          sck=Pin(10), mosi=Pin(11))  # no miso
# your DC, CS, RESET pins
dc = Pin(6, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(4, Pin.OUT)

# --- Prepare pixel data (RGB565)
# example: small 160×80 buffer
w, h = 160, 80
fb = bytearray(w * h * 2)   # 2 bytes/pixel
# fill with some test pattern
for i in range(0, len(fb), 2):
    fb[i:i+2] = struct.pack(">H", (i//2) & 0xFFFF)

# --- DMA setup
d = DMA()

# Determine DREQ index for SPI0_TX (from RP2040/2350 datasheet)
# SPI0_TX = 0x10, SPI1_TX = 0x12
DREQ_SPI1_TX = 26

# SPI0 data register address
SPI1_BASE  = 0x40088000
SSPDR_OFFSET = 0x008
SPI1_DR = SPI1_BASE + SSPDR_OFFSET

# Configure DMA:
#   size=1 → 16-bit halfwords
#   inc_read=True (advance framebuffer pointer)
#   inc_write=False (always write to SPI data register)
#   treq_sel=DREQ_SPI0_TX (pace by SPI FIFO availability)
ctrl = d.pack_ctrl(
    size=1,
    inc_read=True,
    inc_write=False,
    treq_sel=DREQ_SPI1_TX
)
CS = 9
cs=Pin(9,Pin.OUT)
cs.on()
cs.off()
# Bind DMA to framebuffer → SPI DR
d.config(
    read=fb,
    write=SPI1_DR,
    count=len(fb)//2,  # number of 16-bit transfers
    ctrl=ctrl,
    trigger=True
)

# --- Wait for completion (non-blocking option below)
while d.active():
    pass
cs.on()
# Or, if you want to queue next DMA or run callback:
# def done_irq(pin):
#     print("DMA complete")
# d.irq(done_irq)
