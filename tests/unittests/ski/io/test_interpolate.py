"""
"""

import logging
import unittest

from ski.data.commons import ExtendedGPSPoint, LinkedPoint
from ski.io.db import TestDataStore

from ski.io.interpolate import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.DEBUG)


class TestInterpolate(unittest.TestCase):

    '''
    interpolate_point(linked_point, interpolate_f, [ts_delta])
    '''

    def test_interpolate_linked_point(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        lp = LinkedPoint(p1, p2)

        res = interpolate_linked_point(lp, linear_interpolate)

        self.assertIsNotNone(res)
        self.assertEqual(2, res.point.ts)


    def test_interpolate_linked_point_missing_none(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=2, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        lp = LinkedPoint(p1, p2)

        res = interpolate_linked_point(lp, linear_interpolate)

        self.assertIsNone(res)

    '''
    interpolate_points
    '''
    def test_interpolate_points_delta_3(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        output = []

        interpolate_points(p1, p2, linear_interpolate, output)

        self.assertEqual(3, len(output))


    def test_interpolate_points_delta_3(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=4, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        output = []

        interpolate_points(p1, p2, linear_interpolate, output)

        self.assertEqual(4, len(output))


    def test_interpolate_points_negative_delta(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=4, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=1, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        output = []

        interpolate_points(p1, p2, linear_interpolate, output)

        self.assertEqual(1, len(output))


    def test_interpolate_points_duplicate(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=1, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        output = []

        interpolate_points(p1, p2, linear_interpolate, output)

        self.assertEqual(1, len(output))


    '''
    linear_interpolate
    '''

    def test_linear_interpolate_missing_delta_2(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        
        # Interpolate
        res = linear_interpolate(p1, p2, 2)

        self.assertEqual(2, res.ts)
        self.assertEqual(1.5, res.lat)
        self.assertEqual(1.5, res.lon)
        self.assertEqual(2, res.alt)
        self.assertEqual(3, res.spd)
        self.assertEqual(2, res.x)
        self.assertEqual(2, res.y)


    def test_linear_interpolate_missing_delta_4(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=5, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        # Interpolate
        res = linear_interpolate(p1, p2, 4)

        self.assertEqual(2, res.ts)
        self.assertEqual(1.25, res.lat)
        self.assertEqual(1.25, res.lon)
        self.assertEqual(1, res.alt)
        self.assertEqual(2.5, res.spd)
        self.assertEqual(1, res.x)
        self.assertEqual(1, res.y)



if __name__ == '__main__':
    unittest.main()
