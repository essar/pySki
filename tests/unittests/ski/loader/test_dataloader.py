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
log.setLevel(logging.WARNING)


class EmptyLoader:

    def __init__(self):
        self.points = []
        self.ptr = 0


class TestBatchWindow:

    def __init__(self):
        self.body = []

    def load_points(self, points, drain, process_f, **kwargs):
        self.body += points if points is not None else []


class TestSource:

    def __init__(self, size=10):
        self.points = []
        for i in range(size):
            self.points.append(ExtendedGPSPoint(ts=i, lat=1.0, lon=1.0, alt=(i - 1), spd=0.0))

        self.ptr = 0


def test_parser(loader, load_size=64, **kwargs):
    if loader.ptr < len(loader.points):
        points = loader.points[loader.ptr:(loader.ptr + load_size)]
        loader.ptr += len(points)

        return points

    return None


def test_process(track, body, tail, drain, db, **kwargs):
    db.add_points_to_track(track, body)


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Create data store
        self.db = TestDataStore()

        # Create track in default timezone
        tz = timezone('UTC')
        self.track = Track('unittest', 'TEST', datetime.now(tz))

    """
    load_all_points(source, track, parser_f, loader_f, ** kwargs)
    """
    def test_load_all_points(self):
        # Prepare source
        source = TestSource(size=1000)

        load_all_points(source, self.track, test_parser, direct_process_batch, db=self.db)

        self.assertEqual(1000, self.db.insert_count)

    def test_load_all_points_exceeds_buffer(self):
        # Prepare source
        source = TestSource(size=1200)

        load_all_points(source, self.track, test_parser, direct_process_batch, db=self.db)

        self.assertEqual(1200, self.db.insert_count)

    """
    load_into_batch(source, track, batch, drain, parser_f, process_f, **kwargs)
    """
    def test_load_into_batch(self):
        # Prepare source
        source = TestSource(size=50)
        batch = TestBatchWindow()

        res = load_into_batch(source, self.track, batch, False, test_parser, None)
        self.assertTrue(res)
        self.assertEqual(50, len(batch.body))

    def test_load_into_batch_no_data(self):
        # Prepare source
        source = EmptyLoader()
        batch = TestBatchWindow()

        res = load_into_batch(source, self.track, batch, True, test_parser, test_process, db=self.db)
        self.assertFalse(res)
        self.assertEqual(0, self.db.insert_count)



    def test_load_into_batch_incomplete_batch(self):
        # Prepare source
        source = TestSource(size=40)
        batch = BatchWindow(self.track, batch_size=50, overlap=0)

        res = load_into_batch(source, self.track, batch, False, test_parser, test_process, db=self.db)
        self.assertTrue(res)
        self.assertEqual(0, self.db.insert_count)
        self.assertEqual(40, len(batch.body))

    def test_load_into_batch_draining(self):
        # Prepare source
        source = TestSource(size=64)
        batch = BatchWindow(self.track, batch_size=50, overlap=30)

        res = load_into_batch(source, self.track, batch, True, test_parser, test_process, db=self.db)
        self.assertTrue(res)
        self.assertEqual(50, self.db.insert_count)
        self.assertEqual(14, len(batch.body))

    def test_load_into_batch_drain_with_overflow(self):
        # Prepare source
        source = TestSource(size=100)
        batch = BatchWindow(self.track, batch_size=50, overlap=30)

        res = load_into_batch(source, self.track, batch, True, test_parser, test_process, db=self.db)
        self.assertTrue(res)
        self.assertEqual(50, self.db.insert_count)


if __name__ == '__main__':
    unittest.main()
