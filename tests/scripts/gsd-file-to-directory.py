"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import time
from datetime import time as datetime
from math import floor

from ski.logging import calc_stats
from ski.io.gsd import GSDFileSource, stats as loader_stats
from ski.io.track import TrackFileLoader
from ski.loader.cleanup import stats as cleanup_stats
from ski.loader.enrich import stats as enrich_stats
from ski.loader.dataloader import gsd_file_to_directory, direct_write_stats as write_stats


TEST_TRACK_FILE = 'tests/testdata/ski_unittest.yaml'
TEST_DATA_FILE = 'tests/testdata/testdata.gsd'

# Script start time
start = time.time()

# Create track loader
ldr = TrackFileLoader(TEST_TRACK_FILE)
track = ldr.get_track()

# Open the file
with open(TEST_DATA_FILE, mode='r') as f:
    # Create GSD source from file
    source = GSDFileSource(f)

    # Load points
    gsd_file_to_directory(source, track)

# Script end time
end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))

# Provide default values for unused phases
enrich_stats['point_count'] = 0
enrich_stats['process_time'] = 0

total_time = sum([x['process_time'] for x in [loader_stats, cleanup_stats, enrich_stats, write_stats]])
duration = datetime(0, floor(total_time / 60), floor(total_time % 60), floor(total_time % 1))
duration_str = duration.strftime('%Mm%Ss')

print('                    process time ')
print(' phase     points     (s)    (%) ')
print('---------------------------------')
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('loader', *calc_stats(loader_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('cleanup', *calc_stats(cleanup_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('enrich', *calc_stats(enrich_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('write', *calc_stats(write_stats, total_time)))
print('---------------------------------')
print('               {:>10s}'.format(duration_str))
