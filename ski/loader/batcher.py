

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class BatchWindow:

    def __init__(self, body_size=450, overlap=30):
        self.body_size = body_size
        self.overlap = overlap
        self.body = []

        if self.overlap > self.body_size:
            raise ValueError('Overlap size cannot exceed body size')

    def load_points(self, points, output_f=None):
        """ Loads points into the window. If the window is full, call `output_f(points)` with the window data."""

        # Append points in to the body
        self.body += points

        while len(self.body) >= self.body_size:
            # Call provided output function with body data
            if output_f is not None:
                # Assemble points to be sent to output function
                body_out = self.body[:self.body_size]
                # Invoke output function
                output_f(body_out)
                log.debug('Called output function with %d points', len(body_out))

            # Reset the body containing the specified overlap and any remaining points
            body_start = self.body_size - self.overlap
            self.body = self.body[body_start:]

            log.debug('Body size now %d', len(self.body))
