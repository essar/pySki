"""
"""
import logging

from math import atan2, degrees, hypot


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def __calculate_vector(x_distance, y_distance):
    # Calculate distance using hypotenuse of X & Y
    dst = hypot(x_distance, y_distance)
    # Calculate degrees using the arc-tangent of X & Y
    hdg = degrees(atan2(x_distance, y_distance))
    return (dst, hdg)


def __calculate_xy_distances(prev_point, point):
    if prev_point == None or point == None:
        return (0, 0)

    # Calculate X & Y distances
    x_distance = point.x - prev_point.x
    y_distance = point.y - prev_point.y
    return (x_distance, y_distance)


def get_distance(prev_point, point):
    (dist, head) = __calculate_vector(*__calculate_xy_distances(prev_point, point))
    return dist


def get_heading(prev_point, point):
    (dist, head) = __calculate_vector(*__calculate_xy_distances(prev_point, point))
    return head


def get_ts_delta(prev_point, point):
    if point == None or prev_point == None:
        return 1
    # Get difference in timestamps
    return point.ts - prev_point.ts
