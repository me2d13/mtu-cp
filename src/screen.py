from tools import format_datetime
import time
import state

class Screen:
    def __init__(self, lcd, state):
        self.lcd = lcd
        self.state = state
        self.current_screen = "ABOUT"

    def render(self):
        if (self.current_screen == "ABOUT"):
            return self.render_about()

    def render_about(self):
        self.lcd.move_to(0,0)
        self.lcd.write("IP: ")
        self.lcd.write(self.state.get(state.SK_IP_ADDRESS))
        self.lcd.move_to(0,3)
        self.lcd.write(format_datetime(time.localtime()))
        return 1
