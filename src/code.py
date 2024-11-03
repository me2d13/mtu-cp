import board
import digitalio
import time
import os
import ipaddress
import wifi
import socketpool
import web
from log import pdebug, log_memory
from mtu_time import set_time_from_ntp
from asyncio import create_task, gather, run, sleep as async_sleep

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


log_memory()
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

pdebug("Connected to WiFi" )
log_memory()

pool = socketpool.SocketPool(wifi.radio)

set_time_from_ntp(pool)

log_memory()
pdebug("Starting web server...")
server = web.WebServer(pool)
server.start()

#  prints MAC address to REPL
pdebug("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
pdebug("My IP address is", wifi.radio.ipv4_address)
log_memory()

async def handle_http_requests():
    while True:
        server.poll()
        await async_sleep(0)

async def send_http_logs():
    while True:
        #log_memory()
        server.send_logs_if_needed()
        await async_sleep(1)

async def led_blicks():
    while True:
        led.value = True
        await async_sleep(0.2)
        led.value = False
        await async_sleep(1)

async def main():
    await gather(
        create_task(handle_http_requests()),
        create_task(led_blicks()),
        create_task(send_http_logs()),
    )

run(main())