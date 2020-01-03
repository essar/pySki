"""
"""

import logging
import unittest
from ski.data.commons import ExtendedGPSPoint

from ski.loader.enrich import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.DEBUG)


class TestEnrich(unittest.TestCase):

    def test_PointWindow_load_points(self):
        # Prepare data
        w = PointWindow()
        points = [x for x in range(5)]
        w.load_points(points)

        self.assertListEqual([0, 1, 2, 3, 4], w.head)
        self.assertListEqual([], w.tail)

    def test_PointWindow_load_points_to_existing_head(self):
        # Prepare data
        w = PointWindow()
        points = [x for x in range(5)]
        w.head += [x for x in range(5)]
        w.tail += [x for x in range(5)]

        w.load_points(points)

        self.assertEqual(10, len(w.head))
        self.assertEqual(5, len(w.tail))

    def test_PointWindow_extract_fwd3(self):
        # Prepare data
        w = PointWindow()
        w.head += [x for x in range(1, 5)]
        w.tail += [x for x in range(1, 5)]
        w.target_point = 0

        res = w.extract(PointWindow.FORWARD, 3)

        self.assertEqual(3, len(res))
        self.assertListEqual([0, 1, 2], res)

    def test_PointWindow_extract_fwd6(self):
        # Prepare data
        w = PointWindow()
        w.head += [x for x in range(1, 5)]
        w.tail += [x for x in range(1, 5)]
        w.target_point = 0

        res = w.extract(PointWindow.FORWARD, 6)

        self.assertEqual(5, len(res))
        self.assertListEqual([0, 1, 2, 3, 4], res)

    def test_PointWindow_extract_bwd3(self):
        # Prepare data
        w = PointWindow()
        w.head += [x for x in range(1, 5)]
        w.tail += [x for x in range(1, 5)]
        w.target_point = 0

        res = w.extract(PointWindow.BACKWARD, 3)

        self.assertEqual(3, len(res))
        self.assertListEqual([3, 4, 0], res)

    def test_PointWindow_extract_bwd6(self):
        # Prepare data
        w = PointWindow()
        w.head += [x for x in range(1, 5)]
        w.tail += [x for x in range(1, 5)]
        w.target_point = 0

        res = w.extract(PointWindow.BACKWARD, 6)

        self.assertEqual(5, len(res))
        self.assertListEqual([1, 2, 3, 4, 0], res)

    def test_PointWindow_extract_mp3(self):
        # Prepare data
        w = PointWindow()
        w.head += [x for x in range(1, 5)]
        w.tail += [x for x in range(1, 5)]
        w.target_point = 0
        res = w.extract(PointWindow.MIDPOINT, 3)

        self.assertEqual(3, len(res))
        self.assertListEqual([4, 0, 1], res)

    def test_PointWindow_extract_mp11(self):
        # Prepare data
        w = PointWindow()
        w.head += [x for x in range(1, 5)]
        w.tail += [x for x in range(1, 5)]
        w.target_point = 0

        res = w.extract(PointWindow.MIDPOINT, 11)

        self.assertEqual(9, len(res))
        self.assertListEqual([1, 2, 3, 4, 0, 1, 2, 3, 4], res)

    def test_PointWindow_process(self):
        # Prepare data
        w = PointWindow(head_length=3)
        w.head += [x for x in range(5)]
        w.tail += [x for x in range(5)]

        res = w.process()

        self.assertTrue(res)
        self.assertEqual(0, w.target_point)
        self.assertEqual(4, len(w.head))
        self.assertEqual(1, w.head[0])
        self.assertEqual(5, len(w.tail))
        self.assertEqual(4, w.tail[-1])

        res = w.process()

        self.assertTrue(res)
        self.assertEqual(1, w.target_point)
        self.assertEqual(3, len(w.head))
        self.assertEqual(2, w.head[0])
        self.assertEqual(6, len(w.tail))
        self.assertEqual(0, w.tail[-1])

    def test_PointWindow_process_short_head(self):
        # Prepare data
        w = PointWindow(head_length=6)
        w.head += [x for x in range(5)]
        res = w.process()

        self.assertFalse(res)
        self.assertEqual(0, w.target_point)
        self.assertEqual(4, len(w.head))

    def test_PointWindow_process_short_head_draining(self):
        # Prepare data
        w = PointWindow(head_length=5)
        w.head += [x for x in range(5)]
        w.drain = True
        res = w.process()

        self.assertTrue(res)
        self.assertEqual(0, w.target_point)
        self.assertEqual(4, len(w.head))

    def test_PointWindow_process_short_head_draining_empty_head(self):
        # Prepare data
        w = PointWindow(head_length=5)
        w.drain = True
        res = w.process()

        self.assertFalse(res)

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

        log.info('alts=%s; alt_delta=%f', list(map(lambda p: p.alt, points)), res)
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

        log.info('alt_ds=%s; alt_gain=%f', list(map(lambda p: p.alt_d, points)), res)
        self.assertEqual(120, res)

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

        log.info('alt_ds=%s; alt_loss=%f', list(map(lambda p: p.alt_d, points)), res)
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

        log.info('dsts=%s; distance=%f', list(map(lambda p: p.dst, points)), res)
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

        log.info('spds=%s; speed_ave=%f', list(map(lambda p: p.spd, points)), res)
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

        log.info('spds=%s; speed_max=%f', list(map(lambda p: p.spd, points)), res)
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

        log.info('spds=%s; speed_min=%f', list(map(lambda p: p.spd, points)), res)
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

        log.info('spds=%s; speed_delta=%f', list(map(lambda p: p.spd, points)), res)
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
        window = PointWindow(head_length=3, tail_length=3)

        wk = WindowKey(PointWindow.BACKWARD, 3)
        res = enrich_points(points, window, [wk])

        self.assertEqual(3, len(res))
        self.assertIsNotNone(points[0].windows[wk])
        self.assertEqual(1, points[0].windows[wk].distance)

        # Verify altitude delta values
        self.assertEqual(0, points[0].windows[wk].alt_delta)
        self.assertEqual(10, points[1].windows[wk].alt_delta)
        self.assertEqual(30, points[2].windows[wk].alt_delta)

        # Verify maximum speed values
        self.assertEqual(1, points[0].windows[wk].speed_max)
        self.assertEqual(2, points[1].windows[wk].speed_max)
        self.assertEqual(3, points[2].windows[wk].speed_max)

    def test_enrich_points_draining(self):
        # Prepare data
        points = [
            ExtendedGPSPoint(dst=1, alt=10, spd=1),
            ExtendedGPSPoint(dst=1, alt=20, spd=2),
            ExtendedGPSPoint(dst=1, alt=40, spd=3),
            ExtendedGPSPoint(dst=1, alt=70, spd=4),
            ExtendedGPSPoint(dst=1, alt=110, spd=5)
        ]
        window = PointWindow(head_length=3, tail_length=3)
        window.drain = True

        wk = WindowKey(PointWindow.BACKWARD, 3)

        res = enrich_points(points, window, [wk])

        self.assertEqual(5, len(res))
        self.assertIsNotNone(points[0].windows[wk])
        self.assertEqual(1, points[0].windows[wk].distance)

        # Verify altitude delta values
        self.assertEqual(0, points[0].windows[wk].alt_delta)
        self.assertEqual(10, points[1].windows[wk].alt_delta)
        self.assertEqual(30, points[2].windows[wk].alt_delta)
        self.assertEqual(50, points[3].windows[wk].alt_delta)
        self.assertEqual(70, points[4].windows[wk].alt_delta)

        # Verify maximum speed values
        self.assertEqual(1, points[0].windows[wk].speed_max)
        self.assertEqual(2, points[1].windows[wk].speed_max)
        self.assertEqual(3, points[2].windows[wk].speed_max)
        self.assertEqual(4, points[3].windows[wk].speed_max)
        self.assertEqual(5, points[4].windows[wk].speed_max)


if __name__ == '__main__':
    unittest.main()
