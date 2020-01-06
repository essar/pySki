"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import time
from ski.aws.dynamo import DynamoDataStore
from ski.io.gsd import GSDFileLoader
from ski.io.track import TrackFileLoader

from ski.loader.dataloader import *


TEST_TRACK_FILE = 'tests/testdata/ski_unittest.yaml'
TEST_DATA_FILE = 'tests/testdata/testdata.gsd'

# Set up logger
logging.basicConfig()
log.setLevel(logging.INFO)

# Create data store
db = DynamoDataStore()

# Create track loader
ldr = TrackFileLoader(TEST_TRACK_FILE)
track = ldr.get_track()

start = time.time()

# Create file loader; load a single GSD section (64 points)
with open(TEST_DATA_FILE, mode='r') as f:
    loader = GSDFileLoader(f)
    # Load points
    load_all_points(loader, db, track)

end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))
