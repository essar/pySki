'''
  Module providing functions that interpolate between missing points in a data
  list.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (30 Nov 2012)
'''

import logging as log

from gpsdatum import GPSDatum
from linkednode import LinkedNode

count_added = 0
count_removed = 0
counter = 0

def delta_i(i1, i2): return i2 - i1
def delta_f(f1, f2): return f2 - f1
def delta_pt(pt1, pt2): return pt2.gps_ts - pt1.gps_ts

def linear_interpolate_f(f1, f2): return f1 + ((f2 - f1) / 2.0)
def linear_interpolate_i(i1, i2): return i1 + ((i2 - i1) / 2)
def linear_interpolate_pt(p1, p2):
    '''
      Linearly interpolate the x, y, latitude, longitude, altitude, speed and time of two GPSDatum points.
      If the x, y and altitude change between the two points is unchanged, speed is forced to 0.
    '''
    
    log.debug('[Interpolator] p1: %s', p1)
    log.debug('[Interpolator] p2: %s', p2)
    
    ts = linear_interpolate_i(p1.gps_ts, p2.gps_ts)
    la = linear_interpolate_f(p1.gps_la, p2.gps_la)
    lo = linear_interpolate_f(p1.gps_lo, p2.gps_lo)
    x = linear_interpolate_i(p1.gps_x, p2.gps_x)
    y = linear_interpolate_i(p1.gps_y, p2.gps_y)
    a = linear_interpolate_i(p1.gps_a, p2.gps_a)
    s = linear_interpolate_i(p1.gps_s, p2.gps_s)
    
    dp = GPSDatum((ts, (la, lo), (x, y), a, s))
    log.debug('[Interpolator] New point: %s', dp)
    
    return dp


def interpolate_list(firstNode, deltaF, interF, deDup=True):
    '''
      Interpolate over a linked list. Interpolation happens 'in-place', no
      object is returned.
      @param firstNode: the first node of the list.
      @param deltaF: a function used to calculate the delta between two nodes.
      @param interF: a function used to interpolate between two nodes.
      
    '''
    global count_added, count_removed, counter
    
    # Reset counters
    count_added = count_removed = counter = 0
    
    # Initialise with first node
    thisNode = firstNode
    while thisNode != None and thisNode.nxt != None:
        nextNode = thisNode.nxt
        # Calculate distance between points
        delta = deltaF(thisNode.obj, nextNode.obj)
        log.debug('[Interpolator] Node %d: delta %d', counter, delta)
        
        if delta < 0:
            # Negative delta
            log.warn('[Interpolator] Negative time delta (%d) at node %d', delta, counter)
        if delta == 0 and deDup:
            # Duplicate point, remove
            thisNode.nxt = nextNode.nxt
            log.info('[Interpolator] Removed node at %d', counter)
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
            log.info('[Interpolator] Created node at %d', counter)
            
            # Recalculate delta
            nextNode = thisNode.nxt
            delta = deltaF(thisNode.obj, nextNode.obj)
            log.debug('[Interpolator] Node %d: delta %d', counter, delta)
            # Increment counters
            count_added += 1
            counter += 1
        
        # Move to next node    
        thisNode = nextNode
        # Increment counter
        counter += 1
        
        log.debug('[Interpolator] Counter=%d; added=%d, removed=%d', counter, count_added, count_removed)
    