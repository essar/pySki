"""
"""

import logging
import unittest
from datetime import datetime
from math import asin, degrees
from pytz import timezone
from ski.data.commons import EnrichedPoint, LinkedPoint
from ski.io.db import TestDataStore

from ski.io.outlyer import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestOutlyer(unittest.TestCase):

    '''
    is_outlyer(prev_point, point)
    '''

    def test_is_outlyer(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            EnrichedPoint(ts=2, lat=1.0, lon=1.0, alt=0, spd=5.0, x=2, y=2)
        ]

        res = is_outlyer(*points)

        self.assertFalse(res)


    def test_is_outlyer_high_speed(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            EnrichedPoint(ts=2, lat=1.0, lon=1.0, alt=0, spd=1000.0, x=200, y=200)
        ]

        res = is_outlyer(*points)

        self.assertTrue(res)


    def test_is_outlyer_high_speed_factor(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            EnrichedPoint(ts=2, lat=1.0, lon=1.0, alt=0, spd=5.0, x=5, y=5)
        ]

        res = is_outlyer(*points)

        self.assertTrue(res)


    def test_is_outlyer_low_speed_factor(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            EnrichedPoint(ts=2, lat=1.0, lon=1.0, alt=0, spd=5.0, x=1.1, y=1.1)
        ]

        res = is_outlyer(*points)

        self.assertTrue(res)



if __name__ == '__main__':
    unittest.main()
