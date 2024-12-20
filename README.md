# Motorised throttle unit v2
This is 2nd version of custom software for motorised throttle unit (MTU) this time in Circuitpython running at ESP32-S3.

# Update
Giving up with circuit python, it doesn't seem stable enough. Will continue with C version and platform.io [here](https://github.com/me2d13/mtu-pio)

Issues I had with circuitpython
- random freezes and safe mode reboots due to internal watchdog
- pins in use when used for I2C (mainly secondary, for HW with 2 buses)
- random IO error on I2C bus

# Hardware

- ESP32-S3 at module [YD-ESP32-S3 N16R8](https://circuitpython.org/board/yd_esp32_s3_n16r8/)
- MCP23017 to provide enough inputs for buttons
- MCP23017 to provide enough outputs
- CD4051BE to multiplex UART bus to control steppers through TMC2208

## Input buttons
1. Auto-throttle disconnect #1
1. Auto-throttle disconnect #2
1. TOGA #1
1. TOGA #2
1. Stab trim main select
1. Stab trim auto pilot
1. Fuel #1
1. Fuel #2
1. Parking brake
1. Horn cutoff
1. Trim indicator stop 1
1. Trim indicator stop 2
1. 12V present
1. 5V present
1. rotary A
1. rotary B
1. roatry button


## Outputs
1. Parking brake LED
1. Stepper Throttle 1 Enabled
1. Stepper Throttle 1 Direction
1. **Stepper Throttle 1 Step**
1. Stepper Throttle 2 Enabled
1. Stepper Throttle 2 Direction
1. **Stepper Throttle 2 Step**
1. Stepper Trim 1 Enabled
1. Stepper Trim 1 Direction
1. **Stepper Trim 1 Step**
1. Stepper Trim 2 Enabled
1. Stepper Trim 2 Direction
1. **Stepper Trim 2 Step**
1. Stepper Speed brake Enabled
1. Stepper Speed brake Direction
1. **Stepper Speed brake Step**
1. Stepper Trim Wheel Enabled
1. Stepper Trim Wheel Direction
1. **Stepper Trim Wheel Step**
1. **UART addr 0**
1. **UART addr 1**
1. **UART addr 2**

## PCB requested features
- 3.3V from ESP32 board or externally (when board stab would not be strong enough)
- 5V externally from 12V or from ESP32 board
