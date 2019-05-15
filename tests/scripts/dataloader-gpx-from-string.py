"""
  Test script for ski.io.dataloader.

  Loads GPX data from a string.
"""
import logging
from datetime import datetime
from pytz import timezone
from ski.data.commons import Track
from ski.io.db import TestDataStore
from ski.io.gpx import GPXStringLoader

from ski.io.dataloader import *


TEST_DATA = '<track><trkpt lat="51.0000" lon="01.0000"><time>2019-04-16T17:00:00Z</time><ele>149</ele><speed>4.5</speed></trkpt>\
             <trkpt lat="51.2345" lon="-01.2345"><time>2019-04-16T17:00:05Z</time><ele>135</ele><speed>3.25</speed></trkpt></track>'

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

log.debug('Testing data:\n%s', TEST_DATA)


# Create data store
db = TestDataStore()

# Create track in default timezone
tz = timezone('UTC')
track = Track('test','TEST', datetime.now(tz))

# Create string loader
loader = GPXStringLoader(TEST_DATA)
# Load points
load_all_points(loader, db, track)
