'''
Interpolates between missing points in a data list

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
@version: 1.0 (30 Nov 2012)
'''

import logging as log
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
    
    dp = DatumPoint(ts, ((la, lo), (x, y), a, s))
    log.debug('[Interpolator] New point: {0}  ({1} : {2})', dp, p1, p2)
    
    return dp


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
    lastNode = None
    for i in arr:
        newNode = LinkedObj(i, lastNode)
        lastNode = newNode
        
    return lastNode

 
def interpolate_list(lData, deltaF, interF):
    return interpolate_linked_list(build_linked_list(lData), deltaF, interF)   

        
def interpolate_linked_list(firstNode, deltaF, interF):
    global count_added, count_removed, counter
    
    # Initialise with first node
    thisNode = firstNode
    while thisNode != None and thisNode.nxt != None:
        nextNode = thisNode.nxt
        # Calculate distance between points
        delta = deltaF(thisNode.obj, nextNode.obj)
        log.debug('[Interpolator] Node {0}: delta {1}', counter, delta)
        
        if delta < 0:
            # Negative delta
            log.warn('[Interpolator] Negative time delta ({0}) at node {1}', delta, counter)
        if delta == 0:
            # Duplicate point, remove
            thisNode.nxt = nextNode.nxt
            log.info('[Interpolator] Removed node at {0}', counter)
            # Increment counter
            count_removed += 1
            counter -+ 1
        while delta > 1:
            # Interpolate a new point mediating this node and next node
            newNode = LinkedObj(interF(thisNode.obj, nextNode.obj))
            # Set new node's next to next node
            newNode.nxt = nextNode
            # Set this node's next to new node
            thisNode.nxt = newNode
            log.info('[Interpolator] Created node at {0}', counter)
            
            # Recalculate delta
            delta = deltaF(thisNode.obj, nextNode.obj)
            log.debug('[Interpolator] Node {0}: delta {1}', counter, delta)
            # Increment counters
            count_added += 1
            counter += 1
        
        # Move to next node    
        thisNode = nextNode
        # Increment counter
        counter += 1
        
        log.debug('[Interpolator] Counter={0}; added={1}, removed={2}', counter, count_added, count_removed)
    