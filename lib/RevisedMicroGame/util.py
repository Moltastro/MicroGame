def rgb(r, g, b, swap_bytes=True):
    """Returnerar färg med rött, grönt, blått 0-255"""
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F

    value = (r5 << 11) | (g6 << 5) | b5
    if swap_bytes:
        value = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)
    return value