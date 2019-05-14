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


class BasicGPSPoint:
    """
    Class that encapsulates the basic data points collected from the GPS device.
    """
    def __init__(self, ts=0, lat=0.0, lon=0.0, alt=0, spd=0.0):
        self.ts = ts
        self.lat = lat
        self.lon = lon
        self.spd = spd
        self.alt = alt


    def vals(self):
        """Get point data as a dict"""
        return { 'ts': self.ts, 'lat': self.lat, 'lon': self.lon, 'alt': self.alt, 'spd': self.spd }


    def __str__(self):
        return 'ts={:010d}, lat={:.4f}, lon={:.4f}, a={:04d}, s={:06.2f}'.format(self.ts, self.lat, self.lon, self.alt, self.spd)

