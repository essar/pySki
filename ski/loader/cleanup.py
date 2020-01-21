"""
Performs clean up operations on GPS points. First phase in data load pipeline.
[CLEANUP] -> ENRICH
"""
import logging
import time

from ski.config import config
from ski.logging import increment_stat, log_point
from ski.data.coordinate import WGSCoordinate, wgs_to_utm
from ski.data.pointutils import get_distance, get_heading, get_ts_delta
from ski.loader.interpolate import linear_interpolate
from ski.loader.outlyer import is_outlyer


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}

# Load config values
skip_interpolate = config['cleanup']['skip_interpolate']
skip_outlyers = config['cleanup']['skip_outlyers']


def calculate_coords(point):
    """
    Calculates the cartesian coordinates (X&Y) for a GPS point.
    @param point: the point to calculate coordinates for.
    """
    # Build WGS84 coordinate from latitude and longitude
    wgs = WGSCoordinate(point.lat, point.lon)
    # Convert to UTM
    utm = wgs_to_utm(wgs)

    # Extract cartesian X & Y
    point.x = utm.x
    point.y = utm.y
    log.debug('wgs=%s; utm=%s', wgs, utm)


def calculate_deltas(prev_point, point):
    """
    Calculate the delta values for two points.
    @param prev_point: the previous point.
    @param point: the point to calculate deltas for.
    """
    # Skip if no point or previous point provided
    if not (point is None or prev_point is None):
        # Calculate point movements
        point.dst = get_distance(prev_point, point)
        point.hdg = get_heading(prev_point, point)

        # Calculate speed and altitude deltas
        point.alt_d = point.alt - prev_point.alt
        point.spd_d = point.spd - prev_point.spd
        point.hdg_d = point.hdg - prev_point.hdg
        log.debug('calculate_deltas: dst=%.2f, hdg=%05.1f, alt_d=%04d, spd_d=%.2f, hsg_d=%05.1f',
                  point.dst, point.hdg, point.alt_d, point.spd_d, point.hdg_d)


def cleanup_points(points, outlyers=None):
    """
    Clean up a list of points, removing outlyers and interpolating gaps.
    @param points: List of points to clean up.
    @param outlyers: a list of points removed from the input, as outlyers.
    @return: a cleaned list of points, expanded with delta values.
    """

    if outlyers is None:
        outlyers = []

    start_time = time.time()

    # Prepare output list
    output = []

    prev_point = None

    # Loop through all points in input list
    for point in points:

        # Skip invalid values
        if point is None:
            log.warning('<None> found in points list; ignoring')
            continue

        # Calculate X & Y coordinates for point
        calculate_coords(point)

        if prev_point is None:
            # First point in the list

            # Record in pointlog
            log_point(point.ts, 'Clean up', ts=point.ts, **point.ext_values())

            # Add point to output
            output.append(point)
            prev_point = point
            continue

        if not skip_outlyers:
            # Test to see if the point is an outlyer
            if is_outlyer(prev_point, point):
                # Add to outlyers list
                outlyers.append(point)
                continue

        if not skip_interpolate:
            # Calculate the previous point by interpolation
            prev_point = interpolate_point(linear_interpolate, prev_point, point, output)

        # Calculate deltas for point
        calculate_deltas(prev_point, point)

        # Record in pointlog
        log_point(point.ts, 'Clean up', ts=point.ts, **point.ext_values())

        # Add point to output
        output.append(point)
        prev_point = point

    end_time = time.time()
    increment_stat(stats, 'process_time', (end_time - start_time))
    increment_stat(stats, 'point_count', len(points))
    increment_stat(stats, 'points_in', len(points))
    increment_stat(stats, 'points_out', len(output))

    return output


def interpolate_point(interp_f, prev_point, point, output):
    # Calculate time delta
    ts_delta = get_ts_delta(prev_point, point)

    if ts_delta < 0:
        # Point occurred before the previous point
        log.warning('[%010d] Dropping point; negative time delta', point.ts)
        # Ignore the point
        return prev_point

    if ts_delta == 0:
        # Point timestamp is equal to previous point
        log.warning('[%010d] Dropping point; duplicate timestamp', point.ts)
        # Ignore the point
        return prev_point

    while ts_delta > 1:
        # More than one second between points, so interpolate to fill the gap
        # Interpolate a new point mediating point and next point
        new_point = interp_f(prev_point, point, ts_delta)
        log.debug('Adding interpolated point: {%s}', new_point)
        # Calculate deltas for new point
        calculate_deltas(prev_point, new_point)
        # Add to output array
        output.append(new_point)

        # Recalculate delta
        prev_point = new_point
        ts_delta = get_ts_delta(prev_point, point)

    return prev_point
