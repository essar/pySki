"""
  Module that provides common classes and utility functions for SkiData application.
"""
from datetime import datetime


class Track:
    """
    Class that encapsulates data representing a single track or connected set of points.
    """
    def __init__(self, track_id, track_group, track_zdt):
        self.track_id = track_id
        self.track_group = track_group
        self.track_zdt = track_zdt


    def __str__(self):
        return '[{:s}] group={:s} zdt={:s}'.format(self.track_id, self.track_group, self.track_zdt)



class LinkedPoint:
    """
    """
    def __init__(self, point, next_point=None):
        self.point = point
        if next_point == None or type(next_point) == LinkedPoint:
            self.next_point = next_point
        else:
            # Wrap the point as a LinkedPoint
            self.next_point = LinkedPoint(next_point)


    def to_list(self):
        output = []
        p = self
        while p != None:
            output.append(p.point)
            p = p.next_point

        return output


    def __str__(self):
        return  '[{0:010d}]'.format(self.point.ts) if self.next_point == None or self.next_point.point == None else '[{0:010d} => {1:010d}]'.format(self.point.ts, self.next_point.point.ts)



class BasicGPSPoint:
    """
    Class that encapsulates the basic data points collected from the GPS device.
    """
    def __init__(self, ts=0, lat=0.0, lon=0.0, alt=0, spd=0.0):
        self.ts = ts
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.spd = spd


    def vals(self):
        """Get point data as a dict"""
        return { 'ts': self.ts, 'lat': self.lat, 'lon': self.lon, 'alt': self.alt, 'spd': self.spd }

    def __repr__(self):
        return {
            'ts' : '{:010}'.format(self.ts)
        }

    def __str__(self):
        return 'ts={:010d}, lat={:.6f}, lon={:.6f}, a={:04d}, s={:06.2f}'.format(self.ts, self.lat, self.lon, self.alt, self.spd)



class EnrichedPoint(BasicGPSPoint):

    def __init__(self, ts=0, lat=0.0, lon=0.0, alt=0, spd=0.0, x=0, y=0):
        super().__init__(ts, lat, lon, alt, spd)
        self.x = x
        self.y = y
        self.dst = 0.0
        self.hdg = 0.0
        self.alt_d = 0
        self.spd_d = 0.0
        self.hdg_d = 0.0


    def __repr__(self):
        #return super().__repr__().extend(
        return {
                'x'     : '{:08d}'.format(self.x),
                'y'     : '{:08d}'.format(self.y),
                'dst'   : '{:.2f}'.format(self.dst),
                'hdg'   : '{:05.1f}'.format(self.hdg),
                'alt_d' : '{:+04d}'.format(self.alt_d),
                'spd_d' : '{:+06.2f}'.format(self.spd_d),
                'hdg_d' : '{:+06.1f}'.format(self.hdg_d)
            }
        #)


    def __str__(self):
        return '{:s}, x={:08d}, y={:08d}, d={:.2f}, h={:05.1f}, alt_d={:+04d}, spd_d={:+06.2f}, hdg_d={:+06.1f}'.format(super().__str__(), self.x, self.y, self.dst, self.hdg, self.alt_d, self.spd_d, self.hdg_d)


def basic_to_enriched_point(basic_point):
    return EnrichedPoint(**basic_point.vals())
