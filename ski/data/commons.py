"""
  Module that provides common classes and utility functions for SkiData application.
"""


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
        self.alt = alt
        self.spd = spd

    def values(self):
        v = {
            'ts': self.ts,
            'lat': self.lat,
            'lon': self.lon,
            'alt': self.alt,
            'spd': self.spd
        }
        return v

    def __repr__(self):
        return str(self.values())

    def __str__(self):
        return 'ts={ts:010d}, lat={lat:.6f}, lon={lon:.6f}, a={alt:04d}m, s={spd:06.2f}kph'.format(**self.values())


class ExtendedGPSPoint(BasicGPSPoint):
    def __init__(self, track_id=None, ts=0, lat=0.0, lon=0.0, alt=0, spd=0.0, x=0, y=0, dst=0.0, hdg=0.0,
                 alt_d=0, spd_d=0.0, hdg_d=0.0):
        super().__init__(ts, lat, lon, alt, spd)
        self.track_id = track_id
        self.x = x
        self.y = y
        self.dst = dst
        self.hdg = hdg
        self.alt_d = alt_d
        self.spd_d = spd_d
        self.hdg_d = hdg_d

        # Windows
        self.windows = {}

    def values(self):
        v = super().values()
        v.update({
            'x': self.x,
            'y': self.y,
            'dst': self.dst,
            'hdg': self.hdg,
            'alt_d': self.alt_d,
            'spd_d': self.spd_d,
            'hdg_d': self.hdg_d,
        })
        v.update(self.windows)
        return v

    def __str__(self):
        return '{:s}, x={x:08d}, y={y:08d}, d={dst:.2f}m, h={hdg:05.1f}, alt_d={alt_d:+04d}m, ' \
               'spd_d={spd_d:+06.2f}kph, hdg_d={hdg_d:+06.1f}'.format(super().__str__(), **self.values())


class EnrichedWindow:

    def __init__(self, period=0, distance=0.0, alt_min=0, alt_max=0, alt_delta=0, alt_gain=0, alt_loss=0,
                 speed_min=0.0, speed_max=0.0, speed_ave=0.0, speed_delta=0.0):
        self.period = period
        self.distance = distance
        self.alt_delta = alt_delta
        self.alt_gain = alt_gain
        self.alt_loss = alt_loss
        self.alt_max = alt_max
        self.alt_min = alt_min
        self.speed_ave = speed_ave
        self.speed_delta = speed_delta
        self.speed_max = speed_max
        self.speed_min = speed_min

    def values(self):
        v = {
            'period': self.period,
            'distance': self.distance,
            'alt_delta': self.alt_delta,
            'alt_gain': self.alt_gain,
            'alt_loss': self.alt_loss,
            'alt_max': self.alt_max,
            'alt_min': self.alt_min,
            'speed_ave': self.speed_ave,
            'speed_delta': self.speed_delta,
            'speed_max': self.speed_max,
            'speed_min': self.speed_min
        }
        return v

    def __repr__(self):
        return str(self.values())

    def __str__(self):
        return 'period={period:d}s, dist: {distance:.2f}m, ' \
               'alt: {alt_min:04d}m-{alt_max:04d}m ({alt_delta:+04d}m; +{alt_gain:04d}, -{alt_loss:04d}), ' \
               'spd: {speed_min:05.2f}-{speed_max:05.2f} ({speed_delta:+06.2f}; {speed_ave:05.2f})'\
            .format(**self.values())


def basic_to_extended_point(basic_point):
    # Don't attempt to convert if is already an extended point
    if type(basic_point) == ExtendedGPSPoint:
        return basic_point
    if type(basic_point) == BasicGPSPoint:
        return ExtendedGPSPoint(**basic_point.values())
    raise TypeError('Expected BasicGPSPoint')


def debug_point_event(logger, point, message, *args):
    log_msg = '[%010d] ' + message
    logger.debug(log_msg, point.ts, *args)
