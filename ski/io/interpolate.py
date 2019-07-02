"""
"""
import logging

from math import floor
from ski.config import config
from ski.data.commons import ExtendedGPSPoint
from ski.io.cleanup import get_ts_delta

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def __add_point(point, output):
    log.debug('__add_point: %s', point)
    if type(point) != ExtendedGPSPoint:
        log.warning('Interpolator attempting to add %s object to output; expected ExtendedGPSPoint', type(point))
        return
    if point is not None:
        log.debug('__add_point: adding point to output: {%s}', point)
        output.append(point)
    log.debug('__add_point: output=%s', output)


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
    p.ts  = __linear_interpolate_i(p1.ts, p2.ts, delta)
    log.debug('linear_interpolate:  ts=%d|[%d]|%d; delta=%d', p1.ts, p.ts, p2.ts, delta)
    p.lat = __linear_interpolate_f(p1.lat, p2.lat, delta)
    log.debug('linear_interpolate: lat=%f|[%f]|%f; delta=%d', p1.lat, p.lat, p2.lat, delta)
    p.lon = __linear_interpolate_f(p1.lon, p2.lon, delta)
    log.debug('linear_interpolate: lon=%f|[%f]|%f; delta=%d', p1.lon, p.lon, p2.lon, delta)
    p.x   = __linear_interpolate_i(p1.x, p2.x, delta)
    log.debug('linear_interpolate:   x=%d|[%d]|%d; delta=%d', p1.x, p.x, p2.x, delta)
    p.y   = __linear_interpolate_i(p1.y, p2.y, delta)
    log.debug('linear_interpolate:   y=%d|[%d]|%d; delta=%d', p1.y, p.y, p2.y, delta)
    p.alt = __linear_interpolate_i(p1.alt, p2.alt, delta)
    log.debug('linear_interpolate: alt=%d|[%d]|%d; delta=%d', p1.alt, p.alt, p2.alt, delta)
    p.spd = __linear_interpolate_f(p1.spd, p2.spd, delta)
    log.debug('linear_interpolate: spd=%f|[%f]|%f; delta=%d', p1.spd, p.spd, p2.spd, delta)

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
    log.debug('interpolate_point: ts_delta=%d', ts_delta)
        
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
        log.info('Adding interpolated point: %s', new_point)
        insert_count += 1

        # Recalculate delta
        previous_point = new_point
        ts_delta = get_ts_delta(previous_point, point)
        log.debug('interpolate_point: ts_delta=%d', ts_delta)

    # Add initial point
    __add_point(point, output)

    if insert_count > 0:
        log.info('%010d:Added %d point(s) by interpolation', point.ts, insert_count)
    if delete_count > 0:
        log.info('%010d:Removed %d point(s) by interpolation', point.ts, delete_count)

    return output
