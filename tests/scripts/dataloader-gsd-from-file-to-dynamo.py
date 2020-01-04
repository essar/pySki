"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import time
from datetime import datetime
from pytz import timezone
from ski.aws.dynamo import DynamoDataStore
from ski.data.commons import Track
from ski.io.gsd import GSDFileLoader

from ski.loader.dataloader import *


TEST_DATA_FILE = 'tests/testdata/testdata.gsd'

# Set up logger
logging.basicConfig()
log.setLevel(logging.INFO)

# Create data store
db = DynamoDataStore()

# Create track in default timezone
tz = timezone('UTC')
track = Track('test','TEST', datetime.now(tz))

start = time.time()

# Create file loader; load a single GSD section (64 points)
with open(TEST_DATA_FILE, mode='r') as f:
    loader = GSDFileLoader(f)
    # Load points
    load_all_points(loader, db, track)

end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))
