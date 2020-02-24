"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import time
from datetime import time as datetime
from math import floor

from ski.logging import calc_stats
from ski.io.db import TestDataStore
from ski.io.gsd import GSDSource, stats as reader_stats
from ski.io.track import TrackFileLoader
from ski.loader.cleanup import stats as cleanup_stats
from ski.loader.enrich import stats as enrich_stats
from ski.loader.dataloader import file_to_db


TEST_TRACK_FILE = 'tests/testdata/track_20200219.yaml'
TEST_DATA_FILE = 'tests/testdata/20200219_sj.gsd'

# Script start time
start = time.time()

# Create data store
db = TestDataStore()

# Create track loader
ldr = TrackFileLoader(TEST_TRACK_FILE)
track = ldr.get_track()

# Create GSD data source
source = GSDSource(TEST_DATA_FILE)
file_to_db(source, track, db)

# Script end time
end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))

total_time = sum([x['process_time'] for x in [reader_stats, cleanup_stats, enrich_stats]])
duration = datetime(0, floor(total_time / 60), floor(total_time % 60), floor(total_time % 1))
duration_str = duration.strftime('%Mm%Ss')

print('                    process time ')
print(' phase     points     (s)    (%) ')
print('---------------------------------')
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('loader', *calc_stats(reader_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('cleanup', *calc_stats(cleanup_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('enrich', *calc_stats(enrich_stats, total_time)))
print('---------------------------------')
print('               {:>10s}'.format(duration_str))

print('')
print('---------------------------------')
print('QuickStats')
print('---------------------------------')
print(' Total distance  {:>.2f}km'.format(enrich_stats['track_total_distance']))
print(' Desc. distance  {:>.2f}km'.format(enrich_stats['track_desc_distance']))
print(' Total descent   {:>03d}m'.format(enrich_stats['track_total_desc']))
print(' High altitude   {:>04d}m'.format(enrich_stats['track_max_alt']))
print(' Low altitude    {:>04d}m'.format(enrich_stats['track_min_alt']))
print(' High speed      {:>.1f}kph'.format(enrich_stats['track_max_speed']))
print(' 30s sust speed  {:>.1f}kph'.format(enrich_stats['B,30_sust_spd']))
print('---------------------------------')
