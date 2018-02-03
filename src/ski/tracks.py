"""
  Module providing functions and classes for representing ski tracks.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (04 Feb 2015)
"""
from collections import OrderedDict
from datetime import datetime
from logging import getLogger, DEBUG
from math import hypot, cos, sin, atan2
import ski.gps as gps

__author__ = 'Steve Roberts'
__version__ = 1.0

log = getLogger(__name__)
log.setLevel(DEBUG)

################################
# TRACK CONSTANTS
########

MODE_STOP = 0
MODE_SKI = 1
MODE_LIFT = 2


################################
# TRACK CLASSES
########

class ControlPoint:
    """
    ControlPoint : Used in plotting curves and calculating curve lengths.
    """

    def __init__(self):
        self.x = 0   # X coordinate
        self.y = 0   # Y coordinate

    def as_tuple(self):
        return self.x, self.y


class TrackInfo:
    """
    TrackInfo : Contains summary information about a set of Track Points.
    """

    def __init__(self):
        # General track fields
        self.start_time = datetime.utcnow()
        self.end_time = datetime.utcnow()

        self.low_alt = 0.0
        self.hi_alt = 0.0

        self.avg_speed = 0.0
        self.sus_speed = 0.0
        self.sus_speed_secs = 0
        self.top_speed = 0.0

        self.total_distance = 0.0
        self.v_distance = 0.0

        # TODO Move to tracks summary object
        self.ski_distance = 0.0

        self.lift_count = 0
        self.run_count = 0

        self.lift_points = 0
        self.ski_points = 0
        self.stop_points = 0

    def as_dict(self):
        return {
            "startTime": self.start_time.isoformat(),
            "endTime": self.end_time.isoformat(),
            "tzOffset": self.start_time.strftime('%z'),
            "lowAlt": self.low_alt,
            "lowAltStr": "{:,.0f}m".format(self.low_alt),
            "hiAlt": self.hi_alt,
            "hiAltStr": "{:,.0f}m".format(self.hi_alt),
            "avgSpeed": self.avg_speed,
            "avgSpeedStr": "{:.2f}kph".format(self.avg_speed),
            "susSpeed": self.sus_speed,
            "susSpeedStr": "{:.2f}kph".format(self.sus_speed),
            "susSpeedSecs": self.sus_speed_secs,
            "susSpeedSecsStr": "{:0f}s".format(self.sus_speed_secs),
            "topSpeed": self.top_speed,
            "topSpeedStr": "{:.2f}kph".format(self.top_speed),
            "totalDistance": self.total_distance,
            "totalDistanceStr": "{:.2f}km".format(self.total_distance / 1000.0),
            "skiDistance": self.ski_distance,
            "skiDistanceStr": "{:.2f}km".format(self.ski_distance / 1000.0),
            "vDistance": self.v_distance,
            "vDistanceStr": "{:,.0f}m".format(self.v_distance),
            "liftCount": self.lift_count,
            "liftCountStr": "{:.0f}".format(self.lift_count),
            "runCount": self.run_count,
            "liftPoints": self.lift_points,
            "skiPoints": self.ski_points,
            "stopPoints": self.stop_points
        }


class TrackPoint:
    """
    TrackPoint: Single point on a track. Has position, altitude, speed and time elements
    """

    def __init__(self):

        # Core GPS point fields
        self.lat = 0.0               # Latitude
        self.lon = 0.0               # Longitude
        self.x = 0                   # X coordinate (relative)
        self.y = 0                   # Y coordinate (relative)
        self.a = 0.0                 # Altitude
        self.s = 0.0                 # Speed
        self.ts = datetime.utcnow()  # Timestamp

        # Delta fields
        self.adt = 0.0               # Altitude change
        self.d = 0                   # Linear distance
        self.sdt = 0.0               # Speed change
        self.t = 0                   # Time (relative seconds)

        # Additional fields
        self.cp1 = ControlPoint()    # Curve control point 1
        self.cp2 = ControlPoint()    # Curve control point 2
        self.m = MODE_STOP           # Mode

    def as_dict(self):
        return {
            'lat': self.lat,
            'lon': self.lon,
            'x': self.x,
            'y': self.y,
            'cp1': {'x': self.cp1.x, 'y': self.cp1.y},
            'cp2': {'x': self.cp2.x, 'y': self.cp2.y},
            'a': self.a,
            's': self.s,
            't': self.t,
            'ts': self.ts.isoformat(),
            'm': self.m
        }

    def __repr__(self):
        return "{{x : {}, y : {}, cp1 : {{x : {}, y : {}}}, cp2 : {{x : {}, y : {}}}}}".format(
            self.x, self.y, self.cp1.x, self.cp1.y, self.cp2.x, self.cp2.y)


################################
# TRACK FUNCTIONS
########

def __calc_theta(point1, point2):

    x = point2.x - point1.x
    y = point2.y - point1.y

    t = atan2(y, x)

    return t


def __calc_track_distance(points):
    td = 0.0
    for i in range(1, len(points)):
        td += gps.calc_linear_distance(points[i - 1], points[i])

    return td / 100000.0  # Convert back to km


def calc_control_point(last_point, this_point, next_point):

    if this_point is None:
        return

    elif last_point is None:

        t = __calc_theta(this_point, next_point)

        # First point
        cp1 = ControlPoint()
        cp1.x = this_point.x
        cp1.y = this_point.y
        this_point.cp1 = cp1

        cp2 = ControlPoint()
        # a2 = (next_point.x - this_point.x) * cos(t)
        a2 = hypot(next_point.x - this_point.x, next_point.y - this_point.y) / 3
        cp2.x = this_point.x + (a2 * cos(t))
        cp2.y = this_point.y + (a2 * sin(t))
        this_point.cp2 = cp2

    elif next_point is None:

        t = __calc_theta(last_point, this_point)

        cp1 = ControlPoint()
        # a1 = (this_point.y - last_point.y) * cos(t)
        a1 = hypot(this_point.x - last_point.x, this_point.y - last_point.y) / 3
        cp1.x = this_point.x - (a1 * cos(t))
        cp1.y = this_point.y - (a1 * sin(t))
        this_point.cp1 = cp1

        # Last point
        cp2 = ControlPoint()
        cp2.x = this_point.x
        cp2.y = this_point.y
        this_point.cp2 = cp2

    else:

        t = __calc_theta(last_point, next_point)

        cp1 = ControlPoint()
        # a1 = (this_point.y - last_point.y) * cos(t)
        a1 = hypot(this_point.x - last_point.x, this_point.y - last_point.y) / 3
        cp1.x = this_point.x - (a1 * cos(t))
        cp1.y = this_point.y - (a1 * sin(t))
        this_point.cp1 = cp1

        cp2 = ControlPoint()
        # a2 = (next_point.x - this_point.x) * cos(t)
        a2 = hypot(next_point.x - this_point.x, next_point.y - this_point.y) / 3
        cp2.x = this_point.x + (a2 * cos(t))
        cp2.y = this_point.y + (a2 * sin(t))
        this_point.cp2 = cp2


def calc_control_points(point_list):

    # Create reference copy
    pl = point_list[:]

    last_point = None
    this_point = pl.pop(0)
    next_point = pl.pop(0)

    while this_point is not None:

        # Calculate delta points
        if last_point is not None:
            this_point.adt = this_point.a - last_point.a
            this_point.d = gps.calc_linear_distance(last_point, this_point)
            # Override speed if distance is near zero
            this_point.s = 0.0 if this_point.d < 0.3 else this_point.s
            this_point.sdt = this_point.s - last_point.s

        calc_control_point(last_point, this_point, next_point)

        # Move to next point
        last_point = this_point
        this_point = next_point
        next_point = pl.pop(0) if len(pl) > 0 else None


def calc_mode(current_mode, point, point_window):
    # Validate arguments
    if type(current_mode) is not int:
        raise ValueError('Expected String at argument 1', type(current_mode))
    # if type(point) is not type(TrackPoint):
    #    raise ValueError('Expected TrackPoint at argument 2', type(point))
    if type(point_window) is not list:
        raise ValueError('Expected list at argument 3')

    # Calculate window properties
    # window_length = float(len(point_window))

    # moving_d = 0.2
    moving_s = 0.2

    alts = list(map(lambda tp: tp.adt, point_window))  # Get altitude deltas from all points in window
    ascent = sum(alts)                                 # Get total altitude change
    ascending = float(sum([1 for adt in alts if adt > 0])) / len(alts)   # Count all positive alt deltas
    descending = float(sum([1 for adt in alts if adt < 0])) / len(alts)  # Count all negative alt deltas

    # dists = list(map(lambda tp: tp.d, point_window))   # Get linear distances from all points in window
    # moving = float(sum([1 for d in dists if d >= moving_d])) / len(dists)    # Count all positive distances
    # stopped = float(sum([1 for d in dists if d < moving_d])) / len(dists)  # Count all near zero distances
    speeds = list(map(lambda tp: tp.s, point_window))  # Get speed from all points in window
    moving = float(sum([1 for s in speeds if s > moving_s])) / len(speeds)  # Count all positive distances
    stopped = float(sum([1 for s in speeds if s <= moving_s])) / len(speeds)  # Count all zero distances

    if current_mode == MODE_STOP:
        # Stopped, but now moving
        if point.s > moving_s and moving >= 0.9:
            if point.adt > 0 and ascent > 0 and ascending > 0.5:
                # Altitude ascending
                log.debug('%s->%s, at %s.', current_mode, MODE_LIFT, point)
                log.debug('    alts=%s', alts)
                # log.debug('    dists=%s', dists)
                log.debug('    d=%.1f; moving=%.2f.', point.d, moving)
                log.debug('    adt=%.1f, ascent=%.1f, ascending=%.2f', point.adt, ascent, ascending)
                return MODE_LIFT
            if point.adt < 0 and ascent < 0 and descending > 0.5:
                # Altitude descending
                log.debug('%s->%s, at %s.', current_mode, MODE_SKI, point)
                log.debug('    alts=%s', alts)
                # log.debug('    dists=%s', dists)
                log.debug('    d=%.1f; moving=%.2f.', point.d, moving)
                log.debug('    adt=%.1f, ascent=%.1f, descending=%.2f', point.adt, ascent, descending)
                return MODE_SKI

    if current_mode == MODE_SKI:
        # Skiing, but now not moving
        if point.s < moving_s and stopped > 0.9:
            log.debug('%s->%s, at %s.', current_mode, MODE_STOP, point)
            log.debug('    alts=%s', alts)
            # log.debug('    dists=%s', dists)
            log.debug('    d=%.1f; stopped=%.2f.', point.d, stopped)
            return MODE_STOP

        # Skiing, but now on a lift
        if point.adt > 0 and ascent > 0 and ascending > 0.3:
            log.debug('%s->%s, at %s.', current_mode, MODE_LIFT, point)
            log.debug('    alts=%s', alts)
            # log.debug('    dists=%s', dists)
            log.debug('    adt=%.1f, ascent=%.1f, ascending=%.2f', point.adt, ascent, ascending)
            return MODE_LIFT

    if current_mode == MODE_LIFT:
        # On a lift, but now not moving
        if point.s < moving_s and stopped > 0.9:
            log.debug('%s->%s, at %s.', current_mode, MODE_STOP, point)
            log.debug('    alts=%s', alts)
            # log.debug('    dists=%s', dists)
            log.debug('    d=%.1f; stopped=%.2f.', point.d, stopped)
            return MODE_STOP

        # On a lift, but now skiing
        if point.adt <= 0 and ascent < 0 and descending > 0.3:
            log.debug('%s->%s, at %s.', current_mode, MODE_SKI, point)
            log.debug('    alts=%s', alts)
            # log.debug('    dists=%s', dists)
            log.debug('    adt=%.1f, ascent=%.1f, descending=%.2f', point.adt, ascent, descending)
            return MODE_SKI

    # No matches, so stay in same mode
    return current_mode


def build_tracks(point_list):

    all_tracks = OrderedDict()
    current_track = []

    # Properties for mode identification
    window_sz = 20
    window_start = 0
    mode = MODE_STOP

    for tp in point_list:

        # Previous mode
        old_mode = mode
        # Calculate window end
        window_end = window_start + window_sz
        # Process mode
        mode = calc_mode(old_mode, tp, point_list[window_start:window_end])
        # Update point mode
        tp.m = mode

        if old_mode != mode:
            # Mode has changed - new track
            all_tracks[current_track[0]] = current_track
            # Reset current track
            current_track = []

        # Add point to current track
        current_track.append(tp)

        # Increment window
        window_start += 1

    return all_tracks


def group_tracks(track_list):

    track_groups = [[], [], []]
    tk_list = list(track_list.keys())
    tk_list_merged = []

    while len(tk_list) > 0:

        ms = [t.m for t in tk_list[0:3]]
        t = track_list.get(tk_list[0])

        if len(t) < 5:
            # Ignore and merge with previous
            print("Less than 10s")
            tk_list_merged.append(tk_list[0])
            tk_list.pop(0)
        elif ms == [MODE_LIFT, MODE_STOP, MODE_LIFT]:
            print("LIFT-STOP-LIFT")
            tk_list_merged.append(tk_list[0])
            tk_list.pop(0)
            tk_list.pop(0)
        elif ms == [MODE_SKI, MODE_STOP, MODE_SKI] and len(track_list.get(tk_list[1])) < 30:
            print("SKI-STOP-SKI (stop < 30)")
            tk_list_merged.append(tk_list[0])
            tk_list.pop(0)
            tk_list.pop(0)
        else:
            tk_list_merged.append(tk_list[0])
            tk_list.pop(0)

    for k in tk_list_merged:
        track_groups[k.m].append(track_list.get(k))

    return track_groups


def merge_tracks(track1, *track2):

    new_track = []
    mode = track1.m

    # Add all points in track 1 to new track
    new_track.extend(track1)

    # Add all points in track 2 to new track, changing mode
    for t in track2:
        for p in t:
            p.m = mode
            new_track.append(p)

    return new_track


def calc_modes(point_list):

    window_sz = 20
    window_start = 0
    all_tracks = [[], [], []]
    current_track = []
    mode = MODE_STOP

    for tp in point_list:
        # Previous mode
        old_mode = mode
        # Calculate window end
        window_end = window_start + window_sz
        # Process mode
        mode = calc_mode(old_mode, tp, point_list[window_start:window_end])
        # Update point mode
        tp.m = mode

        if old_mode != mode:
            # Mode has changed - new track
            all_tracks[old_mode].append(current_track)
            # Reset current track
            current_track = []
        # Add point to current track
        current_track.append(tp)

        # Increment window
        window_start += 1

    return all_tracks


def generate_track_info(ti, track_points):

    ti.start_time = track_points[0].ts
    ti.end_time = track_points[-1].ts

    ti.low_alt = gps.calc_low_alt(track_points)
    ti.hi_alt = gps.calc_hi_alt(track_points)

    ti.total_distance = __calc_track_distance(track_points)


def generate_lift_info(ti, lift_points, lift_tracks):

    ti.lift_count = len(lift_tracks)
    ti.lift_points = len(lift_points)


def generate_ski_info(ti, ski_points, ski_tracks):

    ti.avg_speed = gps.calc_avg_speed(ski_points)
    ti.sus_speed = gps.calc_sus_speed(ski_points, 10)
    ti.top_speed = gps.calc_top_speed(ski_points)
    ti.v_distance = gps.calc_total_descent(ski_points)
    ti.run_count = len(ski_tracks)
    ti.ski_points = len(ski_points)

    for st in ski_tracks:
        ti.ski_distance += __calc_track_distance(st)
