"""
  Module providing functions and classes for representing GPS data recorded from
  GPS data loggers.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (04 Feb 2015)
"""

from datetime import datetime
from math import floor, hypot

__author__ = 'sroberts'
__version__ = 1.0


class GPSPoint:

    lat = 0.0
    lon = 0.0
    x = 0
    y = 0
    a = 0
    s = 0.0
    ts = datetime.utcnow()

    def __repr__(self):
        return "<{}> ({},{}) [{},{}] / {}m / {:.2f}km/h".format(
            self.ts, self.lat, self.lon, self.x, self.y, self.a, self.s)


class LinkedGPSPoint(GPSPoint):

    next_point = None

    def __init__(self, point, next_point):
        self.lat = point.lat
        self.lon = point.lon
        self.x = point.x
        self.y = point.y
        self.a = point.a
        self.s = point.s
        self.ts = point.ts
        self.next_point = next_point

    def as_list(self):
        ps = []
        next_point = self
        while next_point is not None:
            ps.append(next_point)
            next_point = next_point.next_point

        return ps

    @staticmethod
    def from_list(point_list):
        points = []
        points.extend(point_list)
        points.reverse()
        last_point = None
        for p in points:
            last_point = LinkedGPSPoint(p, last_point)

        return last_point


def __interpolation_delta(this_point, next_point):
    # return (next_point.ts - this_point.ts).seconds
    return floor(next_point.ts.timestamp() - this_point.ts.timestamp())


def __linear_interpolate_f(f1, f2):
    return f1 + ((f2 - f1) / 2.0)


def __linear_interpolate_i(i1, i2):
    return floor(i1 + ((i2 - i1) / 2))


def __linear_interpolate_t(t1, t2):
    return datetime.fromtimestamp(__linear_interpolate_i(t1.timestamp(), t2.timestamp()), t1.tzinfo)


def calc_avg_speed(points):
    return sum(list(map(lambda p: p.s, points))) / len(points)


def calc_hi_alt(points):
    return max(list(map(lambda p: p.a, points)))


def calc_low_alt(points):
    return min(list(map(lambda p: p.a, points)))


def calc_sus_speed(points, secs):
    ss = 0.0
    for i in range(0, len(points)):
        ss = max(ss, min([p.s for p in points[i:i + secs]]))
    return ss


def calc_top_speed(points):
    return max(list(map(lambda p: p.s, points)))


def calc_linear_distance(point1, point2):
    return hypot(point1.x - point2.x, point1.y - point2.y)


def calc_vertical_distance(point1, point2):
    return point1.a - point2.a


def calc_total_ascent(points):
    va = 0.0
    for i in range(1, len(points)):
        va += abs(max(0, calc_vertical_distance(points[i - 1], points[i])))


def calc_total_descent(points):
    vd = 0.0
    for i in range(1, len(points)):
        vd += abs(min(0, calc_vertical_distance(points[i - 1], points[i])))

    return vd


def calc_total_distance(points):
    td = 0.0
    for i in range(1, len(points)):
        td += calc_linear_distance(points[i - 1], points[i])

    return td


def interpolate_point(point1, point2):
    rp = GPSPoint()
    rp.lat = __linear_interpolate_f(point1.lat, point2.lat)
    rp.lon = __linear_interpolate_f(point1.lon, point2.lon)
    rp.x = __linear_interpolate_i(point1.x, point2.x)
    rp.y = __linear_interpolate_i(point1.y, point2.y)
    rp.a = __linear_interpolate_i(point1.a, point2.a)
    rp.s = __linear_interpolate_f(point1.s, point2.s)
    rp.ts = __linear_interpolate_t(point1.ts, point2.ts)
    return rp


def interpolate_linked_point(linked_point):

    this_point = linked_point

    while this_point is not None and this_point.next_point is not None:
        next_point = this_point.next_point

        # Calculate time between points
        delta = __interpolation_delta(this_point, next_point)

        if delta < 0:
            # Negative delta, remove point
            this_point.next_point = next_point.next_point
            # log.warn('Negative time delta (%d) at node %d', delta, counter)

            # Increment counter
            # count_removed += 1
            # counter += 1

        # if delta == 0 and deDup:
            # Duplicate, remove point
        #    this_point.next_point = next_point.next_point
            # log.debug('Removed duplicate node at %d', counter)

            # Increment counter
            # count_removed += 1
            # counter += 1

        while delta > 1:
            # Interpolate a new point mediating this node and next node
            this_point.next_point = LinkedGPSPoint(interpolate_point(this_point, this_point.next_point)
                                                   , this_point.next_point)

            # log.debug('Created new node at %d:', counter)
            # log.debug('    newNode := %s', newNode)

            # Recalculate delta
            next_point = this_point.next_point
            delta = __interpolation_delta(this_point, next_point)
            # log.debug('Node %d: delta %d', counter, delta)

            # Increment counters
            # count_added += 1
            # counter += 1

        # Move to next node
        this_point = next_point
