"""
  Module providing functions for working with AWS DynamoDB.
"""
import logging
import time

from datetime import time as datetime
from math import floor
from urllib.parse import unquote_plus
from ski.logging import calc_stats
from ski.aws.dynamo import DynamoDataStore, stats as process_write_stats
from ski.aws.sqs import sqs_enrich_and_save_record, stats as load_write_stats
from ski.io.gpx import GPXSource
from ski.io.gsd import GSDSource, stats as reader_stats
from ski.io.track import TrackS3Loader
from ski.loader.cleanup import stats as cleanup_stats
from ski.loader.enrich import stats as enrich_stats
from ski.loader.dataloader import gpx_s3_to_sqs, gsd_s3_to_sqs, process_to_db


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def load_file_handler(event, context):
    # Script start time
    start = time.time()

    log.debug('Running lambda function: event=%s; context=%s', event, context)

    for record in event['Records']:
        key = unquote_plus(record['s3']['object']['key'])

        # Validate that we're looking at a track file
        if not key.endswith('.yaml'):
            log.warning('Ignoring non Track file')

        else:
            # Create track loader
            ldr = TrackS3Loader(key)
            track = ldr.get_track()

            # Get data file from track
            datafile = track.datafile
            log.info('Loading data from %s', datafile)

            # Determine source type
            if datafile.endswith('.gpx'):
                # Create GPX Source
                source = GPXSource(datafile)
                gpx_s3_to_sqs(source, track)

            elif datafile.endswith('.gsd'):
                # Create GPX Source
                source = GSDSource(datafile)
                gsd_s3_to_sqs(source, track)

            else:
                print('Unexpected data file format')

    # Script end time
    end = time.time()

    print('Execution completed in {:.2f} seconds'.format(end - start))

    total_time = sum([x['process_time'] for x in [reader_stats, cleanup_stats, load_write_stats]])
    duration = datetime(0, floor(total_time / 60), floor(total_time % 60), floor(total_time % 1))
    duration_str = duration.strftime('%Mm%Ss')

    print('                    process time ')
    print(' phase     points     (s)    (%) ')
    print('---------------------------------')
    print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('read', *calc_stats(reader_stats, total_time)))
    print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('cleanup', *calc_stats(cleanup_stats, total_time)))
    print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('write', *calc_stats(load_write_stats, total_time)))
    print('---------------------------------')
    print('               {:>10s}'.format(duration_str))


def process_data_handler(event, context):
    # Script start time
    start = time.time()

    log.debug('Running lambda function: event=%s; context=%s', event, context)

    # Create data store
    db = DynamoDataStore()

    for record in event['Records']:
        if 'body' in record:
            sqs_enrich_and_save_record(record, process_to_db, db)
        else:
            log.warning('Did not find body in Record')

    # Script end time
    end = time.time()

    print('Execution completed in {:.2f} seconds'.format(end - start))

    total_time = sum([x['process_time'] for x in [enrich_stats, process_write_stats]])
    duration = datetime(0, floor(total_time / 60), floor(total_time % 60), floor(total_time % 1))
    duration_str = duration.strftime('%Mm%Ss')

    print('                    process time ')
    print(' phase     points     (s)    (%) ')
    print('---------------------------------')
    print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('enrich', *calc_stats(enrich_stats, total_time)))
    print(' {:8s}  {:>6d}  {:>6.3f}  {:>4.1f}%'.format('write', *calc_stats(process_write_stats, total_time)))
    print('---------------------------------')
    print('               {:>10s}'.format(duration_str))
