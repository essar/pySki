"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
from ski.aws.dynamo import DynamoDataStore, stats as write_stats
from ski.io.gpx import GPXFileSource, stats as loader_stats
from ski.io.track import TrackFileLoader
from ski.loader.cleanup import stats as cleanup_stats
from ski.loader.enrich import stats as enrich_stats

from ski.loader.dataloader import *


TEST_TRACK_FILE = 'tests/testdata/ski_unittest2.yaml'
TEST_DATA_FILE = 'tests/testdata/testdata.gpx'

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
    source = GPXFileSource(f)
    # Load points

    gpx_file_to_db(source, track, db)
    # gpx_file_to_directory(source, track)


end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))

total_time = sum([x['process_time'] for x in [loader_stats, cleanup_stats, enrich_stats, write_stats]])
print('                    process time\n'
      'phase     points      (s)    (%)\n'
      '--------------------------------\n'
      '{:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%\n'
      '{:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%\n'
      '{:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%\n'
      '{:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%\n'.format(
        'loader', loader_stats['point_count'], loader_stats['process_time'], (loader_stats['process_time'] / total_time) * 100.0,
        'cleanup', cleanup_stats['points_out'], cleanup_stats['process_time'], (cleanup_stats['process_time'] / total_time) * 100.0,
        'enrich', enrich_stats['point_count'], enrich_stats['process_time'], (enrich_stats['process_time'] / total_time) * 100.0,
        'write', write_stats['point_count'], write_stats['process_time'], (write_stats['process_time'] / total_time) * 100.0
        )
      )
