from state import MtuState
from joy import Joystick
from web import WebServer
from lcd import Lcd
from screen import Screen
from tmc2208 import TMC_UART
from motor import Motor
import board

class Container:
    def __init__(self, pool):
        self.state = MtuState()
        self.tmc = TMC_UART(115200)
        self.joy = Joystick()
        self.motor = Motor(self.tmc, board.GPIO17, board.GPIO18)
        self.server = WebServer(pool, self.joy, self.motor)
        self.screen = Screen(Lcd(), self.state)

#tmc.test_uart(0x02)
#pdebug("GCONF", tmc.read_int(0))

