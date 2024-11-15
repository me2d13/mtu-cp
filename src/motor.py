import tmc2208
from log import pdebug
import math
import digitalio
import time

DEFAULT_MICRO_STEPS = 8

class Motor:
    def __init__(self, tmc_uart: tmc2208.TMC_UART, step_pin, dir_pin):
        self.tmc_uart = tmc_uart
        self.step_pin = digitalio.DigitalInOut(step_pin)
        self.step_pin.direction = digitalio.Direction.OUTPUT
        self.dir_pin = digitalio.DigitalInOut(dir_pin)
        self.dir_pin.direction = digitalio.Direction.OUTPUT
        self.ihold = 0
        self.irun = 0
        self.steps_to_do = 0
        self.rpm = 0
        self.microsteps = DEFAULT_MICRO_STEPS
        self.step_delay_ms = 0
        self.next_pulse_ms = 0

    def init(self):
        self.set_current(1,1)
        self.set_microsteps(DEFAULT_MICRO_STEPS)
        return "Motor init OK"

    def collect_data(self):
        gconf = self.tmc_uart.read_int(tmc2208.GCONF)
        ifcnt = self.tmc_uart.read_int(tmc2208.IFCNT)
        return {
            "GCONF": bin(gconf),
            "IFCNT": ifcnt,
            }

    def set_current(self, ihold, irun, ihold_delay = 0):
        self.ihold = ihold
        self.irun = irun
        return self.set_just_current(ihold, irun)

    def set_just_current(self, ihold, irun, ihold_delay = 0):
        # bit 4-0  IHOLD 0-31
        # bit 12-8 IRUN 0-31
        # bit 19-16 IHOLDDELAY 
        ihold_irun = 0
        ihold_irun = ihold_irun | ihold << 0
        ihold_irun = ihold_irun | irun << 8
        ihold_irun = ihold_irun | ihold_delay << 16
        pdebug(f"ihold_irun: {hex(ihold_irun)}")
        return self.tmc_uart.write_reg_check(tmc2208.IHOLD_IRUN, ihold_irun)        


    def set_microsteps(self, number_of_steps):
        chopconf = self.tmc_uart.read_int(tmc2208.CHOPCONF)
        #setting all bits to zero
        chopconf = chopconf & (~tmc2208.msres0 & ~tmc2208.msres1 &
                                ~tmc2208.msres2 & ~tmc2208.msres3)
        msresdezimal = int(math.log(number_of_steps, 2))
        msresdezimal = 8 - msresdezimal
        chopconf = chopconf | msresdezimal <<24
        pdebug(f"writing {number_of_steps} microstep setting")
        self.tmc_uart.write_reg_check(tmc2208.CHOPCONF, chopconf)
        self.microstep = number_of_steps
        self.set_mstep_resolution_reg_select(True)

    def set_mstep_resolution_reg_select(self, en):
        """sets the register bit "mstep_reg_select" to 1 or 0 depending to the given value.
        this is needed to set the microstep resolution via UART
        this method is called by "set_microstepping_resolution"

        Args:
            en (bool): true to set µstep resolution via UART
        """
        gconf = self.tmc_uart.read_int(tmc2208.GCONF)

        if en is True:
            gconf = self.tmc_uart.set_bit(gconf, tmc2208.mstep_reg_select)
        else:
            gconf = self.tmc_uart.clear_bit(gconf, tmc2208.mstep_reg_select)

        pdebug(f"writing MStep Reg Select: {en}")
        self.tmc_uart.write_reg_check(tmc2208.GCONF, gconf)

    def move(self, steps, rpm):
        self.dir_pin.value = (steps > 0)
        self.steps_to_do = abs(steps)
        self.rpm = rpm
        if (rpm == 0):
            self.step_delay_ms = 0
            self.next_pulse_ms = 0
        else:
            self.calculate_step_delay()
        self.make_step()
        now = time.monotonic_ns() // 1_000_000
        self.next_pulse_ms = now + self.step_delay_ms
        pdebug(f"Starting move at {now}, steps to be done {self.steps_to_do}, next step at {self.next_pulse_ms}")
        return "OK"

    def make_step(self):
        self.step_pin.value = True
        self.step_pin.value = False

    def check_step(self):
        if self.steps_to_do > 0:
            now = time.monotonic_ns() // 1_000_000
            if now >= self.next_pulse_ms:
                #pdebug(f"Making step at {now}")
                self.make_step()
                self.next_pulse_ms = now + self.step_delay_ms
                self.steps_to_do -= 1

    def run_with_speed(self, speed):
        self.tmc_uart.write_reg_check(tmc2208.VACTUAL, speed)
        return "OK"

    def hold(self, val):
        if (val == "1"):
            self.set_just_current(self.ihold, self.irun)
        else:
            self.set_just_current(0, self.irun)
        return f"Motor set to hold {val}"

    def calculate_step_delay(self, steps_per_revolution=200):
        # Calculate effective steps per revolution with microstepping
        effective_steps_per_revolution = steps_per_revolution * self.microsteps
        # Calculate steps per second
        steps_per_second = (self.rpm * effective_steps_per_revolution) / 60
        # Calculate delay in milliseconds
        self.step_delay_ms = 1000 / steps_per_second
        pdebug(f"Step delay calculated to {self.step_delay_ms}, steps per second {steps_per_second}")
