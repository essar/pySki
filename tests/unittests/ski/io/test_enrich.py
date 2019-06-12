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

        self.assertEqual(len(res), 5)
        self.assertTrue(w.window_full)
        self.assertEqual(5, res[-1])


    def test_PointWindow_window_full_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 5, 5)

        res = w.window()
        log.info(res)
        
        self.assertEqual(len(res), 5)
        self.assertTrue(w.window_full)
        self.assertEqual(5, res[0])


    def test_PointWindow_window_full_midpoint(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 5)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 5)
        self.assertTrue(w.window_full)
        self.assertEqual(5, res[2])


    def test_PointWindow_window_short_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.BACKWARD, 5, 3)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 4)
        self.assertFalse(w.window_full)
        self.assertEqual(3, res[-1])


    def test_PointWindow_window_short_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.FORWARD, 5, 6)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 4)
        self.assertFalse(w.window_full)
        self.assertEqual(6, res[0])


    def test_PointWindow_window_short_midpoint_bottom(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 1)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 3)
        self.assertFalse(w.window_full)
        self.assertEqual(1, res[1])


    def test_PointWindow_window_short_midpoint_top(self):
        # Prepare data
        points = list(range(10))
        size = 5

        w = PointWindow(points, PointWindow.MIDPOINT, 5, 8)

        res = w.window()
        log.info(res)

        self.assertEqual(len(res), 3)
        self.assertFalse(w.window_full)
        self.assertEqual(8, res[1])
    



if __name__ == '__main__':
    unittest.main()
