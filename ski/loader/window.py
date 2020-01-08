

import logging

from math import floor

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class BatchWindow:

    def __init__(self, body_size=450, overlap=30):
        self.body_size = body_size
        self.overlap = overlap
        self.body = []
        self.tail = []

        if self.overlap > self.body_size:
            raise ValueError('Overlap size cannot exceed body size')

    def __shift_to_tail(self, body_out):
        """ Moves output points from body to tail."""

        # Append output elements of body to tail
        self.tail += body_out

        # Trim to length
        self.tail = self.tail[-self.overlap:]

        # Leave any unprocessed elements in the body
        self.body = self.body[len(body_out):]

        log.debug('body_length=%d, tail_length=%d', len(self.body), len(self.tail))

    def load_points(self, points, output_f=None):
        """ Loads points into the window. If the window is full, call `output_f(points, tail)` with the window data."""

        # Append points in to the body
        self.body += points

        while len(self.body) >= self.body_size:
            # Assemble points to be sent to output function
            body_out = self.body[:self.body_size]

            if output_f is not None:
                # Invoke output function
                output_f(body_out, self.tail)
                log.debug('Called output function with %d points', len(body_out))

            # Move output points to the tail
            self.__shift_to_tail(body_out)


class PointWindow:
    """
    Represents a window of points for calculating enriched values.
    Head: A list of points "before" the target point. Not processed yet
    Tail: A list of points "after" the target point. Already processed.
    """

    def __init__(self, head=None, tail=None, head_length=50, tail_length=50):
        self.head = []
        self.tail = []

        self.head_length = head_length
        self.tail_length = tail_length
        self.target_point = None
        self.drain = False

        if head is not None:
            self.head += head

        if tail is not None:
            self.tail += tail

    def __get_head_points(self, size):
        return self.head[0:(min(size, len(self.head), self.head_length))]

    def __get_target_point(self):
        return self.target_point

    def __get_tail_points(self, size):
        return self.tail[-min(size, len(self.tail), self.tail_length):]

    def current_point(self):
        return self.target_point

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
        if window_type == WindowKey.MIDPOINT and size % 2 == 0:
            raise ValueError('Midpoint window must be of odd length')

        # Forward looking window
        if window_type == WindowKey.FORWARD:
            # Set of points from target point into the head
            points = [self.__get_target_point()] + self.head[:size - 1]
            return points

        elif window_type == WindowKey.MIDPOINT:
            # Load equally either side of target point
            mp = floor((size - 1) / 2)
            points = self.__get_tail_points(mp) + [self.__get_target_point()] + self.__get_head_points(mp)
            return points

        elif window_type == WindowKey.BACKWARD:
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
        self.target_point = self.head.pop(0) if len(self.head) > 0 else None

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
