"""
"""
import logging

from math import floor
from ski.config import config
from ski.data.commons import ExtendedGPSPoint, LinkedPoint

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



def __get_ts_delta2(prev_point, point):
    if point == None or prev_point == None:
        return 0

    # Get difference in timestamps
    return point.ts - prev_point.ts


def __get_ts_delta(p):
    np = p.next_point
    return __get_ts_delta2(p.point, np.point)


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


def interpolate_linked_point(point, inter_f, ts_delta=0):
    """
    Interpolate across a linked point to complete any 
    """
    if ts_delta == 0:
        # May not have been passed in so try and recalculate it
        ts_delta = __get_ts_delta(point)

    # Skip if we're not actually missing any points
    if ts_delta <= 1:
        return None

    next_point = point.next_point

    # Interpolate a new point mediating point and next point
    new_point = LinkedPoint(inter_f(point.point, next_point.point, ts_delta))

    # Insert the new point between our existing points
    new_point.next_point = next_point
    point.next_point = new_point

    return new_point


def interpolate_points(previous_point, point, inter_f, output=[]):
    """
    """
    # Initialise with parameter values
    p = LinkedPoint(previous_point, point)
    insert_count = 0
    delete_count = 0

    while p != None:
        if p.next_point == None:
            # Last point in the list; add and end
            output.append(p.point)
            p = None

        else:
            # Calculate time delta
            ts_delta = __get_ts_delta(p)
            
            if ts_delta < 0:
                log.warning('Negative time delta (%d); %s', ts_delta, p)
                # Delete the point
                p.next_point = p.next_point.next_point
                delete_count += 1
                continue

            if ts_delta == 0:
                log.warning('Duplicate point; %s', p)
                # Delete the point
                p.next_point = p.next_point.next_point
                delete_count += 1
                continue

            while ts_delta > 1:
                new_p = interpolate_linked_point(p, linear_interpolate, ts_delta)
                log.debug('interpolate_points: ts_delta=%d; new_p=%s', ts_delta, new_p)
                insert_count += 1

                # Recalculate delta
                ts_delta = __get_ts_delta(p)

            # Move to next node
            prev_point = p.point
            p = p.next_point

            output.append(p.point)


    if insert_count > 0:
        log.info('%010d:Added %d point(s) by interpolation', point.ts, insert_count)
    if delete_count > 0:
        log.info('%010d:Removed %d point(s) by interpolation', point.ts, delete_count)
