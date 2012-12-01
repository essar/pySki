'''
  Module providing functions that interpolate between missing points in a data
  list.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (30 Nov 2012)
'''

import logging as log
from data import GPSDatum

count_added = 0
count_removed = 0
counter = 0

def delta_i(i1, i2): return i2 - i1
def delta_f(f1, f2): return f2 - f1
def delta_pt(pt1, pt2): return pt2.ts - pt1.ts

def linear_interpolate_f(f1, f2): return f1 + ((f2 - f1) / 2.0)
def linear_interpolate_i(i1, i2): return i1 + ((i2 - i1) / 2)
def linear_interpolate_pt(p1, p2):
    '''
      Linearly interpolate the x, y, latitude, longitude, altitude, speed and time of two GPSDatum points.
      If the x, y and altitude change between the two points is unchanged, speed is forced to 0.
    '''
    ts = linear_interpolate_i(p1.gps_ts, p2.gps_ts)
    la = linear_interpolate_f(p1.gps_la, p2.gps_la)
    lo = linear_interpolate_f(p1.gps_lo, p2.gps_lo)
    x = linear_interpolate_i(p1.gps_x, p2.gps_x)
    y = linear_interpolate_i(p1.gps_y, p2.gps_y)
    a = linear_interpolate_i(p1.gps_a, p2.gps_a)
    s = linear_interpolate_i(p1.gps_s, p2.gps_s)
    
    dp = GPSDatum(ts, (la, lo), (x, y), a, s)
    log.debug('[Interpolator] New point: {0}  ({1} : {2})', dp, p1, p2)
    
    return dp


class LinkedNode:
    '''
      Object that forms a linked list node.  Each node in a linked list
      contains a payload and reference to the next item in the list.
      @param obj: the payload of this node.
      @param nxt: the next item in the linked list.
    '''
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
    '''
      Builds a linked list from a flat array of objects.
      @param array: the array to store in the payloads of the linked list
      @return: the first LinkedObj node in the linked list
    '''
    # Smarter way to do this?
    arr = array[:]
    arr.reverse()
    lastNode = None
    for i in arr:
        newNode = LinkedNode(i, lastNode)
        lastNode = newNode
        
    return lastNode

 
def interpolate_list(lData, deltaF, interF):
    '''
      Interpolate over an array of data.
      @param lData: an array of data to interpolate.
      @param deltaF: a function used to calculate the delta between two nodes.
      @param interF: a function used to interpolate between two nodes.
      @return: an array of the interpolated nodes.
    '''
    ll = build_linked_list(lData)
    interpolate_linked_list(ll, deltaF, interF)
    return ll.to_array()

        
def interpolate_linked_list(firstNode, deltaF, interF):
    '''
      Interpolate over a linked list. Interpolation happens 'in-place', no
      object is returned.
      @param firstNode: the first node of the list.
      @param deltaF: a function used to calculate the delta between two nodes.
      @param interF: a function used to interpolate between two nodes.
      
    '''
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
            newNode = LinkedNode(interF(thisNode.obj, nextNode.obj))
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
    