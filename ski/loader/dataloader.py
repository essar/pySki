"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import json
import logging
import time

from contextlib import closing
from ski.config import config
from ski.logging import increment_stat
from ski.aws.s3 import load_source_from_s3
from ski.aws.sqs import process_to_sqs
from ski.data.commons import basic_to_extended_point
from ski.loader.cleanup import cleanup_points
from ski.loader.enrich import enrich_points
from ski.loader.window import BatchWindow, PointWindow, WindowKey

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

direct_write_stats = {}

#################
# Adjust these parameters depending on what windows you want to add
window_keys = {
    WindowKey(WindowKey.FORWARD, 5): None,
    WindowKey(WindowKey.FORWARD, 30): None,
    WindowKey(WindowKey.BACKWARD, 5): None,
    WindowKey(WindowKey.BACKWARD, 30): None,
    WindowKey(WindowKey.MIDPOINT, 29): None
}
batch_size = config['dataloader']['batch_size']
head_length = 30
tail_length = 30

#################


def dummy_process_batch(body, tail, drain):
    log.info('Process batch of %d points, %d tail', len(body), len(tail))


def direct_process_batch(body, tail, drain, db, batch_idx, track):

    # Prepare a window from points
    window = PointWindow(tail=tail, min_head_length=head_length)
    window.drain = drain

    # Load new batched points to the window
    window.load_points(body)
    log.debug('[batch=%03d] window: head=%d, tail=%d', batch_idx, len(window.head), len(window.tail))

    # Enrich the points
    enriched_points = enrich_points(window, window_keys)
    log.debug('[batch=%03d] Enriched %d points', batch_idx, len(enriched_points))

    # Save points to data store
    db.add_points_to_track(track, enriched_points)
    log.debug('[batch=%03d] Written %d points', batch_idx, db.insert_count)


def process_to_db(body, tail, drain, db, **kwargs):

    enrich_and_save(body, tail, drain, enrich_points, db.add_points_to_track, **kwargs)


def process_to_file(body, tail, drain, batch_idx, track):

    start_time = time.time()

    file = 'tests/batch_output/{:04d}.json'.format(batch_idx)
    with open(file, 'w') as f:
        json.dump({
            'batch': batch_idx,
            'track': track.values(),
            'body': list(map(lambda x: x.values(), body)),
            'tail': list(map(lambda x: x.values(), tail))
        }, f)

    end_time = time.time()
    increment_stat(direct_write_stats, 'process_time', (end_time - start_time))
    increment_stat(direct_write_stats, 'point_count', len(body))
    increment_stat(direct_write_stats, 'file_count', 1)


def enrich_and_save(body, tail, drain, enrich_f, save_f, **kwargs):

    # Prepare a window from tail
    window = PointWindow(tail=tail, min_head_length=head_length)
    window.drain = drain

    # Load points to the window
    window.load_points(body)
    log.debug('enrich_and_save: window=%s', window)

    # Enrich the points
    enriched_points = enrich_f(window, window_keys)

    # Save points to data store
    save_f(enriched_points, **kwargs)


def load_source_from_file(source):

    # Get the file
    f = open(source.url)

    # Init the source
    source.init_stream(f)

    # Return the stream so it can be managed
    return f


def load_into_batch(source, batch, drain, process_f, **kwargs):
    """
    Loads a set of points from a source object, clean these and send to a processor function.
    @param source: reference to data source object.
    @param batch: reference to the batch window.
    @param drain: flag to clear all points from the batch.
    @param process_f: processor function.
    @param kwargs: dict of additional arguments passed to the parser and processor functions.
    @return: True if a point is loaded successfully, False if there are no more points to add.
    """

    # Load points from source
    # points = parser_f(source, **kwargs)
    points = source.parse_points(**kwargs)

    if points is not None and len(points) > 0:

        # Convert to extended points
        ext_points = list(map(basic_to_extended_point, points))

        # Do clean up
        cleaned_points = cleanup_points(ext_points)

    else:
        cleaned_points = None

    # Load points into the batch
    batch.load_points(cleaned_points, drain, process_f=process_f, **kwargs)

    return points is not None and len(points) > 0


def load_all_points(source, process_f, **kwargs):
    """
    Iterates across app points in a source and batch load all points.
    @param source: reference to data source object.
    @param process_f: processor function.
    @param kwargs: dict of additional arguments passed to the parser and processor functions.
    """
    # Initialize a new batch
    batch = BatchWindow(batch_size=batch_size, overlap=tail_length)

    # Initialize a batch counter
    batch_count = 0

    # Load all points from the loader, store in the database
    while load_into_batch(source, batch, False, process_f, batch_idx=batch_count, **kwargs):
        batch_count += 1

    # Call again to drain the buffer
    load_into_batch(source, batch, True, process_f, batch_idx=batch_count, **kwargs)


def file_to_db(source, track, db):

    with closing(load_source_from_file(source)):
        load_all_points(source, process_to_db, db=db, track=track)


def file_to_directory(source, track):

    with closing(load_source_from_file(source)):
        load_all_points(source, process_to_file, track=track)


def file_to_sqs(source, track):

    with closing(load_source_from_file(source)):
        load_all_points(source, process_to_sqs, track=track)


def s3_to_directory(source, track):

    with closing(load_source_from_s3(source)):
        load_all_points(source, process_to_file, track=track)


def s3_to_sqs(source, track):

    with closing(load_source_from_s3(source)):
        load_all_points(source, process_to_sqs, track=track)
