"""
"""

import logging
import unittest

from ski.data.commons import ExtendedGPSPoint
from ski.data.pointutils import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestPointUtils(unittest.TestCase):


    '''
    get_distance(prev_point, point)
    '''
    def test_get_distance(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, x=3, y=3),
            ExtendedGPSPoint(ts=2, x=6, y=7)
        ]

        res = get_distance(*points)

        self.assertEqual(5.0, res)


    def test_get_distance_no_prev(self):
        # Prepare data
        points = [
            None,
            ExtendedGPSPoint(ts=2, x=6, y=7)
        ]

        res = get_distance(*points)

        self.assertEqual(0, res)


    '''
    get_heading(prev_point, point)
    '''
    def test_get_heading(self):
        # Prepare data
        points = [
            # Move East
            ExtendedGPSPoint(ts=1, x=0, y=0),
            ExtendedGPSPoint(ts=2, x=5, y=0)
        ]

        res = get_heading(*points)

        self.assertEqual(90.0, res)


    def test_get_distance_no_prev(self):
        # Prepare data
        points = [
            None,
            ExtendedGPSPoint(ts=2, x=6, y=7)
        ]

        res = get_distance(*points)

        self.assertEqual(0, res)


    '''
    get_ts_delta(prev_point, point)
    '''
    def test_get_ts_delta(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1),
            ExtendedGPSPoint(ts=2)
        ]

        res = get_ts_delta(*points)

        self.assertEqual(1, res)


    def test_get_ts_delta_negative(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=2),
            ExtendedGPSPoint(ts=1)
        ]

        res = get_ts_delta(*points)

        self.assertEqual(-1, res)


if __name__ == '__main__':
    unittest.main()
