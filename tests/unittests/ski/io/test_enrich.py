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

    def test_PointWindow_window_empty(self):
        # Prepare data
        points = []

        w = PointWindow(points, PointWindow.FORWARD, 5)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 0)
        self.assertFalse(w.window_full)


    def test_PointWindow_window_full_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 5, 5)

        res = w.window()
        log.info(res)

        self.assertEqual([1, 2, 3, 4, 5], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_window_full_backward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 6, 6)

        res = w.window()
        log.info(res)

        self.assertEqual([1, 2, 3, 4, 5, 6], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_window_full_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 5, 5)

        res = w.window()
        log.info(res)
        
        self.assertEqual([5, 6, 7, 8, 9], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_window_full_forward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 6, 4)

        res = w.window()
        log.info(res)
        
        self.assertEqual([4, 5, 6, 7, 8, 9], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_window_full_midpoint(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 5)

        res = w.window()
        log.info(res)

        self.assertEqual([3, 4, 5, 6, 7], res)
        self.assertTrue(w.window_full)


    def test_PointWindow_window_full_midpoint_even(self):
        # Prepare data
        points = list(range(10))

        self.assertRaises(ValueError, PointWindow, points, PointWindow.MIDPOINT, 6)


    def test_PointWindow_window_short_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 5, 3)

        res = w.window()
        log.info(res)

        self.assertEqual([0, 1, 2, 3], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_window_short_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 5, 6)

        res = w.window()
        log.info(res)

        self.assertEqual([6, 7, 8, 9], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_window_short_midpoint_bottom(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 1)

        res = w.window()
        log.info(res)

        self.assertEqual([0, 1, 2], res)
        self.assertFalse(w.window_full)


    def test_PointWindow_window_short_midpoint_top(self):
        # Prepare data
        points = list(range(10))
        size = 5

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 8)

        res = w.window()
        log.info(res)

        self.assertEqual([7, 8, 9], res)
        self.assertFalse(w.window_full)


    def test_alt_delta(self):
        # Prepare data
        points = [
            EnrichedPoint(alt=10),
            EnrichedPoint(alt=20),
            EnrichedPoint(alt=30),
            EnrichedPoint(alt=40),
            EnrichedPoint(alt=50)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = alt_delta(w)

        log.info('alt=%f', res)
        self.assertEqual(20, res)


    def test_alt_cuml_gain(self):
        # Prepare data
        points = [
            EnrichedPoint(alt_d=10),
            EnrichedPoint(alt_d=20),
            EnrichedPoint(alt_d=-30),
            EnrichedPoint(alt_d=40),
            EnrichedPoint(alt_d=50)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = alt_cuml_gain(w)

        log.info('alt_d=%f', res)
        self.assertEqual(60, res)


    def test_alt_cuml_loss(self):
        # Prepare data
        points = [
            EnrichedPoint(alt_d=10),
            EnrichedPoint(alt_d=20),
            EnrichedPoint(alt_d=-30),
            EnrichedPoint(alt_d=40),
            EnrichedPoint(alt_d=50)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = alt_cuml_loss(w)

        log.info('alt_d=%f', res)
        self.assertEqual(-30, res)


    def test_average_speed(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3)
        res = average_speed(w)

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


    def test_max_speed(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = max_speed(w)

        log.info('speed=%f', res)
        self.assertEqual(4.0, res)


    def test_min_speed(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = min_speed(w)

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


    def test_speed_delta(self):
        # Prepare data
        points = [
            EnrichedPoint(spd=1),
            EnrichedPoint(spd=2),
            EnrichedPoint(spd=3),
            EnrichedPoint(spd=4),
            EnrichedPoint(spd=5)
        ]

        w = PointWindow(points, PointWindow.FORWARD, 3, 1)
        res = speed_delta(w)

        log.info('speed=%f', res)
        self.assertEqual(2.0, res)


if __name__ == '__main__':
    unittest.main()
