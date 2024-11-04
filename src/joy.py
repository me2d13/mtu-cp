import struct
import time

import usb_hid
import random

def get_device() -> usb_hid.Device:
    """Find a Joystick device in the list of active USB HID devices."""
    for device in usb_hid.devices:
        if (
            device.usage_page == 0x01
            and device.usage == 0x04
            and hasattr(device, "send_report")
        ):
            return device
    raise ValueError("Could not find Joystick HID device - check boot.py.)")

class Joystick:

    def __init__(self):
        self._joy_device = get_device()
        self._report = bytearray(14)

        # Remember the last report as well, so we can avoid sending
        # duplicate reports.
        self._last_report = bytearray(14)

        # Store settings separately before putting into report. Saves code
        # especially for buttons.
        self._buttons_state = 0
        self._joy_x = 0
        self._joy_y = 0
        self._joy_z = 0
        self._joy_r_x = 0
        self._joy_r_y = 0
        self._joy_r_z = 0

        # Send an initial report to test if HID device is ready.
        # If not, wait a bit and try once more.
        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def press_buttons(self, *buttons):
        """Press and hold the given buttons."""
        for button in buttons:
            self._buttons_state |= 1 << self._validate_button_number(button) - 1

    def release_buttons(self, *buttons):
        """Release the given buttons."""
        for button in buttons:
            self._buttons_state &= ~(1 << self._validate_button_number(button) - 1)

    def release_all_buttons(self):
        """Release all the buttons."""
        self._buttons_state = 0

    def click_buttons(self, *buttons):
        """Press and release the given buttons."""
        self.press_buttons(*buttons)
        self.release_buttons(*buttons)

    def move_joysticks(self, x=None, y=None, z=None, r_x=None, r_y=None, r_z=None):
        """Set and send the given joystick values.

        Examples::

            # Change x and y values only.
            gp.move_joysticks(x=100, y=-50)

            # Reset all joystick values to center position.
            gp.move_joysticks(0, 0, 0, 0)
        """
        if x is not None:
            self._joy_x = self._validate_joystick_value(x)
        if y is not None:
            self._joy_y = self._validate_joystick_value(y)
        if z is not None:
            self._joy_z = self._validate_joystick_value(z)
        if r_x is not None:
            self._joy_r_x = self._validate_joystick_value(r_x)
        if r_y is not None:
            self._joy_r_y = self._validate_joystick_value(r_y)
        if r_z is not None:
            self._joy_r_z = self._validate_joystick_value(r_z)

    def reset_all(self):
        """Release all buttons and set joysticks to zero."""
        self._buttons_state = 0
        self._joy_x = 0
        self._joy_y = 0
        self._joy_z = 0
        self._joy_r_x = 0
        self._joy_r_y = 0
        self._joy_r_z = 0

    def demo(self):
        self.move_joysticks(
            random.randint(0, 4095),
            random.randint(0, 4095),
            random.randint(0, 4095),
            random.randint(0, 4095),
            random.randint(0, 4095),
            random.randint(0, 4095),
            )
        self._buttons_state = random.randint(0, 0xffff)


    def send(self, always=False):
        """Send a report with all the existing settings.
        If ``always`` is ``False`` (the default), send only if there have been changes.
        """
        struct.pack_into(
            "<HHHHHHH",
            self._report,
            0,
            self._buttons_state,
            self._joy_x,
            self._joy_y,
            self._joy_z,
            self._joy_r_x,
            self._joy_r_y,
            self._joy_r_z,
        )

        if always or self._last_report != self._report:
            self._joy_device.send_report(self._report)
            # Remember what we sent, without allocating new storage.
            self._last_report[:] = self._report

    @staticmethod
    def _validate_button_number(button):
        if not 0 <= button <= 15:
            raise ValueError("Button number must in range 0 to 15")
        return button

    @staticmethod
    def _validate_joystick_value(value):
        if not 0 <= value <= 4095:
            raise ValueError("Joystick value must be in range 0 to 4095, tried " + str(value))
        return value
