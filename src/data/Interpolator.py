'''
Interpolates between missing points in a data list

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
@version: 1.0 (30 Nov 2012)
'''

from data import DatumPoint

count_added = 0
count_removed = 0
counter = 0

def __delta_i(i1, i2): return i2 - i1
def __delta_pt(pt1, pt2): return pt2.ts - pt1.ts

def __linear_interpolate_f(f1, f2): return f1 + ((f2 - f1) / 2.0)
def __linear_interpolate_i(i1, i2): return i1 + ((i2 - i1) / 2)

def __linear_interpolate(p1, p2):
    '''
      Linearly interpolate the x, y, latitude, longitude, altitude, speed and time of two Datum points.
      If the x, y and altitude change between the two points is unchanged, speed is forced to 0.
    '''
    
    ts = __linear_interpolate_i(p1.ts, p2.ts)
    la = __linear_interpolate_f(p1.la, p2.la)
    lo = __linear_interpolate_f(p1.lo, p2.lo)
    x = __linear_interpolate_i(p1.x, p2.x)
    y = __linear_interpolate_i(p1.y, p2.y)
    a = __linear_interpolate_i(p1.a, p2.a)
    s = __linear_interpolate_i(p1.s, p2.s)
    
    return DatumPoint(ts, ((la, lo), (x, y), a, s))


class LinkedObj:
    def __init__(self, obj=None, nxt=None):
        self.obj = obj
        self.nxt = nxt
    
    def __str__(self):
        str(self.obj)

    def to_array(self):
        # See if this can be done with list comprehension?
        out = [self.obj]
        o = self.nxt
        while o != None:
            out.append(o.obj)
            o = o.nxt
        return out


def build_linked_list(array):
    # Smarter way to do this?
    arr = array[:]
    arr.reverse()
    lastPoint = None
    for i in arr:
        newPoint = LinkedObj(i, lastPoint)
        lastPoint = newPoint
        
    return lastPoint
    
        
def interpolate_linked_list(firstPoint, deltaF, interF):
    global count_added, count_removed, counter
    
    thisPoint = firstPoint
    while thisPoint != None and thisPoint.nxt != None:
        delta = deltaF(thisPoint.obj, thisPoint.nxt.obj)
        
        if delta < 0:
            print ' ** WARN! Negative time delta ({0})'.format(delta)
        if delta == 0:
            thisPoint.nxt = thisPoint.nxt.nxt
            count_removed += 1
        while delta > 1:
            newPoint = LinkedObj(interF(thisPoint.obj, thisPoint.nxt.obj))
            newPoint.nxt = thisPoint.nxt
            thisPoint.nxt = newPoint
            
            delta = deltaF(thisPoint.obj, thisPoint.nxt.obj)
            count_added += 1
            counter += 1
            
        thisPoint = thisPoint.nxt
        counter += 1
    