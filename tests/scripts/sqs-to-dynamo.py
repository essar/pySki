"""
  Test script for ski.io.dataloader.

  Loads GSD data from a local file.
"""
import time
from datetime import time as datetime
from math import floor

from ski.logging import calc_stats
from ski.aws.dynamo import DynamoDataStore, stats as write_stats
from ski.aws.sqs import sqs_read_queue
from ski.loader.enrich import stats as enrich_stats
from ski.loader.dataloader import direct_to_db


# Script start time
start = time.time()

# Create data store
db = DynamoDataStore()

sqs_read_queue(direct_to_db, db)

# Script end time
end = time.time()

print('Execution completed in {:.2f} seconds'.format(end - start))

total_time = sum([x['process_time'] for x in [enrich_stats, write_stats]])
duration = datetime(0, floor(total_time / 60), floor(total_time % 60), floor(total_time % 1))
duration_str = duration.strftime('%Mm%Ss')

print('                    process time ')
print(' phase     points     (s)    (%) ')
print('---------------------------------')
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('enrich', *calc_stats(enrich_stats, total_time)))
print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('write', *calc_stats(write_stats, total_time)))
print('---------------------------------')
print('               {:>10s}'.format(duration_str))
