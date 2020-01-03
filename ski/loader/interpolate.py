"""
"""
import logging

from math import floor
from ski.data.commons import ExtendedGPSPoint, debug_point_event

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def __linear_interpolate_f(f1, f2, delta):
    """ Perform linear interpolation between two floating point values. """
    return f1 + ((f2 - f1) / delta)


def __linear_interpolate_i(i1, i2, delta):
    """ Perform linear interpolation between two integer values. """
    return floor(i1 + ((i2 - i1) / delta))


def linear_interpolate(p1, p2, delta):
    """
    Perform a linear interpolation between two points.
    """
    # Create a new point
    p = ExtendedGPSPoint()
    # Interpolate timestamp
    p.ts = __linear_interpolate_i(p1.ts, p2.ts, delta)
    # Interpolate latitude & longitude
    p.lat = __linear_interpolate_f(p1.lat, p2.lat, delta)
    p.lon = __linear_interpolate_f(p1.lon, p2.lon, delta)
    # Interpolate X & Y
    p.x = __linear_interpolate_i(p1.x, p2.x, delta)
    p.y = __linear_interpolate_i(p1.y, p2.y, delta)
    # Interpolate altitude
    p.alt = __linear_interpolate_i(p1.alt, p2.alt, delta)
    # Interpolate speed
    p.spd = __linear_interpolate_f(p1.spd, p2.spd, delta)

    debug_point_event(log, p2, 'linear_interpolate (delta=%d): {%s} {%s}: {%s}', delta, p1, p2, p)

    return p
