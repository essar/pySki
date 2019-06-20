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

    def test_PointWindow_for_points_empty(self):
        # Prepare data
        points = []

        w = PointWindow(PointWindow.FORWARD, 5)

        res = w.for_points(points)
        log.info(res)

        self.assertEqual(len(res), 0)


    def test_PointWindow_for_points_full_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.BACKWARD, 5)

        res = w.for_points(points, 5)
        log.info(res)

        self.assertEqual([1, 2, 3, 4, 5], res)


    def test_PointWindow_for_points_full_backward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.BACKWARD, 6)

        res = w.for_points(points, 6)
        log.info(res)

        self.assertEqual([1, 2, 3, 4, 5, 6], res)


    def test_PointWindow_for_points_full_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.FORWARD, 5)

        res = w.for_points(points, 5)
        log.info(res)
        
        self.assertEqual([5, 6, 7, 8, 9], res)


    def test_PointWindow_for_points_full_forward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.FORWARD, 6)

        res = w.for_points(points, 4)
        log.info(res)
        
        self.assertEqual([4, 5, 6, 7, 8, 9], res)


    def test_PointWindow_for_points_full_midpoint(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.MIDPOINT, 5)

        res = w.for_points(points, 5)
        log.info(res)

        self.assertEqual([3, 4, 5, 6, 7], res)


    def test_PointWindow_for_points_full_midpoint_even(self):
        # Prepare data
        points = list(range(10))

        self.assertRaises(ValueError, PointWindow, PointWindow.MIDPOINT, 6)


    def test_PointWindow_for_points_short_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.BACKWARD, 5)

        res = w.for_points(points, 3)
        log.info(res)

        self.assertEqual([0, 1, 2, 3], res)


    def test_PointWindow_for_points_short_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.FORWARD, 5)

        res = w.for_points(points, 6)
        log.info(res)

        self.assertEqual([6, 7, 8, 9], res)


    def test_PointWindow_for_points_short_midpoint_bottom(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.MIDPOINT, 5)

        res = w.for_points(points, 1)
        log.info(res)

        self.assertEqual([0, 1, 2], res)


    def test_PointWindow_for_points_short_midpoint_top(self):
        # Prepare data
        points = list(range(10))
        size = 5

        w = PointWindow(PointWindow.MIDPOINT, 5)

        res = w.for_points(points, 8)
        log.info(res)

        self.assertEqual([7, 8, 9], res)


    def test_window_alt_delta(self):
        # Prepare data
        points = [
            EnrichedPoint(alt=10),
            EnrichedPoint(alt=20),
            EnrichedPoint(alt=30),
            EnrichedPoint(alt=40),
            EnrichedPoint(alt=50)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_alt_delta(w, points, 1)

        log.info('alt=%f', res)
        self.assertEqual(20, res)


    def test_window_alt_cuml_gain(self):
        # Prepare data
        points = [
            EnrichedPoint(alt_d=10),
            EnrichedPoint(alt_d=20),
            EnrichedPoint(alt_d=-30),
            EnrichedPoint(alt_d=40),
            EnrichedPoint(alt_d=50)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_alt_cuml_gain(w, points, 1)

        log.info('alt_d=%f', res)
        self.assertEqual(60, res)


    def test_window_alt_cuml_loss(self):
        # Prepare data
        points = [
            EnrichedPoint(alt_d=10),
            EnrichedPoint(alt_d=20),
            EnrichedPoint(alt_d=-30),
            EnrichedPoint(alt_d=40),
            EnrichedPoint(alt_d=50)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_alt_cuml_loss(w, points, 1)

        log.info('alt_d=%f', res)
        self.assertEqual(-30, res)


    def test_window_distance(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1),
            EnrichedPoint(dst=2),
            EnrichedPoint(dst=3),
            EnrichedPoint(dst=4),
            EnrichedPoint(dst=5)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_distance(w, points, 1)

        log.info('dst=%f', res)
        self.assertEqual(9, res)


    def test_window_speed_ave(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_speed_ave(w, points, 1)

        log.info('speed=%f', res)
        self.assertEqual(3.0, res)


    def test_window_speed_max(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_speed_max(w, points, 1)

        log.info('speed=%f', res)
        self.assertEqual(4.0, res)


    def test_window_speed_min(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_speed_min(w, points, 1)

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


    def test_window_speed_delta(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(PointWindow.FORWARD, 3)
        res = window_speed_delta(w, points, 1)

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
        window = PointWindow(PointWindow.FORWARD, 5)

        res = get_enriched_data(window, points)
        log.info('Enriched data: %s', res)

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
        windows = { 'fwd3' : PointWindow(PointWindow.FORWARD, 3) }

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


    def test_enrich_points_with_tail(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]

        windows = { 'fwd3' : PointWindow(PointWindow.FORWARD, 3) }
        tail = []

        # 1st iteration
        enrich_points(points, windows, min_tail=3, tail=tail)

        # Should be 2 points left unprocessed
        self.assertEqual(2, len(tail))

        # 2nd iteration; tail from previous run
        enrich_points(tail, windows)

        # Validate window has been created on all points
        self.assertIsNotNone(points[0].windows['fwd3'])
        self.assertIsNotNone(points[1].windows['fwd3'])
        self.assertIsNotNone(points[2].windows['fwd3'])
        self.assertIsNotNone(points[3].windows['fwd3'])
        self.assertIsNotNone(points[4].windows['fwd3'])


    def test_enrich_points_2_batches(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]
        points2 = [
            EnrichedPoint(dst=1, alt=110, spd=5),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=10, spd=1)
        ]

        windows = { 'fwd3' : PointWindow(PointWindow.FORWARD, 3) }
        tail = []

        # 1st iteration
        enrich_points(points, windows, min_tail=3, tail=tail)

        # Should be 2 points left unprocessed
        self.assertEqual(2, len(tail))

        # 2nd iteration; tail from previous run plus new points
        enrich_points((tail + points2), windows)

        # Validate window has been created on all points
        self.assertIsNotNone(points[0].windows['fwd3'])
        self.assertIsNotNone(points[4].windows['fwd3'])
        self.assertIsNotNone(points2[0].windows['fwd3'])
        self.assertIsNotNone(points2[4].windows['fwd3'])

        # Validate window values across batches
        self.assertEqual(-40, points[4].windows['fwd3'].alt_delta)
        self.assertEqual(-1, points[4].windows['fwd3'].speed_delta)
        

    def test_enrich_points_2_batches_with_lookback(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]
        points2 = [
            EnrichedPoint(dst=1, alt=110, spd=5),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=10, spd=1)
        ]

        windows = { 'bwd3' : PointWindow(PointWindow.BACKWARD, 3) }
        head = []

        # 1st iteration
        enrich_points(points, windows, max_head=3, head=head)

        # Should be 3 points provided in the head
        self.assertEqual(3, len(head))

        # 2nd iteration; overflow from previous run plus new points, passing head fron 1st run
        enrich_points(points2, windows, max_head=3, head=head)

        # Validate window has been created on all points
        self.assertIsNotNone(points[0].windows['bwd3'])
        self.assertIsNotNone(points[4].windows['bwd3'])
        self.assertIsNotNone(points2[0].windows['bwd3'])
        self.assertIsNotNone(points2[4].windows['bwd3'])

        # Validate window values across batches
        self.assertEqual(70, points2[0].windows['bwd3'].alt_min)
        self.assertEqual(110, points2[1].windows['bwd3'].alt_max)


if __name__ == '__main__':
    unittest.main()
