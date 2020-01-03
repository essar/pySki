"""
"""

import unittest
from math import asin, degrees
from ski.data.commons import ExtendedGPSPoint

from ski.loader.cleanup import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestCleanup(unittest.TestCase):

    """
    calc_deltas(prev_point, point)
    """
    def test_calc_deltas(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0, x=1, y=1),
            ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=5, x=4, y=5)
        ]

        # Calculate deltas
        calculate_deltas(*points)

        # Verify calculations
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

        # Calculate deltas
        calculate_deltas(*points)

        # Verify calculations
        self.assertEqual(points[1].dst, 0.0)
        self.assertEqual(points[1].hdg, 0.0)
        self.assertEqual(points[1].alt_d, 0.0)
        self.assertEqual(points[1].spd_d, 0.0)
        self.assertEqual(points[1].hdg_d, 0.0)

    """
    cleanup_points(points, [outlyers])
    """
    def test_cleanup_points_clean_data(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0),
            ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=3, spd=0)
        ]

        outlyers = []
        output = cleanup_points(points, outlyers)

        self.assertEqual(2, len(output))
        self.assertEqual(0, len(outlyers))

    def test_cleanup_points_empty_list(self):
        output = cleanup_points([])

        self.assertEqual([], output)

    def test_cleanup_points_with_interpolation(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0),
            ExtendedGPSPoint(ts=3, lat=1.0, lon=1.0, alt=5, spd=0)
        ]

        outlyers = []
        output = cleanup_points(points, outlyers)

        self.assertEqual(3, len(output))
        self.assertEqual(0, len(outlyers))

    def test_cleanup_points_with_outlyers(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0),
            ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=5, spd=0),
            ExtendedGPSPoint(ts=3, lat=1.0, lon=1.0, alt=5, spd=50)
        ]

        outlyers = []
        output = cleanup_points(points, outlyers)

        self.assertEqual(2, len(output))
        self.assertEqual(1, len(outlyers))

    """
    interpolate_point(inter_f, prev_point, point, output)
    """
    def test_interpolate_point_None(self):
        output = []
        interpolate_point(linear_interpolate, None, None, output)

        self.assertListEqual([], output)

    def test_interpolate_point_prev_None(self):
        # Prepare data
        p1 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)

        output = []
        res = interpolate_point(linear_interpolate, None, p1, output)

        self.assertIsNone(res)
        self.assertListEqual([], output)

    def test_interpolate_point_delta_1(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p1 = ExtendedGPSPoint(ts=2, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        output = []
        res = interpolate_point(linear_interpolate, p0, p1, output)

        self.assertEqual(p0, res)
        self.assertListEqual([], output)

    def test_interpolate_point_delta_2(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p2 = ExtendedGPSPoint(ts=3, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        output = []
        res = interpolate_point(linear_interpolate, p0, p2, output)

        self.assertEqual(output[0], res)
        self.assertEqual(1, len(output))

    def test_interpolate_point_delta_3(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p3 = ExtendedGPSPoint(ts=4, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        output = []
        res = interpolate_point(linear_interpolate, p0, p3, output)

        self.assertEqual(output[1], res)
        self.assertEqual(2, len(output))

    def test_interpolate_point_negative_delta(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p1 = ExtendedGPSPoint(ts=1, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        output = []
        res = interpolate_point(linear_interpolate, p0, p1, output)

        self.assertEqual(p0, res)
        self.assertListEqual([], output)

    def test_interpolate_point_duplicate(self):
        # Prepare data
        p0 = ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=1, spd=2, x=1, y=1)
        p1 = ExtendedGPSPoint(ts=1, lat=2.0, lon=2.0, alt=3, spd=4, x=3, y=3)

        output = []
        res = interpolate_point(linear_interpolate, p0, p1, output)

        self.assertEqual(p0, res)
        self.assertListEqual([], output)


if __name__ == '__main__':
    unittest.main()
