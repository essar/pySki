"""
"""
import logging

from math import ceil, floor
from ski.config import config
from ski.data.commons import EnrichedPoint, EnrichedWindow

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class PointWindow:

    FORWARD  = 1
    MIDPOINT = 2
    BACKWARD = 3

    def __init__(self, window_type, size):

        # Do not allow a midpoint to be created of even length
        if window_type == PointWindow.MIDPOINT and size % 2 == 0:
            raise ValueError('Midpoint window must be of odd length')

        self.window_type = window_type
        self.size = size


    def for_points(self, points, position=0):
        if self.window_type == PointWindow.FORWARD:
            # Forward load from the position
            window_start = max(0, position)
            window_end = min(len(points), (position + self.size))

        elif self.window_type == PointWindow.MIDPOINT:
            # Load equally either side of position
            mp = self.size / 2

            window_start = max(0, position - (min(len(points), (position + ceil(mp))) - position) + 1, position - floor(mp))
            window_end = min(len(points), position + (position - max(0, position - floor(mp))) + 1, (position + ceil(mp)))

        elif self.window_type == PointWindow.BACKWARD:
            # Backward load from the position
            window_start = max(0, position - self.size + 1)
            window_end = min(len(points), position + 1)

        window = points[window_start:window_end]
        window_full = (len(window) == self.size)
        log.debug('Window is %s', 'full' if window_full else 'not full')
        return window



def __avg(values):
    return float(sum(values)) / max(1, len(values))


def __enriched_alt_vals(window, points, position):
    return {
        'alt_delta' : window_alt_delta(window, points, position),
        'alt_gain'  : window_alt_cuml_gain(window, points, position),
        'alt_loss'  : window_alt_cuml_loss(window, points, position),
        'alt_max'   : window_alt_max(window, points, position),
        'alt_min'   : window_alt_min(window, points, position)
    }


def __enriched_speed_vals(window, points, position):
    return {
        'speed_min'   : window_speed_min(window, points, position),
        'speed_max'   : window_speed_max(window, points, position),
        'speed_ave'   : window_speed_ave(window, points, position),
        'speed_delta' : window_speed_delta(window, points, position)
    }


def enrich_points(points, windows, head=[], min_tail=1, overflow=[]):
    # Create position counter, start above head values
    position = len(head)

    # Process as many points as we can
    while len(points[position:]) >= min_tail:
        p = points[position]

        for k in windows:
            # Get window based on key and set to current position
            w = windows[k]

            # Build a dict of enriched values
            vals = get_enriched_data(w, points, position)

            # Add the enrichment data to the point, using the input dict key
            p.windows[k] = EnrichedWindow(**vals)
            log.debug('Enriched data: %s=%s', k, vals)

        log.info('Added windows: %s', list(p.windows.keys()))

        # Increment to next position
        position += 1
        
    # Return any unprocessed elements
    overflow.extend(points[position:])


def get_enriched_data(window, points, position=0):
    # Build a dict of enriched values
    data = {
        'distance' : window_distance(window, points, position)
    }
    data.update(__enriched_alt_vals(window, points, position))
    data.update(__enriched_speed_vals(window, points, position))
    return data


def window_alt_delta(window, points, position):
    w = window.for_points(points, position)
    return w[-1].alt - w[0].alt


def window_alt_cuml_gain(window, points, position):
    w = window.for_points(points, position)
    return sum([p.alt_d for p in w if p.alt_d > 0])


def window_alt_cuml_loss(window, points, position):
    w = window.for_points(points, position)
    return sum([p.alt_d for p in w if p.alt_d < 0])


def window_alt_max(window, points, position):
    w = window.for_points(points, position)
    return max([p.alt for p in w])


def window_alt_min(window, points, position):
    w = window.for_points(points, position)
    return min([p.alt for p in w])


def window_distance(window, points, position):
    w = window.for_points(points, position)
    return sum([p.dst for p in w])


def window_speed_ave(window, points, position):
    w = window.for_points(points, position)
    return __avg([p.spd for p in w])


def window_speed_delta(window, points, position):
    w = window.for_points(points, position)
    return w[-1].spd - w[0].spd


def window_speed_max(window, points, position):
    w = window.for_points(points, position)
    return max([p.spd for p in w])


def window_speed_min(window, points, position):
    w = window.for_points(points, position)
    return min([p.spd for p in w])

