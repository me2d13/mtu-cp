import board
import busio
from log import pdebug
from lcd_pico_lib import I2cLcd

def enumerate_i2c():
    pdebug("Enumerating i2c...")
    #i2c = board.STEMMA_I2C()  # uses board.SCL and board.SDA
    i2c = busio.I2C(board.GP1, board.GP0)
    i2c.try_lock()
    try:
        for device_address in i2c.scan():
            pdebug("Found ", hex(device_address))
    finally:
        i2c.unlock()

class Lcd:
    def __init__(self):
        self.i2c = busio.I2C(board.GP1, board.GP0)
        self.i2c.try_lock()
        try:
            self.lcd = I2cLcd(self.i2c, 0x27, 4, 20)
            self.lcd.backlight_on()
            self.lcd.clear()
            self.lcd.putstr("\n       M T U       ")
        finally:
            self.i2c.unlock()

    def write(self, what, with_clear = False):
        self.i2c.try_lock()
        try:
            if with_clear:
                self.lcd.clear()
            self.lcd.putstr(what)
        finally:
            self.i2c.unlock()

    def move_to(self, x, y):
        self.i2c.try_lock()
        try:
            self.lcd.move_to(x,y)
        finally:
            self.i2c.unlock()
