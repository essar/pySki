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

    def __init__(self, points, window_type, size, position=0):

        # Do not allow a midpoint to be created of even length
        if window_type == PointWindow.MIDPOINT and size % 2 == 0:
            raise ValueError('Midpoint window must be of odd length')

        self.points = points
        self.window_type = window_type
        self.size = size
        self.position = position
        self.window_full = False


    def window(self):
        if self.window_type == PointWindow.FORWARD:
            # Forward load from the position
            window_start = max(0, self.position)
            window_end = min(len(self.points), (self.position + self.size))
            log.debug('Forward window from %d: %d->%d', self.position, window_start, window_end)

        elif self.window_type == PointWindow.MIDPOINT:
            # Load equally either side of position
            mp = self.size / 2

            window_start = max(0, self.position - (min(len(self.points), (self.position + ceil(mp))) - self.position) + 1, self.position - floor(mp))
            window_end = min(len(self.points), self.position + (self.position - max(0, self.position - floor(mp))) + 1, (self.position + ceil(mp)))
            log.debug('Midpoint window from %d: %d->%d', self.position, window_start, window_end)

        elif self.window_type == PointWindow.BACKWARD:
            # Backward load from the position
            window_start = max(0, self.position - self.size + 1)
            window_end = min(len(self.points), self.position + 1)
            log.debug('Backward window from %d: %d->%d', self.position, window_start, window_end)

        window = self.points[window_start:window_end]
        self.window_full = (len(window) == self.size)
        log.debug('Window is %s', 'full' if self.window_full else 'not full')
        return window


    def alt_delta(self):
        return self.window()[-1].alt - self.window()[0].alt


    def alt_cuml_gain(self):
        return sum([p.alt_d for p in self.window() if p.alt_d > 0])


    def alt_cuml_loss(self):
        return sum([p.alt_d for p in self.window() if p.alt_d < 0])


    def alt_max(self):
        return max([p.alt for p in self.window()])


    def alt_min(self):
        return min([p.alt for p in self.window()])


    def distance(self):
        return sum([p.dst for p in self.window()])


    def speed_ave(self):
        return avg([p.spd for p in self.window()])


    def speed_delta(self):
        return self.window()[-1].spd - self.window()[0].spd


    def speed_max(self):
        return max([p.spd for p in self.window()])


    def speed_min(self):
        return min([p.spd for p in self.window()])



def avg(values):
    return float(sum(values)) / max(1, len(values))




def __enriched_alt_vals(window):
    return {
        'alt_delta' : window.alt_delta(),
        'alt_gain'  : window.alt_cuml_gain(),
        'alt_loss'  : window.alt_cuml_loss(),
        'alt_max'   : window.alt_max(),
        'alt_min'   : window.alt_min()
    }


def __enriched_speed_vals(window):
    return {
        'speed_min'   : window.speed_min(),
        'speed_max'   : window.speed_max(),
        'speed_ave'   : window.speed_ave(),
        'speed_delta' : window.speed_delta()
    }


def get_enriched_data(window):
    # Build a dict of enriched values
    data = {
        'distance' : window.distance()
    }
    data.update(__enriched_alt_vals(window))
    data.update(__enriched_speed_vals(window))
    return data


def enrich_points(points, windows, head=[], min_tail=1, overflow=[]):
    # Create position counter, start above head values
    position = len(head)

    # Process as many points as we can
    while len(points[position:]) >= min_tail:
        p = points[position]

        for k in windows:
            # Get window based on key and set to current position
            w = windows[k]
            w.position = position

            if w.points[w.position] != p:
                log.warning('Window point is not equal to the main point')

            # Build a dict of enriched values
            vals = get_enriched_data(w)

            # Add the enrichment data to the point, using the input dict key
            p.windows[k] = EnrichedWindow(**vals)

        log.info('Added windows: %s', list(p.windows.keys()))

        # Increment to next position
        position += 1
        
    # Return any unprocessed elements
    overflow.extend(points[position:])

