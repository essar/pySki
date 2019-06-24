"""
"""

import unittest
from datetime import datetime
from pytz import timezone
from ski.data.commons import ExtendedGPSPoint, Track
from ski.io.db import TestDataStore

from ski.io.dataloader import *


class EmptyLoader:
    def load_points(self):
        return None

class TestLoader:
    points = [
        ExtendedGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0.0),
        ExtendedGPSPoint(ts=2, lat=1.0, lon=1.0, alt=2, spd=0.0),
        ExtendedGPSPoint(ts=3, lat=1.0, lon=1.0, alt=4, spd=0.0),
        ExtendedGPSPoint(ts=4, lat=1.0, lon=1.0, alt=3, spd=0.0)
    ]
    ptr = 0


    def load_points(self):
        if self.ptr >= len(self.points):
            return None

        points = self.points[self.ptr:100]
        self.ptr += len(points)
        return points


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Create data store
        self.db = TestDataStore()

        # Create track in default timezone
        tz = timezone('UTC')
        self.track = Track('unittest','TEST', datetime.now(tz))


    def test_load_extended_points(self):
        # Prepare loader
        loader = TestLoader()

        res = load_extended_points(loader, self.db, self.track)
        self.assertTrue(res)
        self.assertEqual(4, self.db.insert_count)


    def test_load_points_to_db(self):
        # Prepare loader
        loader = TestLoader()

        res = load_points_to_db(loader, self.db, self.track)
        self.assertTrue(res)
        self.assertEqual(4, self.db.insert_count)


    def test_load_points_to_db_no_data(self):
        # Prepare loader
        loader = EmptyLoader()

        res = load_points_to_db(loader, self.db, self.track)
        self.assertFalse(res)
        self.assertEqual(0, self.db.insert_count)


if __name__ == '__main__':
    unittest.main()
