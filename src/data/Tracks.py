'''
Created on 16 Nov 2012

@author: sroberts
'''

from math import sqrt
import Utils

def calc_distance((d, (x1, y1)), (x2, y2)):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)  
    d1 = sqrt(dx^2 + dy^2)
    return ((d + d1), (x2, y2))

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


class TrackSummary:

    altDelta = 0    
    distance = 0.0
    hiAlt = loAlt = hiSpeed = 0
    length = 0
    maxX = minX = sizeX = 0
    maxY = minY = sizeY = 0
    
    ''' Constructor '''
    def __init__(self, data):
        (self.loAlt, self.hiAlt) = Utils.min_max_alts(data)
        self.altDelta = abs(self.hiAlt - self.loAlt)
        
        self.hiSpeed = max(Utils.speeds(data))
        
        (self.minX, self.maxX) = Utils.min_max_x(data)
        self.sizeX = abs(self.maxX - self.minX)
        
        (self.minY, self.maxY) = Utils.min_max_y(data)
        self.sizeY = abs(self.maxY - self.minY)
        
        p0 = (0, Utils.carts([data[0]])[0])
        (self.distance, __px) = reduce(calc_distance, Utils.carts(data), p0)
        self.length = len(data)
        
    def print_summary(self):
        print '(X,Y):    ({0},{2})-({1},{3})'.format(self.minX, self.maxX, self.minY, self.maxY)
        print 'Size:     {0}x{1}'.format(self.sizeX, self.sizeY)
        print 'Altitude: low={0}, high={1}'.format(self.loAlt, self.hiAlt)
        print 'Speed:    high={0}'.format(self.hiSpeed)
        print 'Distance: {0}'.format(self.distance)
        