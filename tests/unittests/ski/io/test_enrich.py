"""
"""

import logging
import unittest
from ski.data.commons import EnrichedPoint

from ski.io.enrich import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.WARNING)


class TestEnrich(unittest.TestCase):

    '''
    PointWindow.for_points()
    '''

    def test_PointWindow_for_points_empty(self):
        # Prepare data
        points = []

        w = PointWindow(PointWindow.FORWARD, 5)

        res = w.for_points(points)
        log.info('points=%s; 5F=%s', points, res)

        self.assertEqual(len(res), 0)


    def test_PointWindow_for_points_full_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.BACKWARD, 5)

        res = w.for_points(points, 5)
        log.info('points=%s; 5B=%s', points, res)

        self.assertEqual([1, 2, 3, 4, 5], res)


    def test_PointWindow_for_points_full_backward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.BACKWARD, 6)

        res = w.for_points(points, 6)
        log.info('points=%s; 6B=%s', points, res)

        self.assertEqual([1, 2, 3, 4, 5, 6], res)


    def test_PointWindow_for_points_full_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.FORWARD, 5)

        res = w.for_points(points, 5)
        log.info('points=%s; 5F=%s', points, res)
        
        self.assertEqual([5, 6, 7, 8, 9], res)


    def test_PointWindow_for_points_full_forward_even(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.FORWARD, 6)

        res = w.for_points(points, 4)
        log.info('points=%s; 6W=%s', points, res)
        
        self.assertEqual([4, 5, 6, 7, 8, 9], res)


    def test_PointWindow_for_points_full_midpoint(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.MIDPOINT, 5)

        res = w.for_points(points, 5)
        log.info('points=%s; 5MP=%s', points, res)

        self.assertEqual([3, 4, 5, 6, 7], res)


    def test_PointWindow_for_points_full_midpoint_even(self):
        # Prepare data
        points = list(range(10))

        log.info('points=%s; 6MP=[]', points)

        self.assertRaises(ValueError, PointWindow, PointWindow.MIDPOINT, 6)


    def test_PointWindow_for_points_short_backward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.BACKWARD, 5)

        res = w.for_points(points, 3)
        log.info('points=%s; 5B=%s', points, res)

        self.assertEqual([0, 1, 2, 3], res)


    def test_PointWindow_for_points_short_forward(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.FORWARD, 5)

        res = w.for_points(points, 6)
        log.info('points=%s; 6F=%s', points, res)

        self.assertEqual([6, 7, 8, 9], res)


    def test_PointWindow_for_points_short_midpoint_bottom(self):
        # Prepare data
        points = list(range(10))

        w = PointWindow(PointWindow.MIDPOINT, 5)

        res = w.for_points(points, 1)
        log.info('points=%s; 5MP=%s', points, res)

        self.assertEqual([0, 1, 2], res)


    def test_PointWindow_for_points_short_midpoint_top(self):
        # Prepare data
        points = list(range(10))
        size = 5

        w = PointWindow(PointWindow.MIDPOINT, 5)

        res = w.for_points(points, 8)
        log.info('points=%s; 5MP=%s', points, res)

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

        log.info('alts=%s; 3F window_alt_delta=%f', list(map(lambda p: p.alt, points)), res)
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

        log.info('alt_ds=%s; 3F window_alt_gain=%f', list(map(lambda p: p.alt_d, points)), res)
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

        log.info('alt_ds=%s; 3F window_alt_loss=%f', list(map(lambda p: p.alt_d, points)), res)
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

        log.info('dsts=%s; 3F window_distance=%f', list(map(lambda p: p.dst, points)), res)
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

        log.info('spds=%s; 3F window_speed_ave=%f', list(map(lambda p: p.spd, points)), res)
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

        log.info('spds=%s; 3F window_speed_max=%f', list(map(lambda p: p.spd, points)), res)
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

        log.info('spds=%s; 3F window_speed_min=%f', list(map(lambda p: p.spd, points)), res)
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

        log.info('spds=%s; 3F window_speed_delta=%f', list(map(lambda p: p.spd, points)), res)
        self.assertEqual(2.0, res)


    '''
    get_enriched_data
    '''
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
        log.info('points=%s; 5F=%s', points, res)

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


    '''
    enrich_points
    '''


    '''
    enrich_windows
    '''
    def test_enrich_windows(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]
        windows = { 'fwd3' : PointWindow(PointWindow.FORWARD, 3) }

        enrich_windows(points, windows)
        log.info('points=%s', points)

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


    def test_enrich_windows_with_head(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]

        windows = { 'bwd3' : PointWindow(PointWindow.BACKWARD, 3) }
        head = [
            EnrichedPoint(dst=0, alt=20, spd=0),
            EnrichedPoint(dst=1, alt=20, spd=1)
        ]

        enrich_windows(points, windows, head=head)
        log.info('points=%s', points)

        # Validate head data has been used on first points
        self.assertEqual(-10, points[0].windows['bwd3'].alt_delta)
        self.assertEqual(0,  points[1].windows['bwd3'].alt_delta)
        self.assertEqual(0, points[0].windows['bwd3'].speed_min)
        self.assertEqual(1, points[1].windows['bwd3'].speed_min)


    def test_enrich_windows_with_tail(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]

        windows = { 'fwd3' : PointWindow(PointWindow.FORWARD, 3) }
        tail = [
            EnrichedPoint(dst=1, alt=110, spd=6),
            EnrichedPoint(dst=1, alt=100, spd=7)
        ]

        enrich_windows(points, windows, tail=tail)
        log.info('points=%s', points)

        # Validate tail data has been used on last points
        self.assertEqual(40, points[3].windows['fwd3'].alt_delta)
        self.assertEqual(-10,  points[4].windows['fwd3'].alt_delta)
        self.assertEqual(6, points[3].windows['fwd3'].speed_max)
        self.assertEqual(7, points[4].windows['fwd3'].speed_max)


    def test_enrich_windows_with_head_and_tail(self):
        # Prepare data
        points = [
            EnrichedPoint(dst=1, alt=10, spd=1),
            EnrichedPoint(dst=1, alt=20, spd=2),
            EnrichedPoint(dst=1, alt=40, spd=3),
            EnrichedPoint(dst=1, alt=70, spd=4),
            EnrichedPoint(dst=1, alt=110, spd=5)
        ]

        windows = { 'bwd4' : PointWindow(PointWindow.BACKWARD, 4), 'fwd4' : PointWindow(PointWindow.FORWARD, 4) }
        head = [
            EnrichedPoint(dst=0, alt=20, spd=0),
            EnrichedPoint(dst=1, alt=20, spd=1)
        ]
        tail = [
            EnrichedPoint(dst=1, alt=110, spd=6),
            EnrichedPoint(dst=1, alt=100, spd=7)
        ]

        enrich_windows(points, windows, head=head, tail=tail)

        # Validate head and tail data has been used on last points
        self.assertEqual(20, points[2].windows['bwd4'].alt_delta)
        self.assertEqual(70, points[2].windows['fwd4'].alt_delta)
        self.assertEqual(1, points[2].windows['bwd4'].speed_min)
        self.assertEqual(6, points[2].windows['fwd4'].speed_max)
        


if __name__ == '__main__':
    unittest.main()
