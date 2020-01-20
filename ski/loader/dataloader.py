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

from ski.config import config
from ski.logging import increment_stat
from ski.aws.dynamo import stats as write_stats
from ski.data.commons import basic_to_extended_point
from ski.io.gsd import load_gsd_points, stats as loader_stats
from ski.loader.cleanup import cleanup_points, stats as cleanup_stats
from ski.loader.enrich import enrich_points, stats as enrich_stats
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


def dummy_process_batch(track, body, tail, drain):
    log.info('Process batch of %d points, %d tail', len(body), len(tail))


def file_process_batch(track, body, tail, drain, batch_idx):

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


def direct_process_batch(body, tail, drain, db, batch_idx, track):

    # Prepare a window from points
    window = PointWindow(tail=tail, min_head_length=head_length)
    window.drain = drain

    # Load new batched points to the window
    window.load_points(body)
    log.debug('[batch=%03d] window: head=%d, tail=%d', batch_idx, len(window.head), len(window.tail))

    # Enrich the points
    enriched_points = enrich_points(window, window_keys)
    log.info('[batch=%03d] Enriched %d points', batch_idx, len(enriched_points))

    # Save points to data store
    db.add_points_to_track(track, enriched_points)
    log.info('[batch=%03d] Written %d points', batch_idx, db.insert_count)


def load_into_batch(source, batch, drain, parser_f, process_f, **kwargs):
    """
    Loads a set of points from a source object, clean these and send to a processor function.
    @param source: reference to data source object.
    @param batch: reference to the batch window.
    @param drain: flag to clear all points from the batch.
    @param parser_f: parsing function used for extracting data from the source.
    @param process_f: processor function.
    @param kwargs: dict of additional arguments passed to the parser and processor functions.
    @return: True if a point is loaded successfully, False if there are no more points to add.
    """

    # Load points from source
    points = parser_f(source, **kwargs)

    if points is not None:

        # Convert to extended points
        ext_points = list(map(basic_to_extended_point, points))

        # Do clean up
        cleaned_points = cleanup_points(ext_points)

    else:
        cleaned_points = None

    # Load points into the batch
    batch.load_points(cleaned_points, drain, process_f=process_f, **kwargs)

    return points is not None


def load_all_points(source, parser_f, process_f, **kwargs):
    """
    Iterates across app points in a source and batch load all points.
    @param source: reference to data source object.
    @param parser_f: parsing function.
    @param process_f: processor function.
    @param kwargs: dict of additional arguments passed to the parser and processor functions.
    """
    # Initialize a new batch
    batch = BatchWindow(batch_size=batch_size, overlap=tail_length)

    # Initialize a batch counter
    batch_count = 0

    # Load all points from the loader, store in the database
    while load_into_batch(source, batch, False, parser_f, process_f, batch_idx=batch_count, **kwargs):
        batch_count += 1

    # Call again to drain the buffer
    load_into_batch(source, batch, True, parser_f, process_f, batch_idx=batch_count, **kwargs)


def old_load_all_points(loader, db, track):
    """
    Iterates across all points held in a loader and store all points in the data store.
    @param loader: a Loader class providing the input data.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    """

    # Initialize a new batch
    batch = BatchWindow(batch_size=batch_size, overlap=tail_length)

    # Initialise a new point window
    window = PointWindow(min_head_length=head_length)

    # Initialize a batch counter
    batch_count = 0

    # Load all points from the loader, store in the database
    while load_points(loader, batch, db, track):
        batch_count += 1

    # Drain the window
    window.drain = True
    # Call to drain the buffer
    load_points(loader, batch, db, track, True)

    log.info('Load complete: %d points loaded for %s', db.insert_count, track.track_id)

    log.info('Load: %s', loader_stats)
    log.info('Clean up: %s', cleanup_stats)
    log.info('Enrich: %s', enrich_stats)
    log.info('Write: %s', write_stats)

    total_time = sum([x['process_time'] for x in [loader_stats, cleanup_stats, enrich_stats, write_stats]])

    log.info('Timings: load=%.3fs (%.1f%%), cleanup=%.3fs (%.1f%%), enrich=%.3fs (%.1f%%), write=%.3fs (%.1f%%)',
             loader_stats['process_time'], (loader_stats['process_time'] / total_time) * 100.0,
             cleanup_stats['process_time'], (cleanup_stats['process_time'] / total_time) * 100.0,
             enrich_stats['process_time'], (enrich_stats['process_time'] / total_time) * 100.0,
             write_stats['process_time'], (write_stats['process_time'] / total_time) * 100.0,
             )


def gsd_file_to_db(file, track, db):

    source = file
    parser_function = None
    loader_function = direct_process_batch

    load_all_points(source, track, parser_function, loader_function, db=db)


def s3_to_db(s3_file, track, db):

    source = s3_file
    parser_function = None
    loader_function = direct_process_batch

    load_all_points(source, track, parser_function, loader_function, db=db)
