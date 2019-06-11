"""
"""

import logging
import unittest
from datetime import datetime
from math import asin, degrees
from pytz import timezone
from ski.data.commons import EnrichedPoint, LinkedPoint
from ski.io.db import TestDataStore

from ski.io.cleanup import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestCleanup(unittest.TestCase):

    '''
    calc_deltas(prev_point, point)
    '''

    def test_calc_deltas(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            EnrichedPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=5, x=4, y=5)
        ]

        calculate_point_deltas(*points)

        self.assertEqual(points[1].dst, 5.0)
        self.assertAlmostEqual(points[1].hdg, degrees(asin(3 / 5)), 8)
        self.assertEqual(points[1].alt_d, 5)
        self.assertEqual(points[1].spd_d, 5.0)
        self.assertAlmostEqual(points[1].hdg_d, degrees(asin(3 / 5)), 8)


    def test_calc_deltas_no_prev(self):
        # Prepare data
        points = [
            None,
            EnrichedPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=5, x=4, y=5)
        ]

        calculate_point_deltas(*points)

        self.assertEqual(points[1].dst, 0.0)
        self.assertEqual(points[1].hdg, 0.0)
        self.assertEqual(points[1].alt_d, 0.0)
        self.assertEqual(points[1].spd_d, 0.0)
        self.assertEqual(points[1].hdg_d, 0.0)



    '''
    cleanup_point(point, output, outlyers)
    '''

    def test_cleanup_point_with_no_output(self):
        # Prepare data
        point = EnrichedPoint(ts=1, lat=5.0, lon=5.0, alt=2, spd=2)
        output = []
        outlyers=[]

        cleanup_point(point, output, outlyers)

        self.assertEqual(1, len(output))    # Point is moved to output list
        self.assertEqual(0, len(outlyers))  # No outlyers removed


    def test_cleanup_point_with_delta_2(self):
        # Prepare data
        point = EnrichedPoint(ts=3, lat=45.304158, lon=6.586400, alt=2, spd=10.0)
        output = [
            EnrichedPoint(ts=1, lat=45.304125, lon=6.586398, alt=4, spd=4.0, x=310781, y=5019570)
        ]
        outlyers=[]

        cleanup_point(point, output, outlyers)

        self.assertEqual(3, len(output))    # Output now contains 3 points (including an interpolated point)
        self.assertEqual(0, len(outlyers))  # No outlyers removed


    def test_cleanup_point_with_outlyer(self):
        # Prepare data
        point = EnrichedPoint(ts=2, lat=45.304158, lon=6.586400, alt=2, spd=123.0)
        output = [
            EnrichedPoint(ts=1, lat=45.304125, lon=6.586398, alt=3, spd=4, x=310781, y=5019570)
        ]
        outlyers=[]

        cleanup_point(point, output, outlyers)

        self.assertEqual(1, len(output))    # Original point remains in output
        self.assertEqual(1, len(outlyers))  # New point returned in outlyer list



    '''
    cleanup_points(points, output, outlyers)
    '''

    def test_cleanup_points_with_outlyer(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=45.304082, lon=6.586386, alt=3, spd=17.0),
            EnrichedPoint(ts=2, lat=45.304125, lon=6.586398, alt=3, spd=117.0),
            EnrichedPoint(ts=3, lat=45.304158, lon=6.586400, alt=3, spd=17.0)
        ]
        output = []
        outlyers=[]

        cleanup_points(points, output, outlyers)

        self.assertEqual(3, len(output))    # 3 points in output as outlyer should be interpolated
        self.assertEqual(1, len(outlyers))  # 1 point moved to outlyer list
            


    '''
    interpolate_point(linked_point, interpolate_f, [ts_delta])
    '''

    def test_interpolate_point_missing_delta_2(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1),
            EnrichedPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        ]
        lp = LinkedPoint(*points)

        res = interpolate_point(lp, linear_interpolate)

        self.assertEqual(2, res.point.ts)
        self.assertEqual(1.5, res.point.lat)
        self.assertEqual(1.5, res.point.lon)
        self.assertEqual(2, res.point.alt)
        self.assertEqual(3, res.point.spd)
        self.assertEqual(2, res.point.x)
        self.assertEqual(2, res.point.y)


    def test_interpolate_point_missing_none(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1),
            EnrichedPoint(ts=2, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        ]
        lp = LinkedPoint(*points)

        res = interpolate_point(lp, linear_interpolate)

        self.assertIsNone(res)


    def test_linear_interpolate_missing_delta_2(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1),
            EnrichedPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        ]

        res = linear_interpolate(points[0], points[1], 2)

        self.assertEqual(2, res.ts)
        self.assertEqual(1.5, res.lat)
        self.assertEqual(1.5, res.lon)
        self.assertEqual(2, res.alt)
        self.assertEqual(3, res.spd)
        self.assertEqual(2, res.x)
        self.assertEqual(2, res.y)


    def test_linear_interpolate_missing_delta_4(self):
        # Prepare data
        points = [
            EnrichedPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1),
            EnrichedPoint(ts=5, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)
        ]

        res = linear_interpolate(points[0], points[1], 4)

        self.assertEqual(2, res.ts)
        self.assertEqual(1.25, res.lat)
        self.assertEqual(1.25, res.lon)
        self.assertEqual(1, res.alt)
        self.assertEqual(2.5, res.spd)
        self.assertEqual(1, res.x)
        self.assertEqual(1, res.y)



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
