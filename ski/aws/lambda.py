"""
  Module providing functions for working with AWS DynamoDB.
"""
import logging

from urllib.parse import unquote_plus
from ski.aws.dynamo import DynamoDataStore
from ski.aws.sqs import sqs_enrich_and_save_record
from ski.io.gpx import GPXSource, parse_gpx
from ski.io.gsd import GSDSource, parse_gsd
from ski.io.track import TrackS3Loader
from ski.loader.dataloader import s3_to_sqs, process_to_db


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Create data store
db = DynamoDataStore()


def load_file_handler(event, context):

    log.debug('Running lambda function: event=%s; context=%s', event, context)

    for record in event['Records']:
        key = unquote_plus(record['s3']['object']['key'])

        # Validate that we're looking at a track file
        if not key.startswith('track_') or key.endswith('.yaml'):
            log.error('%s does not appear to be a Track file; ignoring.', key)

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
                s3_to_sqs(source, parse_gpx, track)

            elif datafile.endswith('.gsd'):
                # Create GPX Source
                source = GSDSource(datafile)
                s3_to_sqs(source, parse_gsd, track)

            else:
                log.error('Unexpected data file format')


def process_data_handler(event, context):

    log.debug('Running lambda function: event=%s; context=%s', event, context)

    for record in event['Records']:
        if 'body' in record:
            sqs_enrich_and_save_record(record, process_to_db, db)
        else:
            log.error('Did not find body in Record')
