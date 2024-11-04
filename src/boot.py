import usb_hid
import supervisor

# Define custom VID, PID, product name, and manufacturer
CUSTOM_VID = 0xDDFD  # Non-registered VID
CUSTOM_PID = 0x5051  # Non-registered PID
PRODUCT_NAME = "MTU_v1"
MANUFACTURER_NAME = "Me2d"

# Set USB identification
supervisor.set_usb_identification(vid=CUSTOM_VID, pid=CUSTOM_PID, manufacturer=MANUFACTURER_NAME, product=PRODUCT_NAME)

# 6axes, 12 buttons

# 73 items, 151 bytes


MTU_REPORT_DESCRIPTOR = bytes((
    0x05, 0x01,                    # USAGE_PAGE (Generic Desktop)
    0x09, 0x04,                    # USAGE (Joystick)
    0xa1, 0x01,                    # COLLECTION (Application)
    0x85, 0x05,                    #   REPORT_ID (5)
    0x05, 0x09,                    #   USAGE_PAGE (Button)
    0x19, 0x01,                    #   USAGE_MINIMUM (Button 1)
    0x29, 0x10,                    #   USAGE_MAXIMUM (Button 16)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x25, 0x01,                    #   LOGICAL_MAXIMUM (1)
    0x75, 0x01,                    #   REPORT_SIZE (1)
    0x95, 0x10,                    #   REPORT_COUNT (16)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0x09, 0x30,                    #   USAGE (X)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x26, 0x00, 0x0f,              #   LOGICAL_MAXIMUM (4095)
    0x75, 0x0c,                    #   REPORT_SIZE (12)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x75, 0x04,                    #   REPORT_SIZE (4)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x03,                    #   INPUT (Cnst,Var,Abs)
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0x09, 0x31,                    #   USAGE (Y)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x26, 0x00, 0x0f,              #   LOGICAL_MAXIMUM (4095)
    0x75, 0x0c,                    #   REPORT_SIZE (12)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x75, 0x04,                    #   REPORT_SIZE (4)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x03,                    #   INPUT (Cnst,Var,Abs)
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0x09, 0x32,                    #   USAGE (Z)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x26, 0x00, 0x0f,              #   LOGICAL_MAXIMUM (4095)
    0x75, 0x0c,                    #   REPORT_SIZE (12)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x75, 0x04,                    #   REPORT_SIZE (4)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x03,                    #   INPUT (Cnst,Var,Abs)
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0x09, 0x33,                    #   USAGE (Rx)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x26, 0x00, 0x0f,              #   LOGICAL_MAXIMUM (4095)
    0x75, 0x0c,                    #   REPORT_SIZE (12)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x75, 0x04,                    #   REPORT_SIZE (4)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x03,                    #   INPUT (Cnst,Var,Abs)
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0x09, 0x34,                    #   USAGE (Ry)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x26, 0x00, 0x0f,              #   LOGICAL_MAXIMUM (4095)
    0x75, 0x0c,                    #   REPORT_SIZE (12)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x75, 0x04,                    #   REPORT_SIZE (4)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x03,                    #   INPUT (Cnst,Var,Abs)
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0x09, 0x35,                    #   USAGE (Rz)
    0x15, 0x00,                    #   LOGICAL_MINIMUM (0)
    0x26, 0x00, 0x0f,              #   LOGICAL_MAXIMUM (4095)
    0x75, 0x0c,                    #   REPORT_SIZE (12)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x02,                    #   INPUT (Data,Var,Abs)
    0x75, 0x04,                    #   REPORT_SIZE (4)
    0x95, 0x01,                    #   REPORT_COUNT (1)
    0x81, 0x03,                    #   INPUT (Cnst,Var,Abs)
    0xc0                           #               END_COLLECTION
))

mtu_device = usb_hid.Device(
    report_descriptor=MTU_REPORT_DESCRIPTOR,
    usage_page=0x01,           # Generic Desktop Control
    usage=0x04,                # Joystick
    report_ids=(5,),           # Descriptor uses report ID 5.
    in_report_lengths=(14,),    # This joy sends 14 bytes in its report.
    out_report_lengths=(0,),   # It does not receive any reports.
)

usb_hid.set_interface_name(PRODUCT_NAME)

usb_hid.enable(
    (usb_hid.Device.KEYBOARD,
     usb_hid.Device.MOUSE,
     usb_hid.Device.CONSUMER_CONTROL,
     mtu_device)
)

print("USB hid enabled")

