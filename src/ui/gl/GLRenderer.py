'''
Created on 19 Nov 2012

@author: sroberts
'''

b_inverted = False

def relPos(minV, maxV, value):
    value = min(maxV, max(minV, value))
    return float(value - minV) / float(maxV - minV)

def getColourValue(minV, maxV, value):
    ''' Returns a colour 3-tuple for a value within the given range. '''
    return getColourValuef(relPos(minV, maxV, value))
    
def getColourValuef(value):
    ''' Returns a colour 3-tuple for a float between 0 and 1. '''
    
    # Bind the value within the range 0-1.
    value = min(1.0, max(0.0, value))
    
    if value <= (1.0/6.0):
        # 0,0,0-255,0,0
        r = relPos(0.0, (1.0/6.0), value)
        g = 0.0
        b = 0.0
    if value > (1.0/6.0) and value <= (2.0/6.0):
        # 255,0,0-255,255,0
        r = 1.0
        g = relPos((1.0/6.0), (2.0/6.0), value)
        b = 0.0
    if value > (2.0/6.0) and value <= (3.0/6.0):
        # 255,255,0-0,255,0
        r = 1.0 - relPos((2.0/6.0), (3.0/6.0), value)
        g = 1.0
        b = 0.0
    if value > (3.0/6.0) and value <= (4.0/6.0):
        # 0,255,0-0,255,255
        r = 0.0
        g = 1.0
        b = relPos((3.0/6.0), (4.0/6.0), value)
    if value > (4.0/6.0) and value <= (5.0/6.0):
        # 0,255,255-0,0,255
        r = 0.0
        g = 1.0 - relPos((4.0/6.0), (5.0/6.0), value)
        b = 1.0
    if value > (5.0/6.0):
        # 0,0,255-255,255,255
        r = relPos((5.0/6.0), 1.0, value)
        g = relPos((5.0/6.0), 1.0, value)
        b = 1.0
    
    # Dark (black) to light (white)
    if b_inverted:
        return (1.0 - r, 1.0 - g, 1.0 - b)
    else:
        return (r, g, b)
    
