"""
"""

import unittest
from ski.data.commons import ExtendedGPSPoint
from ski.loader.window import PointWindow, WindowKey

from ski.loader.enrich import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestEnrich(unittest.TestCase):

    def test_alt_delta(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(alt=10),
            ExtendedGPSPoint(alt=20),
            ExtendedGPSPoint(alt=-30),
            ExtendedGPSPoint(alt=40),
            ExtendedGPSPoint(alt=50)
        ]

        res = alt_delta(points)

        self.assertEqual(40, res)

    def test_alt_cuml_gain(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(alt_d=10),
            ExtendedGPSPoint(alt_d=20),
            ExtendedGPSPoint(alt_d=-30),
            ExtendedGPSPoint(alt_d=40),
            ExtendedGPSPoint(alt_d=50)
        ]

        res = alt_cuml_gain(points)

        self.assertEqual(120, res, '')

    def test_alt_cuml_loss(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(alt_d=10),
            ExtendedGPSPoint(alt_d=20),
            ExtendedGPSPoint(alt_d=-30),
            ExtendedGPSPoint(alt_d=40),
            ExtendedGPSPoint(alt_d=50)
        ]

        res = alt_cuml_loss(points)

        self.assertEqual(-30, res)

    def test_distance(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(dst=1),
            ExtendedGPSPoint(dst=2),
            ExtendedGPSPoint(dst=3),
            ExtendedGPSPoint(dst=4),
            ExtendedGPSPoint(dst=5)
        ]

        res = distance(points)

        self.assertEqual(15, res)

    def test_speed_ave(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(spd=1),
            ExtendedGPSPoint(spd=2),
            ExtendedGPSPoint(spd=3),
            ExtendedGPSPoint(spd=4),
            ExtendedGPSPoint(spd=5)
        ]

        res = speed_ave(points)

        self.assertEqual(3.0, res)

    def test_speed_max(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(spd=1),
            ExtendedGPSPoint(spd=2),
            ExtendedGPSPoint(spd=3),
            ExtendedGPSPoint(spd=4),
            ExtendedGPSPoint(spd=5)
        ]

        res = speed_max(points)

        self.assertEqual(5.0, res)

    def test_speed_min(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(spd=1),
            ExtendedGPSPoint(spd=2),
            ExtendedGPSPoint(spd=3),
            ExtendedGPSPoint(spd=4),
            ExtendedGPSPoint(spd=5)
        ]

        res = speed_min(points)

        self.assertEqual(1.0, res)

    def test_speed_delta(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(spd=1),
            ExtendedGPSPoint(spd=2),
            ExtendedGPSPoint(spd=3),
            ExtendedGPSPoint(spd=4),
            ExtendedGPSPoint(spd=5)
        ]

        res = speed_delta(points)

        self.assertEqual(4.0, res)

    """
    get_enriched_data
    """
    def test_get_enriched_data(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(dst=1, alt=10, spd=1),
            ExtendedGPSPoint(dst=1, alt=20, spd=2),
            ExtendedGPSPoint(dst=1, alt=30, spd=3),
            ExtendedGPSPoint(dst=1, alt=40, spd=4),
            ExtendedGPSPoint(dst=1, alt=50, spd=5)
        ]

        res = get_enriched_data(points)

        self.assertEqual(5, res['distance'])

        self.assertEqual(40, res['alt_delta'])
        self.assertEqual(0,  res['alt_gain'])
        self.assertEqual(0,  res['alt_loss'])
        self.assertEqual(50, res['alt_max'])
        self.assertEqual(10, res['alt_min'])

        self.assertEqual(3, res['speed_ave'])
        self.assertEqual(4, res['speed_delta'])
        self.assertEqual(5, res['speed_max'])
        self.assertEqual(1, res['speed_min'])

    """
    enrich_points
    """
    def test_enrich_points(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(dst=1, alt=10, spd=1),
            ExtendedGPSPoint(dst=1, alt=20, spd=2),
            ExtendedGPSPoint(dst=1, alt=40, spd=3),
            ExtendedGPSPoint(dst=1, alt=70, spd=4),
            ExtendedGPSPoint(dst=1, alt=110, spd=5)
        ]
        window = PointWindow(head=points, min_head_length=2)

        # Window key looking forward (in the body)
        wk = WindowKey(WindowKey.FORWARD, 3)

        res = enrich_points(window, [wk])

        self.assertEqual(3, len(res))
        self.assertIsNotNone(points[0].windows[wk])

    def test_enrich_points_drain(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(dst=1, alt=10, spd=1),
            ExtendedGPSPoint(dst=1, alt=20, spd=2),
            ExtendedGPSPoint(dst=1, alt=40, spd=3),
            ExtendedGPSPoint(dst=1, alt=70, spd=4),
            ExtendedGPSPoint(dst=1, alt=110, spd=5)
        ]
        # Call enrich_batch is no min_head_length to drain it
        window = PointWindow(head=points)

        wk = WindowKey(WindowKey.FORWARD, 3)

        # Call enrich_batch is no min_head_length to drain it
        res = enrich_points(window, [wk])

        self.assertEqual(5, len(res))
        self.assertIsNotNone(points[0].windows[wk])


if __name__ == '__main__':
    unittest.main()
