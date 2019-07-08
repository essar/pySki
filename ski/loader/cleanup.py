"""
"""
import logging

from math import atan2, degrees, floor, hypot, tan
from ski.config import config
from ski.data.coordinate import WGSCoordinate, WGStoUTM
from ski.data.pointutils import get_distance, get_heading, get_ts_delta
from ski.loader.interpolate import interpolate_point, linear_interpolate
from ski.loader.outlyer import is_outlyer


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

skip_interpolate = config['cleanup']['skip_interpolate']
skip_outlyers = config['cleanup']['skip_outlyers']


def calculate_coords(point):
    # Cartesian X & Y
    wgs = WGSCoordinate(point.lat, point.lon)
    utm = WGStoUTM(wgs)
    log.debug('calculate_coords: wgs=%s; utm=%s', wgs, utm)
    point.x = utm.x
    point.y = utm.y
    log.debug('calculate_coords: x=%.2f, y=%05.1f', point.x, point.y)


def calculate_deltas(points, prev_point, output):
    for point in points:
        # Calculate point_deltas
        calculate_point_deltas(prev_point, point)
        output.append(point)
        # Move to next point
        prev_point = point


def calculate_point_deltas(prev_point, point):
    # Skip if no previous point provided
    if prev_point == None:
        return

    # Get movements
    point.dst = get_distance(prev_point, point)
    point.hdg = get_heading(prev_point, point)
    log.debug('calculate_point_deltas: dst=%.2f, hdg=%05.1f', point.dst, point.hdg)

    # Calculate speed and altitude deltas
    point.alt_d = point.alt - prev_point.alt
    point.spd_d = point.spd - prev_point.spd
    point.hdg_d = point.hdg - prev_point.hdg
    log.debug('calculate_point_deltas: alt_d=%04d, spd_d=%.2f, hsg_d=%05.1f', point.alt_d, point.spd_d, point.hdg_d)


def cleanup_points(points, output=[], outlyers=[]):
    """
    """
    log.info('Starting cleanup of %d points', len(points))

    for point in points:
        log.debug('Cleaning point {%s}', point)

        if point is None:
            log.warning('<None> found in points list; ignoring')
            return

        # Calculate the X & Y for each point
        calculate_coords(point)

        # Previous point is last point in output list
        prev_point = output[-1] if len(output) > 0 else None
        log.debug('cleanup_points: prev_point={%s}', prev_point)

        if not skip_outlyers:
            # Test to see if the point is an outlyer
            if is_outlyer(prev_point, point):
                # Add to the outlyers list
                outlyers.append(point)
                # Move on to the next point - do not add to the output list
                continue

        if not skip_interpolate:
            # Interpolate any missing points
            interpolated_points = interpolate_point(linear_interpolate, point, prev_point)
            # Calculate deltas for all points output from interpolator
            calculate_deltas(interpolated_points, prev_point, output)

        else:
            # Calculate deltas for point
            calculate_deltas([point], prev_point, output)

    log.info('Cleanup complete; %d points, %d outlyers', len(output), len(outlyers))
