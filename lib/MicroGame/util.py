from time import ticks_diff,ticks_ms
def rgb(r, g, b, swap_bytes=True):
    """Returnerar färg med rött, grönt, blått 0-255"""
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F

    value = (r5 << 11) | (g6 << 5) | b5
    if swap_bytes:
        value = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)
    return value
DEBUG=False
def debug(*var):
    if DEBUG:
        print(*var)
def log_time():
    def log_time_decorator(func):
        def wrapper(*args, **kwargs):
            start = ticks_ms()
            result = func(*args, **kwargs)
            end = ticks_ms()
            elapsed = ticks_diff(end, start)
            print(f'Function {func} took {elapsed}')
        return wrapper
    return log_time_decorator

def log_time_repeat(list,times):
    def log_time_decorator(func):
        def wrapper(*args, **kwargs):
            start = ticks_ms()
            result = func(*args, **kwargs)
            end = ticks_ms()
            elapsed = ticks_diff(end, start)
            list.append(elapsed)
            return result
        return wrapper
    return log_time_decorator