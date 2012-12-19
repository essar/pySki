'''
Created on 11 Dec 2012

@author: sroberts
'''

MODE_LIFT = 'LIFT'
MODE_SKI = 'SKI'
MODE_STOP = 'STOP'

class SkiTrackHeader:
    first = last = None
    mode = None
    
    area = (0, 0)
    height = width = 0
    
    hiAlt = loAlt = 0
    avSpeed = hiSpeed = 0.0
    hiAngle = loAngle = 0.0
    distance = net_distance = 0
    duration = 0
    name = ''
    
    def print_track_header(self):
        print '================'
        print ' TRACK HEADER'
        print '================'
        print 'Count/duration: {0:d}'.format(self.duration)
        print 'Distance: {0:.2f}m'.format(self.distance)
        print 'Altitude: {0:4,d}m-{1:4,d}m ({2:+,d}m)'.format(self.loAlt, self.hiAlt, self.dAlt)
        print 'Angle: {0:2.1f}, {1:2.1f}'.format(self.loAngle, self.hiAngle)
        print 'High speed: {0:2.0f}km/h'.format(self.hiSpeed)
        print 'Average speed: {0:2.1f}km/h'.format(self.avSpeed)
        print 'Area: {0}'.format(self.area)


class SkiTrack:

    def __init__(self, tData):
        # Validate arguments
        self.data = tData
        
        self.hdr = SkiTrackHeader()
        
        # First & last
        self.hdr.first = tData[0]
        self.hdr.last = tData[-1]
        self.hdr.mode = tData[0].mode
        
        # Property arrays
        self.xs = [p.x for p in tData]
        self.ys = [p.y for p in tData]
        self.alts = [p.alt for p in tData]
        self.spds = [p.spd for p in tData]
        
        # Area, width & height
        self.hdr.area = ((min(self.xs), min(self.ys)), (max(self.xs), max(self.ys)))
        self.hdr.width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*self.hdr.area)
        self.hdr.height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*self.hdr.area)
        
        # Altitude
        self.hdr.loAlt = min(self.alts)
        self.hdr.hiAlt = max(self.alts)
        self.hdr.dAlt = sum([p.delta_a for p in tData])
        
        # Angle
        anglesD = [p.angle for p in tData]
        self.hdr.loAngle = min(anglesD)
        self.hdr.hiAngle = max(anglesD)
        
        # Distance & duration
        distsD = [p.xy_distance for p in tData]
        self.hdr.distance = sum(distsD)
        self.hdr.duration = len(tData)
        
        # Speed
        self.hdr.hiSpeed = max(self.spds)
        self.hdr.avSpeed = sum(self.spds) / len(tData)
        
        
class SkiTrackPoint:
    
    mode = None
    
    # Static values
    x = y = alt = 0
    spd = 0.0
    ts = 0
    
    # Calculated values
    angle = 0.0
    delta_x = delta_y = delta_a = 0
    distance = xy_distance = 0.0
    calc_speed = 0.0
    tz_time = None

    def __init__(self, d):
        self.ts = d.gps_ts
        self.x = d.gps_x
        self.y = d.gps_y
        self.alt = d.gps_a
        self.spd = d.gps_s
        
    def __str__(self):
        return '{:s} ({:.2f}m, {:+.1f}m)'.format(self.as_tuple(), self.distance, self.delta_a)
    
    def as_tuple(self):
        return (self.mode, (self.ts, (self.x, self.y), self.alt, self.spd))
