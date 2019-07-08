"""
"""

import logging
import unittest

from ski.data.commons import ExtendedGPSPoint
from ski.io.db import TestDataStore

from ski.loader.interpolate import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestInterpolate(unittest.TestCase):


    '''
    interpolate_point
    '''
    def test_interpolate_point_None(self):

        res = interpolate_point(linear_interpolate, None, None)
        self.assertEqual([], res)


    def test_interpolate_point_prev_None(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        
        res = interpolate_point(linear_interpolate, p1)
        self.assertEqual([p1], res)

    
    def test_interpolate_point_delta_1(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p1 = ExtendedGPSPoint(ts=2, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        res = interpolate_point(linear_interpolate, p1, p0)

        self.assertEqual([p1], res)


    def test_interpolate_point_delta_2(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        res = interpolate_point(linear_interpolate, p2, p0)

        self.assertEqual(2, len(res))


    def test_interpolate_point_delta_3(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p3 = ExtendedGPSPoint(ts=4, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        res = interpolate_point(linear_interpolate, p3, p0)

        self.assertEqual(3, len(res))


    def test_interpolate_point_negative_delta(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p1 = ExtendedGPSPoint(ts=1, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        res = interpolate_point(linear_interpolate, p1, p0)

        self.assertEqual([], res);


    def test_interpolate_point_duplicate(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p1 = ExtendedGPSPoint(ts=1, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        res = interpolate_point(linear_interpolate, p1, p0)

        self.assertEqual([], res);


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
