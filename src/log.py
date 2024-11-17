from collections import deque
import time
import gc
from tools import format_datetime

class LogItem:
    def __init__(self, log_number, log_time, level, message):
        self.log_number = log_number
        self.log_time = format_datetime(log_time)
        self.level = level
        self.message = message

    def to_string(self):
        return f"{self.log_time}: {self.level} {self.message}"

log_items = deque([], 100)
log_counter = 0

def add_raw_log(log_time, level, message):
    global log_items, log_counter
    log_items.append(LogItem(log_counter, log_time, level, message))
    log_counter += 1

def debug(message):
    add_raw_log(time.localtime(), "DEBUG", message)

# print and debug
def pdebug(*args):
    print(*args)
    debug(" ".join(map(str, args)))

# print and error
def perror(*args):
    print(*args)
    add_raw_log(time.localtime(), "ERROR", " ".join(map(str, args)))

def log_memory():
    gc.collect()
    pdebug("Free mem:", gc.mem_free())

def get_last_log():
    return log_counter