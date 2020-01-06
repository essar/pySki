"""
"""
import logging

from math import floor
from ski.data.commons import EnrichedWindow, debug_point_event

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class WindowKey:

    def __init__(self, window_type, size):
        self.window_type = window_type
        self.size = size

    def __eq__(self, other):
        return type(other) == WindowKey and (self.window_type == other.window_type) and (self.size == other.size)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return '{:s},{:d}'.format(['', 'F', 'M', 'B'][self.window_type], self.size)

    def __str__(self):
        return self.__repr__()

    def key(self):
        return self.window_type, self.size


class PointWindow:
    """
    Represents a window of points for calculating enriched values.
    Head: A list of points "before" the target point. Not processed yet
    Tail: A list of points "after" the target point. Already processed.
    """

    FORWARD = 1
    MIDPOINT = 2
    BACKWARD = 3

    def __init__(self, head_length=50, tail_length=50):
        self.head = []
        self.head_length = head_length
        self.tail = []
        self.tail_length = tail_length
        self.target_point = None
        self.drain = False

    def __get_head_points(self, size):
        return self.head[0:(min(size, len(self.head), self.head_length))]

    def __get_target_point(self):
        return self.target_point

    def __get_tail_points(self, size):
        return self.tail[-min(size, len(self.tail), self.tail_length):]

    def extract(self, window_type, size):
        """
        Extract a set of points from the window, based on a direction and size
        @param window_type: window direction:
            FORWARD - points ahead of the current point
            BACKWARD - points behind the current point
            MIDPOINT - poinds equally either side of the current point
        @param size: size of the window
        @return: a list of points, including the current point
        """

        # Do not allow a midpoint to be created of even length
        if window_type == PointWindow.MIDPOINT and size % 2 == 0:
            raise ValueError('Midpoint window must be of odd length')

        # Forward looking window
        if window_type == PointWindow.FORWARD:
            # Set of points from target point into the head
            points = [self.__get_target_point()] + self.__get_head_points(size - 1)
            return points

        elif window_type == PointWindow.MIDPOINT:
            # Load equally either side of target point
            mp = floor((size - 1) / 2)
            points = self.__get_tail_points(mp) + [self.__get_target_point()] + self.__get_head_points(mp)
            return points

        elif window_type == PointWindow.BACKWARD:
            # Set of points into the tail plus the target point
            points = self.__get_tail_points(size - 1) + [self.__get_target_point()]
            return points

    def load_points(self, points):
        """
        Load points into the window (head).
        @param points: the points to add
        """
        self.head += points
        log.debug('head: %s', self.head)

    def process(self):
        """
        Process a point, moving it from the top of the head to the bottom of the tail.
        @return: True if the buffers remain full or the window is draining, false otherwise
        """
        if self.target_point is not None:
            # Add target point to end of tail
            self.tail.append(self.target_point)

        # Stop if head is empty and we're draining
        if self.drain and len(self.head) == 0:
            return False

        # Extract point from top of head
        self.target_point = self.head.pop(0)

        return self.drain or (len(self.head) + 1) >= self.head_length

    def reset_target(self):
        """

        """
        if not self.drain:
            self.head.insert(0, self.target_point)
        self.target_point = None

    def trim(self):
        """
        Reduce the tail to the target length.
        """
        self.tail = self.tail[0:self.tail_length]


def enrich_points(points, window, default_keys):
    """
    Enriches a list of points, using the specified window
    @param points: a list of points to enrich
    @param window: a PointWindow that persists between executions of this call
    @param default_keys: a list of default window keys to set in each point
    """

    # Load the points into the window
    window.load_points(points)

    # Initialize output
    output = []

    # Iterate through the window
    while window.process():
        # Get current point from the window
        point = window.target_point

        for k in default_keys:
            # Extract window points using window key
            window_points = window.extract(*k.key())
            # Calculate the enriched values for this set of points
            enriched_values = get_enriched_data(window_points)
            debug_point_event(log, window.target_point, 'Enriched data (%s): %s', k, enriched_values)

            # Save enriched values to the point
            window.target_point.windows[k] = EnrichedWindow(**enriched_values)

        # Add enriched point to output
        output.append(point)

    # Push the target point back into the head
    window.reset_target()

    log.info('Enriched %d points; %d remain in head, %d in tail', len(output), len(window.head), len(window.tail))

    # Clean up window
    window.trim()

    # Return enriched points
    return output


def __avg(values):
    return float(sum(values)) / max(1, len(values))


def get_enriched_data(points):
    # Build a dict of enriched values
    data = {
        'distance': distance(points),
        'alt_delta': alt_delta(points),
        'alt_gain': alt_cuml_gain(points),
        'alt_loss': alt_cuml_loss(points),
        'alt_max': alt_max(points),
        'alt_min': alt_min(points),
        'speed_min': speed_min(points),
        'speed_max': speed_max(points),
        'speed_ave': speed_ave(points),
        'speed_delta': speed_delta(points)
    }
    return data


def alt_delta(points):
    return points[-1].alt - points[0].alt


def alt_cuml_gain(points):
    return sum([p.alt_d for p in points if p.alt_d > 0])


def alt_cuml_loss(points):
    return sum([p.alt_d for p in points if p.alt_d < 0])


def alt_max(points):
    return max([p.alt for p in points])


def alt_min(points):
    return min([p.alt for p in points])


def distance(points):
    return sum([p.dst for p in points])


def speed_ave(points):
    return __avg([p.spd for p in points])


def speed_delta(points):
    return points[-1].spd - points[0].spd


def speed_max(points):
    return max([p.spd for p in points])


def speed_min(points):
    return min([p.spd for p in points])
