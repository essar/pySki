'''
Created on 16 Nov 2012

@author: sroberts
'''

from math import sqrt
import data

def calc_dalt((d, a1), a2):
    da = a1 - a2
    return ((d + da, a2))

def calc_distance((d, (x1, y1)), (x2, y2)):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)  
    d1 = sqrt(dx^2 + dy^2)
    return ((d + d1), (x2, y2))


class SkiTrackHeader:
    avSpeed = 0.0
    name = ''
    
    def __init__(self, tData):
        # First & last
        self.first = tData[0]
        self.last = tData[-1]
        
        # Area, width & height
        xsD = data.ps_Xs(tData)
        ysD = data.ps_Ys(tData)
        self.area = ((min(xsD), min(ysD)), (max(xsD), max(ysD)))
        self.width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*self.area)
        self.height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*self.area)
        
        # Altitude
        asD = data.ps_As(tData)
        self.loAlt = min(asD)
        self.hiAlt = max(asD)
        #self.dAlt = sum(asD)
        p0 = (0, data.p_A(self.first))
        (self.dAlt, __pa) = reduce(calc_dalt, data.ps_As(tData), p0)
        
        # Speed
        ssD = data.ps_Ss(tData)
        #self.avSpeed = avg(ssD)
        self.hiSpeed = max(ssD)
        
        # Distance & duration
        p0 = (0, data.p_Cart(self.first))
        (self.distance, __px) = reduce(calc_distance, data.ps_Carts(tData), p0)
        self.duration = len(tData)
    
    
    def print_track_header(self):
        print '================'
        print ' TRACK HEADER'
        print '================'
        print 'Count/duration: {0:d}'.format(self.duration)
        print 'Distance: {0:.2f}m'.format(self.distance)
        print 'Altitude: {0:4,d}m-{1:4,d}m ({2:+,d}m)'.format(self.loAlt, self.hiAlt, self.dAlt)
        print 'High speed: {0:2.0f}km/h'.format(self.hiSpeed)
        print 'Average speed: {0:2.1f}km/h'.format(self.avSpeed)
        print 'Area: {0}'.format(self.area)
        








def dist_between(p1, p2):
    pt1 = Point(p1)
    pt2 = Point(p2)
    dx = abs(pt1.x - pt2.x)
    dy = abs(pt1.y - pt2.y)    
    return sqrt(dx^2 + dy^2)


class Point:
    ''' A class that represents a GPS data point.
        A GPS point has the following properties:
         * Timestamp (in seconds)
         *   Latitude & Longtiude
         *   Cartesian X & Y
         *   Altitude
         *   Speed
    '''
    p0 = (0, ((0.0, 0.0), (0, 0), 0, 0))
    
    timestamp = 0
    latitude = longitude = 0.0
    x = y = 0
    altitude = speed = 0
    
    def __init__(self, p):
        (self.timestamp, ((self.latitude, self.longitude), (self.x, self.y), self.altitude, self.speed)) = p



        