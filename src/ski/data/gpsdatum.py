'''
Created on 11 Dec 2012

@author: sroberts
'''

class GPSDatum:
    '''
      Class representing a single entry of GPS data, as read from a GPS device
      or data file.
    '''
    def __init__(self, (ts, (la, lo), (x, y), a, s)):
        self.gps_ts = ts
        self.gps_la = la
        self.gps_lo = lo
        self.gps_x = x
        self.gps_y = y
        self.gps_a = a
        self.gps_s = s

    def __str__(self):
        return 'ts={0}, location=({1:.4f},{2:.4f}), alt={3:d}, spd={4:.1f}'.format(self.gps_ts, self.gps_la, self.gps_lo, self.gps_a, self.gps_s)

    def as_tuple(self):
        return (self.gps_ts, (self.gps_la, self.gps_lo), (self.gps_x, self.gps_y), self.gps_a, self.gps_s)