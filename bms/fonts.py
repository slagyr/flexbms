from bms.util import load_binary

_font5x7 = None
_font6x8 = None
_font8x8 = None

def clear():
    global _font5x7
    _font5x7 = None
    global _font6x8
    _font6x8 = None
    global _font8x8
    _font8x8 = None

def font5x7():
    global _font5x7
    if not _font5x7:
        _font5x7 = load_binary("font5x7")
    return _font5x7

def font6x8():
    global _font6x8
    if not _font6x8:
        _font6x8 = load_binary("font6x8")
    return _font6x8

def font8x8():
    global _font8x8
    if not _font8x8:
        _font8x8 = load_binary("font8x8")
    return _font8x8

