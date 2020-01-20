"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import logging
from datetime import datetime
from pytz import timezone
from ski.data.commons import Track
from ski.io.db import TestDataStore
from ski.io.gsd import GSDFileSource

from ski.loader.dataloader import *


TEST_DATA_FILE = 'tests/testdata/testdata.gsd'

# Set up logger
logging.basicConfig()
log.setLevel(logging.INFO)

# Create data store
db = TestDataStore()

# Create track in default timezone
tz = timezone('UTC')
track = Track('test','TEST', datetime.now(tz))

# Create file loader; load a single GSD section (64 points)
with open(TEST_DATA_FILE, mode='r') as f:
    loader = GSDFileSource(f, section_limit=1)
    # Load points
    load_all_points(loader, db, track, extended=False)
