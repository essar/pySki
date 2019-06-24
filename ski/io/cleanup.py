"""
"""
import logging

from math import atan2, degrees, floor, hypot, tan
from ski.config import config
from ski.data.commons import EnrichedPoint, LinkedPoint
from ski.data.coordinate import WGSCoordinate, WGStoUTM

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


outlyer_max_speed = config['cleanup']['outlyer_max_speed']
outlyer_max_speed_factor = config['cleanup']['outlyer_max_speed_factor']


def __calculate_coords(point):
    # Cartesian X & Y
    wgs = WGSCoordinate(point.lat, point.lon)
    utm = WGStoUTM(wgs)
    log.debug('wgs: %s', wgs)
    log.debug('utm: %s', utm)
    point.x = utm.x
    point.y = utm.y


def __calculate_vector(x_distance, y_distance):
    # Calculate distance using hypotenuse of X & Y
    dst = hypot(x_distance, y_distance)
    # Calculate degrees using the arc-tangent of X & Y
    hdg = degrees(atan2(x_distance, y_distance))
    return (dst, hdg)


def __calculate_xy_distances(prev_point, point):
    if prev_point == None or point == None:
        return (0, 0)

    # Calculate distance using X & Y & pythag...
    x_distance = point.x - prev_point.x
    y_distance = point.y - prev_point.y
    return (x_distance, y_distance)


def __get_distance(prev_point, point):
    (dist, head) = __calculate_vector(*__calculate_xy_distances(prev_point, point))
    return dist


def __get_heading(prev_point, point):
    (dist, head) = __calculate_vector(*__calculate_xy_distances(prev_point, point))
    return head


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


def __process_linked_point(linked_point, inter_f, output=[]):
    """
    """
    # Initialise with parameter value
    p = linked_point
    insert_count = 0
    while(p != None and p.next_point != None):
        # Calculate time delta
        ts_delta = __get_ts_delta(p)
        
        if ts_delta < 0:
            log.warning('Negative time delta (%d); %s', ts_delta, p)
            # Delete the point
            p.next_point = p.next_point.next_point
        if ts_delta == 0:
            log.warning('Duplicate point; %s', p)
            # Delete the point
            lp.next_point = p.next_point.next_point
        while ts_delta > 1:
            new_p = interpolate_point(p, linear_interpolate, ts_delta)
            log.debug('Interpolated point: %010d -> [%010d] -> %010d', p.point.ts, new_p.point.ts, new_p.next_point.point.ts)

            insert_count += 1

            # Recalculate delta
            ts_delta = __get_ts_delta(p)

        # Move to next node
        prev_point = p.point
        p = p.next_point

        calculate_point_deltas(prev_point, p.point)
        output.append(p.point)
        log.debug('Cleaned point: %s', p.point)

    if insert_count > 0:
        log.info('Added %d point(s) by interpolation at %010d', insert_count, linked_point.next_point.point.ts)



def calculate_point_deltas(prev_point, point):
    # Skip if no previous point provided
    if prev_point == None:
        return

    # Calculate X & Y distances
    (x, y) = __calculate_xy_distances(prev_point, point)

    # Get movement vector
    (point.dst, point.hdg) = __calculate_vector(x, y)

    # Calculate speed and altitude deltas
    point.alt_d = point.alt - prev_point.alt
    point.spd_d = point.spd - prev_point.spd
    point.hdg_d = point.hdg - prev_point.hdg
    log.debug('deltas: x=%.2f, y=%.2f, dst=%.2f, hdg=%05.1f, alt_d=%04d, spd_d=%.2f, hsg_d=%05.1f', x, y, point.dst, point.hdg, point.alt_d, point.spd_d, point.hdg_d)


def cleanup_point(point, output=[], outlyers=[]):
    """
    """
    log.debug('Cleaning point: %s', point)

    # Calculate the X * Y for each point
    __calculate_coords(point)

    # Skip first point
    if len(output) == 0:
        output.append(point)
        return

    # Previous point is last point in output list
    prev_point = output[-1]

    # Test to see if the point is an outlyer
    if is_outlyer(prev_point, point):
        # Add to the outlyers list
        outlyers.append(point)
        # Move on to the next point - do not add to the output list
        log.info('Removed outlying point; ts=%010d', point.ts)
        return

    # Put points into a linked point
    lp = LinkedPoint(prev_point, point)

    # Interpolate and process point
    __process_linked_point(lp, linear_interpolate, output)


def cleanup_points(points, output=[], outlyers=[]):
    """
    """
    # Initialise counters
    insert_count = 0
    delete_count = 0

    for point in points:
        cleanup_point(point, output, outlyers)

    log.info('%d points input, %d points output; %d outlyers', len(points), len(output), len(outlyers))


def linear_interpolate(p1, p2, delta):
    p = EnrichedPoint()
    p.ts  = __linear_interpolate_i(p1.ts, p2.ts, delta)
    p.lat = __linear_interpolate_f(p1.lat, p2.lat, delta)
    p.lon = __linear_interpolate_f(p1.lon, p2.lon, delta)
    p.x   = __linear_interpolate_i(p1.x, p2.x, delta)
    p.y   = __linear_interpolate_i(p1.y, p2.y, delta)
    p.alt = __linear_interpolate_i(p1.alt, p2.alt, delta)
    p.spd = __linear_interpolate_f(p1.spd, p2.spd, delta)

    return p


def is_outlyer(prev_point, point):
    # Skip if no previous point provided
    if prev_point == None:
        return False
    
    # calculate distance travelled in metres
    calc_dist = __get_distance(prev_point, point)
    ts_delta = __get_ts_delta2(prev_point, point)
    
    # calculate speed (convert metres per second -> km per hour)
    calc_spd = (calc_dist / ts_delta) * 3.60
    calc_spd_factor = 1 if point.spd == 0.0 else calc_spd / max(1, point.spd)
    log.debug('outlyer: ts_delta=%d, calc_dist=%.2f, gps_speed=%.2f, calc_speed=%.4f, calc_spd_factor=%.3f', ts_delta, calc_dist, point.spd, calc_spd, calc_spd_factor)

    # Compare calculated speed against max speed
    if calc_spd > outlyer_max_speed:
        log.info('Calculated speed (%.2f) exceeds threshold', calc_spd)
        return True

    # Compare calculated speed factor against max speed factor and inverse (e.g. 1/3) speed factor
    if calc_spd_factor > outlyer_max_speed_factor or calc_spd_factor < (1 / outlyer_max_speed_factor):
        log.info('Calculated speed (%.2f) exceeds factor threshold (%.1fx)', calc_spd, calc_spd_factor)
        return True

    return False


def interpolate_point(point, inter_f, ts_delta=0):
    """
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

