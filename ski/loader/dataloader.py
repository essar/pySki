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

from ski.logging import log_json
from ski.config import config
from ski.logging import increment_stat
from ski.aws.dynamo import stats as write_stats
from ski.data.commons import basic_to_extended_point
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


def dummy_process_batch(batch_idx, body, tail, drain):
    log.info('Process batch of %d points, %d tail', len(body), len(tail))


def file_process_batch(batch_idx, body, tail, drain, track):

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


def direct_process_batch(batch_idx, body, tail, drain, db, track):

    # Prepare a window from points
    window = PointWindow(tail=tail, min_head_length=head_length)
    window.drain = drain
    window.load_points(body)


    # Load new batched points to the window
    #window.load_points(body)
    log.debug('[batch=%03d] window: head=%d, tail=%d', batch_idx, len(window.head), len(window.tail))

    # Enrich the points
    enriched_points = enrich_points(window, window_keys)
    log.info('[batch=%03d] Enriched %d points', batch_idx, len(enriched_points))

    # Save points to data store
    db.add_points_to_track(track, enriched_points)
    log.info('[batch=%03d] Written %d points', batch_idx, db.insert_count)


def load_points(loader, batch, db, track, drain=False):
    """
    Loads a set of points from a loader object, clean these and store in the data store as part of a specified track.
    @param loader: a Loader class providing the input data.
    @param batch: reference to the batch handler.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    @return true if a point is added successfully, false if there are no more points to add.
    """
    # Load points from loader
    points = loader.load_points()

    if points is not None:

        # Convert to extended points
        ext_points = list(map(basic_to_extended_point, points))

        # Do clean up
        cleaned_points = cleanup_points(track, ext_points)

    else:
        cleaned_points = None

    # Load points into the batch
    batch.load_points(cleaned_points, drain=drain, process_f=direct_process_batch, db=db, track=track)
    #batch.load_points(cleaned_points, drain=drain, process_f=file_process_batch, track=track)

    return points is not None


def load_all_points(loader, db, track):
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

    loader_stats = loader.get_stats()

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
