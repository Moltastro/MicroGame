from rp2040 import LCD_1inch83
from time import sleep
LCD = LCD_1inch83()
LCD.set_bl_pwm(65535)

LCD.fill(LCD.white)


LCD.show()