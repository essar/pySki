"""
"""

import logging
import unittest
from datetime import datetime
from pytz import timezone
from ski.data.commons import ExtendedGPSPoint, Track
from ski.io.db import TestDataStore

from ski.io.dataloader import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.INFO)


class EmptyLoader:
    def load_points(self):
        return None

class TestLoader:

    def __init__(self, points=4):
        self.points = []
        for i in range(points):
            self.points.append(ExtendedGPSPoint(
                ts  = i,
                lat = 1.0,
                lon = 1.0,
                alt = (i - 1),
                spd = 0.0)
            )

        self.ptr = 0


    def load_points(self, bufsize=100):
        if self.ptr >= len(self.points):
            return None

        points = self.points[self.ptr:(self.ptr + bufsize)]
        self.ptr += len(points)
        return points



class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Create data store
        self.db = TestDataStore()

        # Create track in default timezone
        tz = timezone('UTC')
        self.track = Track('unittest','TEST', datetime.now(tz))


    def test_load_all_points(self):
        # Prepare loader
        loader = TestLoader()

        load_all_points(loader, self.db, self.track)

        self.assertEqual(4, self.db.insert_count)


    def test_load_all_points_exceeds_buffer(self):
        # Prepare loader
        loader = TestLoader(101)

        load_all_points(loader, self.db, self.track)

        self.assertEqual(101, self.db.insert_count)


    def test_load_basic_points(self):
        # Prepare loader
        loader = TestLoader()

        res = load_basic_points(loader, self.db, self.track)
        self.assertTrue(res)
        self.assertEqual(4, self.db.insert_count)


    def test_load_basic_points_no_data(self):
        # Prepare loader
        loader = EmptyLoader()

        res = load_basic_points(loader, self.db, self.track)
        self.assertFalse(res)
        self.assertEqual(0, self.db.insert_count)


    def test_load_extended_points(self):
        # Prepare loader
        loader = TestLoader()

        tail = []
        res = load_extended_points(loader, self.db, self.track, head=[], tail=tail)
        self.assertTrue(res)
        self.assertEqual(4, self.db.insert_count)
        self.assertEqual(0, len(tail))


    def test_load_extended_points_no_data(self):
        # Prepare loader
        loader = EmptyLoader()

        res = load_extended_points(loader, self.db, self.track, head=[], tail=[])
        self.assertFalse(res)
        self.assertEqual(0, self.db.insert_count)


    def test_load_extended_points_with_tail(self):
        # Prepare loader
        loader = TestLoader()
        
        tail = []
        res = load_extended_points(loader, self.db, self.track, head=[], tail=tail)
        self.assertTrue(res)
        self.assertEqual(4, self.db.insert_count)
        self.assertEqual(0, len(tail))



if __name__ == '__main__':
    unittest.main()
