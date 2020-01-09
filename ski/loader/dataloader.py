"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import logging
import time

from ski.logging import log_json
from ski.data.commons import basic_to_extended_point
from ski.loader.cleanup import cleanup_points
from ski.loader.enrich import enrich_points
from ski.loader.window import BatchWindow, PointWindow, WindowKey

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


#################
# Adjust these parameters depending on what windows you want to add
window_keys = {
    WindowKey(WindowKey.FORWARD, 5): None,
    WindowKey(WindowKey.FORWARD, 30): None,
    WindowKey(WindowKey.BACKWARD, 5): None,
    WindowKey(WindowKey.BACKWARD, 30): None,
    WindowKey(WindowKey.MIDPOINT, 29): None
}
batch_size = 180
head_length = 30
tail_length = 30
#################


class Timings:

    def __init__(self):
        self.load_time = 0.0
        self.clean_time = 0.0
        self.enrich_time = 0.0
        self.write_time = 0.0

    def __repr__(self):
        return {
            'load': self.load_time,
            'clean': (self.clean_time - self.load_time),
            'enrich': (self.enrich_time - self.clean_time),
            'write': (self.write_time - self.enrich_time)
        }

    def __str__(self):
        return 'load={:.3f}s ({:.1f}%), clean={:.3f}s ({:.1f}%), enrich={:.3f}s ({:.1f}%), write={:.3f}s ({:.1f}%)'.format(
            self.load_time,
            (self.load_time / self.write_time) * 100.0,
            (self.clean_time - self.load_time),
            ((self.clean_time - self.load_time) / self.write_time) * 100.0,
            (self.enrich_time - self.clean_time),
            ((self.enrich_time - self.clean_time) / self.write_time) * 100.0,
            (self.write_time - self.enrich_time),
            ((self.write_time - self.enrich_time) / self.write_time) * 100.0
        )


t = Timings()
start_time = time.time()


def dummy_process_batch(body, tail):
    log.info('Process batch of %d points, %d tail', len(body), len(tail))


def direct_process_batch(body, tail, window, db, track):

    # Load new batched points to the window
    window.load_points(body)
    log.debug('window: head=%d, tail=%d', len(window.head), len(window.tail))

    # Enrich the points
    enriched_points = enrich_points(window, window_keys)
    t.enrich_time += (time.time() - start_time)
    log.info('Enriched %d points', len(enriched_points))

    # Save points to data store
    db.add_points_to_track(track, enriched_points)
    t.write_time += (time.time() - start_time)
    log.info('Written %d points', db.insert_count)


def load_points(loader, batch, window, db, track):
    """
    Loads a set of points from a loader object, clean these and store in the data store as part of a specified track.
    @param loader: a Loader class providing the input data.
    @param batch: reference to the batch handler.
    @param window: a point window for generating enrichment values.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    @return true if a point is added successfully, false if there are no more points to add.
    """
    # Load points from loader
    points = loader.load_points()

    if points is not None:
        t.load_time += time.time() - start_time

        # Convert to extended points
        ext_points = list(map(basic_to_extended_point, points))

        # Do clean up
        cleaned_points = cleanup_points(track, ext_points)
        t.clean_time += (time.time() - start_time)

    else:
        cleaned_points = None

    # Load points into the batch
    batch.load_points(cleaned_points, direct_process_batch, window=window, db=db, track=track)

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
    while load_points(loader, batch, window, db, track):
        batch_count += 1

    # Drain the window
    window.drain = True
    # Call to drain the buffer
    load_points(loader, batch, window, db, track)

    log.info('Load complete: %d points loaded for %s', db.insert_count, track.track_id)
    log.info('%s', t)
