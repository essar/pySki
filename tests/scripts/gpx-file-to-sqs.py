"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import time

from datetime import time as datetime
from math import floor
from ski.aws.sqs import stats as write_stats
from ski.logging import calc_stats
from ski.io.gpx import GPXSource, stats as reader_stats
from ski.io.track import TrackFileLoader
from ski.loader.cleanup import stats as cleanup_stats
from ski.loader.dataloader import file_to_sqs


TEST_TRACK_FILE = 'tests/testdata/ski_unittest_2.yaml'
TEST_DATA_FILE = 'tests/testdata/testdata.gpx'

# Script start time
start = time.time()

# Create track loader
ldr = TrackFileLoader(TEST_TRACK_FILE)
track = ldr.get_track()

# Create GPX Source
source = GPXSource(TEST_DATA_FILE)
file_to_sqs(source, track)

# Script end time
end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))

total_time = sum([x['process_time'] for x in [reader_stats, cleanup_stats, write_stats]])
duration = datetime(0, floor(total_time / 60), floor(total_time % 60), floor(total_time % 1))
duration_str = duration.strftime('%Mm%Ss')

print('                    process time ')
print(' phase     points     (s)    (%) ')
print('---------------------------------')
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('loader', *calc_stats(reader_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('cleanup', *calc_stats(cleanup_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('write', *calc_stats(write_stats, total_time)))
print('---------------------------------')
print('               {:>10s}'.format(duration_str))
