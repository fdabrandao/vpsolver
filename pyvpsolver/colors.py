"""
Finding N Distinct RGB Colors
Based on code from StackOverflow: http://stackoverflow.com/a/2142206
"""
import math

def rgbcode(t):
    r, g, b = t
    r = int(r*255)
    g = int(g*255)
    b = int(b*255)        
    return '#%0.2x%0.2x%0.2x' % (r, g, b)

def rgbcolor(h, f, v, p):
    """Convert a color specified by h-value and f-value to an RGB
    three-tuple."""
    # q = 1 - f
    # t = f
    if h == 0:
        return v, f, p
    elif h == 1:
        return 1 - f, v, p
    elif h == 2:
        return p, v, f
    elif h == 3:
        return p, 1 - f, v
    elif h == 4:
        return f, p, v
    elif h == 5:
        return v, p, 1 - f  

def uniquecolors(n, v=0.5, p=0.0):
    """Compute a list of distinct colors, ecah of which is
    represented as an RGB three-tuple"""
    hues = (360.0 / n * i for i in range(n))
    hs = (math.floor(hue / 60) % 6 for hue in hues)
    fs = (hue / 60 - math.floor(hue / 60) for hue in hues)
    return [rgbcode(rgbcolor(h, f, v, p)) for h, f in zip(hs, fs)]

