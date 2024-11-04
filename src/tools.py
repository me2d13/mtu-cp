
def format_datetime(datetime):
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        datetime.tm_year,
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

