"""
"""
import logging

from math import floor
from ski.config import config
from ski.data.commons import ExtendedGPSPoint
from ski.data.pointutils import get_ts_delta

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def __add_point(point, output):
    if type(point) != ExtendedGPSPoint:
        log.warning('Interpolator attempting to add %s object to output; expected ExtendedGPSPoint', type(point))
        return
    if point is not None:
        output.append(point)


def __linear_interpolate_f(f1, f2, delta):
    """"""
    return f1 + ((f2 - f1) / delta)


def __linear_interpolate_i(i1, i2, delta):
    """"""
    return floor(i1 + ((i2 - i1) / delta))


def linear_interpolate(p1, p2, delta):
    """
    Perform a linear interpolation between two points.
    """
    p = ExtendedGPSPoint()
    log.debug('linear_interpolate: interpolating data; delta=%d', delta)
    p.ts  = __linear_interpolate_i(p1.ts, p2.ts, delta)
    log.debug('linear_interpolate:   ts  = %10d << %10d >> %10d', p1.ts, p.ts, p2.ts)
    p.lat = __linear_interpolate_f(p1.lat, p2.lat, delta)
    log.debug('linear_interpolate:   lat = %10f << %10f >> %10f', p1.lat, p.lat, p2.lat)
    p.lon = __linear_interpolate_f(p1.lon, p2.lon, delta)
    log.debug('linear_interpolate:   lon = %10f << %10f >> %10f', p1.lon, p.lon, p2.lon)
    p.x   = __linear_interpolate_i(p1.x, p2.x, delta)
    log.debug('linear_interpolate:   x   = %10d << %10d >> %10d', p1.x, p.x, p2.x)
    p.y   = __linear_interpolate_i(p1.y, p2.y, delta)
    log.debug('linear_interpolate:   y   = %10d << %10d >> %10d', p1.y, p.y, p2.y)
    p.alt = __linear_interpolate_i(p1.alt, p2.alt, delta)
    log.debug('linear_interpolate:   alt = %10d << %10d >> %10d', p1.alt, p.alt, p2.alt)
    p.spd = __linear_interpolate_f(p1.spd, p2.spd, delta)
    log.debug('linear_interpolate:   spd = %10f << %10f >> %10f', p1.spd, p.spd, p2.spd)

    return p


def interpolate_point(inter_f, point, previous_point=None):
    """
    Evaluates the delta between two points and returns an array of points between the two.
    prev_point is *not* returned as part of the array.
    """
    output = []
    insert_count = 0
    delete_count = 0

    # Calculate time delta
    ts_delta = get_ts_delta(previous_point, point)
    log.debug('interpolate_point: ts_delta=%d; ts=[%d >> %d]', ts_delta, previous_point.ts if previous_point is not None else 0, point.ts if point is not None else 0)
        
    if ts_delta < 0:
        log.warning('Negative time delta (%d); %s', ts_delta, point)
        # Ignore the point
        delete_count += 1
        return output

    if ts_delta == 0:
        log.warning('Duplicate point; %s', point)
        # Ignore the point
        delete_count += 1
        return output

    while ts_delta > 1:
        # Interpolate a new point mediating point and next point
        new_point = inter_f(previous_point, point, ts_delta)
        __add_point(new_point, output)
        log.info('Adding interpolated point %d between %d and %d', new_point.ts, previous_point.ts, point.ts)
        log.debug('Interpolated point: {%s}', point)
        insert_count += 1

        # Recalculate delta
        previous_point = new_point
        ts_delta = get_ts_delta(previous_point, point)
        log.debug('interpolate_point: ts_delta=%d; ts=[%d >> %d]', ts_delta, previous_point.ts if previous_point is not None else 0, point.ts if point is not None else 0)

    # Add initial point
    __add_point(point, output)

    if insert_count > 0:
        log.info('Added %d point(s) by interpolation', insert_count)
    if delete_count > 0:
        log.info('Removed %d point(s) by interpolation', delete_count)

    return output
