"""
"""

import logging
import unittest
from ski.data.commons import EnrichedPoint

from ski.io.enrich import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.INFO)


class TestEnrich(unittest.TestCase):

    '''
    PointWindow.window()
    '''

    def test_PointWindow_empty(self):
        # Prepare data
        points = []

        w = PointWindow(points, PointWindow.FORWARD, 5)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 0)
        self.assertFalse(w.window_full)


    def test_PointWindow_full_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 5, 5)

        res = w.window()
        log.info(res)

        self.assertEqual([1, 2, 3, 4, 5], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_full_backward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 6, 6)

        res = w.window()
        log.info(res)

        self.assertEqual([1, 2, 3, 4, 5, 6], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_full_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 5, 5)

        res = w.window()
        log.info(res)
        
        self.assertEqual([5, 6, 7, 8, 9], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_full_forward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 6, 4)

        res = w.window()
        log.info(res)
        
        self.assertEqual([4, 5, 6, 7, 8, 9], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_full_midpoint(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 5)

        res = w.window()
        log.info(res)

        self.assertEqual([3, 4, 5, 6, 7], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_full_midpoint_even(self):
        # Prepare data
        points = list(range(10))

        self.assertRaises(ValueError, PointWindow, points, PointWindow.MIDPOINT, 6)


    def test_PointWindow_short_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 5, 3)

        res = w.window()
        log.info(res)

        self.assertEqual([0, 1, 2, 3], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_short_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 5, 6)

        res = w.window()
        log.info(res)

        self.assertEqual([6, 7, 8, 9], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_short_midpoint_bottom(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 1)

        res = w.window()
        log.info(res)

        self.assertEqual([0, 1, 2], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_short_midpoint_top(self):
        # Prepare data
        points = list(range(10))
        size = 5

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 8)

        res = w.window()
        log.info(res)

        self.assertEqual([7, 8, 9], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_alt_delta(self):
        # Prepare data
        points = [
            EnrichedPoint(alt=10),
            EnrichedPoint(alt=20),
            EnrichedPoint(alt=30),
            EnrichedPoint(alt=40),
            EnrichedPoint(alt=50)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.alt_delta()

        log.info('alt=%f', res)
        self.assertEqual(20, res)


    def test_PointWindow_alt_cuml_gain(self):
        # Prepare data
        points = [
            EnrichedPoint(alt_d=10),
            EnrichedPoint(alt_d=20),
            EnrichedPoint(alt_d=-30),
            EnrichedPoint(alt_d=40),
            EnrichedPoint(alt_d=50)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.alt_cuml_gain()

        log.info('alt_d=%f', res)
        self.assertEqual(60, res)


    def test_PointWindow_alt_cuml_loss(self):
        # Prepare data
        points = [
            EnrichedPoint(alt_d=10),
            EnrichedPoint(alt_d=20),
            EnrichedPoint(alt_d=-30),
            EnrichedPoint(alt_d=40),
            EnrichedPoint(alt_d=50)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.alt_cuml_loss()

        log.info('alt_d=%f', res)
        self.assertEqual(-30, res)


    def test_PointWindow_distance(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1),
            EnrichedPoint(dst=2),
            EnrichedPoint(dst=3),
            EnrichedPoint(dst=4),
            EnrichedPoint(dst=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.distance()

        log.info('dst=%f', res)
        self.assertEqual(9, res)


    def test_PointWindow_speed_ave(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3)
        res = w.speed_ave()

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


    def test_PointWindow_speed_max(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.speed_max()

        log.info('speed=%f', res)
        self.assertEqual(4.0, res)


    def test_PointWindow_speed_min(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.speed_min()

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


    def test_PointWindow_speed_delta(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = w.speed_delta()

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


    def test_get_enriched_data(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=30, spd=3),
            EnrichedPoint(dst=1, alt=40, spd=4),
            EnrichedPoint(dst=1, alt=50, spd=5)
        ]
        window = PointWindow(points, PointWindow.FORWARD, 5)

        res = get_enriched_data(window)

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


    def test_enrich_points(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]
        windows = { 'fwd3' : PointWindow(points, PointWindow.FORWARD, 3) }

        enrich_points(points, windows)

        self.assertIsNotNone(points[0].windows['fwd3'])
        self.assertEqual(3, points[0].windows['fwd3'].distance)

        # Verify altitude delta values
        self.assertEqual(30, points[0].windows['fwd3'].alt_delta)
        self.assertEqual(50, points[1].windows['fwd3'].alt_delta)
        self.assertEqual(70, points[2].windows['fwd3'].alt_delta)
        self.assertEqual(40, points[3].windows['fwd3'].alt_delta)
        self.assertEqual(0,  points[4].windows['fwd3'].alt_delta)

        # Verify maximum speed values
        self.assertEqual(3, points[0].windows['fwd3'].speed_max)
        self.assertEqual(4, points[1].windows['fwd3'].speed_max)
        self.assertEqual(5, points[2].windows['fwd3'].speed_max)
        self.assertEqual(5, points[3].windows['fwd3'].speed_max)
        self.assertEqual(5, points[4].windows['fwd3'].speed_max)


    def test_enrich_points_with_min_tail(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]
        windows = { 'fwd3' : PointWindow(points, PointWindow.FORWARD, 3) }

        overflow = []
        enrich_points(points, windows, min_tail=3, overflow=overflow)

        self.assertEqual(2, len(overflow))


    def test_enrich_points_with_tail(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]
        

        head = []
        overflow = []

        # First iteration
        windows = { 'fwd3' : PointWindow(points, PointWindow.FORWARD, 3) }
        enrich_points(points, windows, head=head, min_tail=3, overflow=overflow)

        # Second iteration
        points = overflow
        windows = { 'fwd3' : PointWindow(points, PointWindow.FORWARD, 3) }
        enrich_points(points, windows, head=head, min_tail=3, overflow=overflow)        


        self.assertEqual(2, len(overflow))



if __name__ == '__main__':
    unittest.main()
