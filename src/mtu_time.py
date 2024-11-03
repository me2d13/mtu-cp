import adafruit_ntp
import rtc
from log import pdebug

my_tz_offset = +1  # CET

def set_time_from_ntp(pool):
    pdebug("Trying to set time from NTP with offset", my_tz_offset)
    try:
        ntp = adafruit_ntp.NTP(pool, tz_offset=my_tz_offset)
        rtc.RTC().datetime = ntp.datetime
        pdebug("Time set")
    except:
        pdebug("Exception during contacting NTP server")