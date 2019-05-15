"""
"""

import logging
import unittest
from datetime import datetime
from pytz import timezone
from ski.data.commons import BasicGPSPoint, Track
from ski.io.db import TestDataStore

from ski.io.dataloader import *

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class EmptyLoader:
    def load_points(self):
        return None

class TestLoader:
    def load_points(self):
        return [BasicGPSPoint(ts=1, lat=1.0, lon=1.0, alt=0, spd=0.0)]


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Create data store
        self.db = TestDataStore()

        # Create track in default timezone
        tz = timezone('UTC')
        self.track = Track('unittest','TEST', datetime.now(tz))


    def test_load_points_to_db(self):
        # Prepare loader
        loader = TestLoader()

        res = load_points_to_db(loader, self.db, self.track)
        self.assertTrue(res)
        self.assertEqual(1, self.db.insert_count)


    def test_load_points_to_db_no_data(self):
        # Prepare loader
        loader = EmptyLoader()

        res = load_points_to_db(loader, self.db, self.track)
        self.assertFalse(res)
        self.assertEqual(0, self.db.insert_count)


if __name__ == '__main__':
    unittest.main()
