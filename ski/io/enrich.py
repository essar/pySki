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

        elif self.window_type == PointWindow.MIDPOINT:
            # Load equally either side of position
            mp = self.size / 2

            window_start = max(0, self.position - (min(len(self.points), (self.position + ceil(mp))) - self.position) + 1, self.position - floor(mp))
            window_end = min(len(self.points), self.position + (self.position - max(0, self.position - floor(mp))) + 1, (self.position + ceil(mp)))

        elif self.window_type == PointWindow.BACKWARD:
            # Backward load from the position
            window_start = max(0, self.position - self.size + 1)
            window_end = min(len(self.points), self.position + 1)

        window = self.points[window_start:window_end]
        self.window_full = (len(window) == self.size)
        return window

