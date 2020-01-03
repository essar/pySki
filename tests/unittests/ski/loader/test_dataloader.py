"""
"""

import unittest
from datetime import datetime
from pytz import timezone
from ski.data.commons import ExtendedGPSPoint, Track
from ski.io.db import TestDataStore

from ski.loader.dataloader import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.DEBUG)


class EmptyLoader:

    def load_points(self):
        return None


class TestLoader:

    def __init__(self, points=4):
        self.points = []
        for i in range(points):
            self.points.append(ExtendedGPSPoint(ts=i, lat=1.0, lon=1.0, alt=(i - 1), spd=0.0))

        self.ptr = 0

    def load_points(self, buf_size=100):
        if self.ptr >= len(self.points):
            return None

        points = self.points[self.ptr:(self.ptr + buf_size)]
        self.ptr += len(points)
        return points


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Create data store
        self.db = TestDataStore()

        # Create track in default timezone
        tz = timezone('UTC')
        self.track = Track('unittest', 'TEST', datetime.now(tz))

    def test_load_all_points(self):
        # Prepare loader
        loader = TestLoader(points=50)

        load_all_points(loader, self.db, self.track)

        self.assertEqual(50, self.db.insert_count, list(map(lambda p: p.ts, loader.points)))

    def test_load_all_points_exceeds_buffer(self):
        # Prepare loader
        loader = TestLoader(101)

        load_all_points(loader, self.db, self.track)

        self.assertEqual(101, self.db.insert_count)

    def test_load_points(self):
        # Prepare loader
        loader = TestLoader(points=50)
        window = PointWindow(head_length=30)

        res = load_points(loader, window, self.db, self.track)
        self.assertTrue(res)
        self.assertEqual(21, self.db.insert_count)

    def test_load_points_draining(self):
        # Prepare loader
        loader = TestLoader(points=50)
        window = PointWindow(head_length=30)

        window.drain = True

        res = load_points(loader, window, self.db, self.track)
        self.assertTrue(res)
        self.assertEqual(50, self.db.insert_count)

    def test_load_points_no_data(self):
        # Prepare loader
        loader = EmptyLoader()
        window = PointWindow()

        window.drain = True

        res = load_points(loader, window, self.db, self.track)
        self.assertFalse(res)
        self.assertEqual(0, self.db.insert_count)


if __name__ == '__main__':
    unittest.main()
