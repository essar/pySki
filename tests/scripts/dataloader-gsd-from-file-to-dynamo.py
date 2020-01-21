"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
from ski.aws.dynamo import DynamoDataStore, stats as write_stats
from ski.io.gsd import GSDFileSource, stats as loader_stats
from ski.io.track import TrackFileLoader
from ski.loader.cleanup import stats as cleanup_stats
from ski.loader.enrich import stats as enrich_stats
from ski.loader.dataloader import direct_write_stats as write_stats

from ski.loader.dataloader import *


TEST_TRACK_FILE = 'tests/testdata/ski_unittest.yaml'
TEST_DATA_FILE = 'tests/testdata/testdata.gsd'

# Create data store
db = DynamoDataStore()

# Create track loader
ldr = TrackFileLoader(TEST_TRACK_FILE)
track = ldr.get_track()

start = time.time()

# Create file loader; load a single GSD section (64 points)
with open(TEST_DATA_FILE, mode='r') as f:
    source = GSDFileSource(f)
    # Load points

    # gsd_file_to_db(source, track, db)
    gsd_file_to_directory(source, track)


end = time.time()

enrich_stats['point_count'] = 0
enrich_stats['process_time'] = 0

print('Execution completed in {:.2f} seconds'.format(end - start))

total_time = sum([x['process_time'] for x in [loader_stats, cleanup_stats, enrich_stats, write_stats]])
print('                    process time')
print(' phase     points     (s)    (%)')
print('---------------------------------')
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('loader', loader_stats['point_count'], loader_stats['process_time'], (loader_stats['process_time'] / total_time) * 100.0))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('cleanup', cleanup_stats['points_out'], cleanup_stats['process_time'], (cleanup_stats['process_time'] / total_time) * 100.0))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('enrich', enrich_stats['point_count'], enrich_stats['process_time'], (enrich_stats['process_time'] / total_time) * 100.0))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('write', write_stats['point_count'], write_stats['process_time'], (write_stats['process_time'] / total_time) * 100.0))
print('---------------------------------')
print('                 {:>8.3}          '.format(total_time))
