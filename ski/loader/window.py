

import logging

from math import floor

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}


class BatchWindow:

    def __init__(self, batch_size=30, overlap=0):
        self.batch_size = batch_size
        self.overlap = overlap
        self.body = []
        self.tail = []
        self.batch_count = 0

        if self.overlap > self.batch_size:
            raise ValueError('Overlap size cannot exceed batch size')

    def __process_batch(self, drain, process_f, **kwargs):
        self.batch_count += 1

        body_out = self.body[:self.batch_size]

        log.debug('%s[batch=%03d] Processing %d points', self, self.batch_count, len(body_out))

        if process_f is not None:
            # Invoke process function
            process_f(self.batch_count, body_out, self.tail, drain, **kwargs)

        # Append output elements of body to tail
        self.tail += body_out

        # Use overlap of 0 if we're draining
        ol = 0 if drain else self.overlap

        # Trim to length
        self.tail = self.tail[-(self.overlap * 2):-ol]

        # Leave any unprocessed elements in the body, plus the overlap
        self.body = self.body[len(body_out)-ol:]

        log.debug('%s[batch=%03d] %d points processed', self, self.batch_count, len(body_out))

    def __str__(self):
        return '[BatchWindow][body={:d}][tail={:d}]'.format(len(self.body), len(self.tail))

    def load_points(self, points, drain=False, process_f=None, **kwargs):
        """ Loads points into the window. If the window is full, call `output_f(points, tail)` with the window data."""

        if points is None:
            # End of input, process the batch
            self.__process_batch(drain, process_f, **kwargs)

        else:
            # Append points in to the body
            self.body += points
            log.debug('%s Loaded %d points', self, len(points))

            while len(self.body) >= self.batch_size:
                self.__process_batch(drain, process_f, **kwargs)


class PointWindow:
    """
    Represents a window of points for calculating enriched values.
    Head: A list of points "before" the target point. Not processed yet
    Tail: A list of points "after" the target point. Already processed.
    """

    def __init__(self, head=None, tail=None, min_head_length=0):
        self.head = []
        self.tail = []

        self.min_head_length = min_head_length
        self.target_point = None
        self.drain = False

        if head is not None:
            self.head += head

        if tail is not None:
            self.tail += tail

    def __str__(self):
        return '[PointWindow][head={:d}][tail={:d}]'.format(len(self.head), len(self.tail))

    def extract(self, window_type, size):
        """
        Extract a set of points from the window, based on a direction and size
        @param window_type: window direction:
            FORWARD - points ahead of the current point
            BACKWARD - points behind the current point
            MIDPOINT - points equally either side of the current point
        @param size: size of the window
        @return: a list of points, including the current point
        """

        # Do not allow a midpoint to be created of even length
        if window_type == WindowKey.MIDPOINT and size % 2 == 0:
            raise ValueError('Midpoint window must be of odd length')

        # Forward looking window
        if window_type == WindowKey.FORWARD:
            # Set of points from target point into the head
            points = [self.target_point] + self.head[:size - 1]
            return points

        elif window_type == WindowKey.MIDPOINT:
            # Load equally either side of target point
            mp = floor((size - 1) / 2.0)
            points = self.tail[-mp:] + [self.target_point] + self.head[:mp]
            return points

        elif window_type == WindowKey.BACKWARD:
            # Set of points into the tail plus the target point
            points = self.tail[-(size - 1):] + [self.target_point]
            return points

    def load_points(self, points):
        """
        Load points into the window (head).
        @param points: the points to add
        """
        self.head += points
        log.debug('%s Loaded %s points', self, len(points))

    def process(self):
        """
        Process a point, moving it from the top of the head to the bottom of the tail.
        @return: True if the buffers remain full or the window is draining, false otherwise
        """

        if self.target_point is not None:
            # Add target point to end of tail
            self.tail.append(self.target_point)

        # Reset target point, prevents it being duplicated
        self.target_point = None

        # Stop if head is empty and we're draining
        if self.drain and len(self.head) == 0:
            log.debug('%s Window drained', self)
            return False

        if self.drain or len(self.head) > max(0, self.min_head_length):
            # Extract point from top of head
            self.target_point = self.head.pop(0)
            log.debug('%s Process window: OK', self)
            return True

        log.debug('%s Process window: closed (min_head=%d < %d)', self, self.min_head_length, len(self.head))
        return False


class WindowKey:

    FORWARD = 1
    MIDPOINT = 2
    BACKWARD = 3

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
