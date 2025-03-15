class TimeUnits:
    second: float = 1.0
    minute: float = 60 * second
    hour: float = 60 * minute
    day: float = 24 * hour
    week: float = 7 * day
    month: float = 30 * day
    year: float = 365 * day

    millisecond: float = second / 1e3
    microsecond: float = millisecond / 1e3
    nanosecond: float = microsecond / 1e3
    picosecond: float = nanosecond / 1e3
    femtosecond: float = picosecond / 1e3

