"""
  Test script for ski.io.dataloader.

  Loads GSD data from an S3 resource.
"""
import logging
from datetime import datetime
from pytz import timezone
from ski.aws.s3 import S3File
from ski.data.commons import Track
from ski.io.db import TestDataStore
from ski.io.gsd import GSDS3Loader

from ski.io.dataloader import *


TEST_DATA_S3 = 'gsd/testdata.gsd'

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Create data store
db = TestDataStore()

# Create track in default timezone
tz = timezone('UTC')
track = Track('test','TEST', datetime.now(tz))

# Create S3 loader; load a single GSD section (64 points)
s3f = S3File(TEST_DATA_S3, True)
loader = GSDS3Loader(s3f, section_limit=1)
# Load points
load_all_points(loader, db, track)
