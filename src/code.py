import board
import digitalio
import os
import ipaddress
import wifi
import socketpool
from log import pdebug, log_memory
from mtu_time import set_time_from_ntp
from asyncio import create_task, gather, run, sleep as async_sleep
from lcd import enumerate_i2c
from container import Container
import state

#led = digitalio.DigitalInOut(board.LED)
#led.direction = digitalio.Direction.OUTPUT

# neopixel not working until connected, see https://github.com/orgs/micropython/discussions/11097
#led = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.6, auto_write=True, pixel_order=neopixel.GRB)

print("Connecting to WiFi")
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
pdebug("Connected to WiFi" )
pool = socketpool.SocketPool(wifi.radio)
set_time_from_ntp(pool)

#enumerate_i2c()

container = Container(pool)

pdebug("Starting web server...")
container.server.start()

#  prints MAC address to REPL
pdebug("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
pdebug("My IP address is", wifi.radio.ipv4_address)
log_memory()

container.state.put(state.SK_IP_ADDRESS, str(wifi.radio.ipv4_address))

async def handle_http_requests():
    while True:
        container.server.poll()
        await async_sleep(0)

async def send_http_logs():
    while True:
        #log_memory()
        container.server.send_logs_if_needed()
        await async_sleep(1)

async def led_blicks():
    while True:
        #led.value = True
        led[0] = (0x10, 0, 0)
        #led.show()
        await async_sleep(0.2)
        #led.value = False
        #led[0] = (0, 0, 0)
        await async_sleep(1)

async def screen_task():
    while True:
        # for now make it simple, no change screen trigger
        wait_time = container.screen.render()
        await async_sleep(wait_time)

async def motors_task():
    while True:
        container.motor.check_step()
        await async_sleep(0)

async def main():
    await gather(
        create_task(handle_http_requests()),
        #create_task(led_blicks()),
        create_task(send_http_logs()),
        create_task(screen_task()),
        create_task(motors_task()),
    )

run(main())