"""
"""
import logging

from math import ceil, floor
from ski.config import config
from ski.data.pointutils import split_points
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
        return window



class WindowConfig:
    def __init__(self, windows={}, head_length=0, tail_length=0):
        self.windows = windows
        self.head_length = head_length
        self.tail_length = tail_length


window_config = WindowConfig(
    windows = {
        'fwd3' : PointWindow(PointWindow.FORWARD, 3)
    }, 
    head_length = 0,
    tail_length = 3
)


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


def enrich_points(points, head, body=[], tail=[], all_points=False):
    # Enrich points
    head_length = len(head)
    tail_length = 0 if all_points else window_config.tail_length # Check if buffer is full as non-full buffer would be zero tail
    
    # Prepend the head to the cleaned points and then split into head, body and tail
    split_points(head + points, head_length, tail_length, head, body, tail)
    log.debug('enrich_points: head=%s', head)
    log.debug('enrich_points: body=%s', body)
    log.debug('enrich_points: tail=%s', tail)

    enrich_windows(body, window_config.windows, head, tail)


def enrich_windows(points, windows, head=[], tail=[]):
    
    log.debug('enrich_windows: head=%d; points=%d; tail=%d', len(head), len(points), len(tail))

    # Create position counter, start above head values
    position = len(head)
    # Build an array that holds head, tail and points to enrich
    all_points = (head + points + tail)
    
    # Process as many points as we can
    while len(all_points[position:]) > len(tail):
        p = all_points[position]
        log.debug('p=%s', p)

        for k in windows:
            # Get window based on key and set to current position
            w = windows[k]

            # Build a dict of enriched values
            vals = get_enriched_data(w, all_points, position)
            
            # Add the enrichment data to the point, using the input dict key
            p.windows[k] = EnrichedWindow(**vals)
            log.debug('windows[%s]=%s', k, vals)

        log.debug('enrich_windows: windows=%s', list(p.windows.keys()))

        # Increment to next position
        position += 1


def get_enriched_data(window, points, position=0):
    log.debug('window_points=%s', points[position:(position + window.size)])
        
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

