"""
"""
import logging

from math import ceil, floor
from ski.config import config
from ski.data.commons import EnrichedPoint

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



