"""
"""

import logging
import unittest
from math import asin, degrees
from ski.data.commons import ExtendedGPSPoint

from ski.io.cleanup import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestCleanup(unittest.TestCase):

    '''
    calc_point_deltas(prev_point, point)
    '''
    def test_calc_point_deltas(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=5, x=4, y=5)
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
            ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=5, x=4, y=5)
        ]

        calculate_point_deltas(*points)

        self.assertEqual(points[1].dst, 0.0)
        self.assertEqual(points[1].hdg, 0.0)
        self.assertEqual(points[1].alt_d, 0.0)
        self.assertEqual(points[1].spd_d, 0.0)
        self.assertEqual(points[1].hdg_d, 0.0)


    '''
    cleanup_points(points, [output], [outlyers])
    '''
    def test_cleanup_points_empty_list(self):
        output = []
        res = cleanup_points([], output)

        self.assertEqual([], output)


    def test_cleanup_points_with_interpolation(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0),
            ExtendedGPSPoint(ts=3, lat=1.0, lon=1.0, alt=5, spd=0)
        ]

        output = []
        outlyers = []
        res = cleanup_points(points, output, outlyers)

        self.assertEqual(3, len(output))
        self.assertEqual(0, len(outlyers))


    def test_cleanup_points_with_outlyers(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0),
            ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=0),
            ExtendedGPSPoint(ts=3, lat=1.0, lon=1.0, alt=5, spd=50)
        ]

        output = []
        outlyers = []
        res = cleanup_points(points, output, outlyers)

        self.assertEqual(2, len(output))
        self.assertEqual(1, len(outlyers))



if __name__ == '__main__':
    unittest.main()
