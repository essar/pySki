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
from ski.loader.enrich import enrich_points, PointWindow, WindowKey

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


#################
# Adjust these parameters depending on what windows you want to add
window_keys = {
    WindowKey(PointWindow.FORWARD, 5): None,
    WindowKey(PointWindow.FORWARD, 30): None,
    WindowKey(PointWindow.BACKWARD, 5): None,
    WindowKey(PointWindow.BACKWARD, 30): None,
    WindowKey(PointWindow.MIDPOINT, 29): None
}
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


def drain_window(window, db, track):
    """
    Drains the point window of any remaining points.
    @param window: the current point window.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    """

    # Set drain flag on window
    window.drain = True

    start_time = time.time()

    # Process remainder of the window
    enriched_points = enrich_points([], window, window_keys)
    t.enrich_time += (time.time() - start_time)

    # Save points to data store
    db.add_points_to_track(track, enriched_points)
    t.write_time += (time.time() - start_time)

    log.info('%d extended points loaded to track %s', len(enriched_points), track.track_id)


def load_points(loader, window, db, track):
    """
    Loads a set of points from a loader object, clean these and store in the data store as part of a specified track.
    @param loader: a Loader class providing the input data.
    @param window: the current point window.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    @return true if a point is added successfully, false if there are no more points to add.
    """

    start_time = time.time()

    # Load points into buffer and convert to extended points
    points = loader.load_points()
    if points is None or len(points) == 0:
        return False

    t.load_time += time.time() - start_time

    ext_points = list(map(basic_to_extended_point, points))

    # Do clean up
    cleaned_points = cleanup_points(track, ext_points)
    t.clean_time += (time.time() - start_time)

    # Do enrichment
    enriched_points = enrich_points(cleaned_points, window, window_keys)
    t.enrich_time += (time.time() - start_time)

    if len(cleaned_points) != len(enriched_points):
        log.warning('[%s] Cleaned up %d points but enriched %d',
                    track.track_id, len(cleaned_points), len(enriched_points))

    # Save points to data store
    db.add_points_to_track(track, enriched_points)
    t.write_time += (time.time() - start_time)

    log_json(log, logging.INFO, track=track,
             ext_point=len(ext_points),
             cleaned_points=len(cleaned_points),
             enriched_points=len(enriched_points),
             inserted=db.insert_count)

    return True


def load_all_points(loader, db, track):
    """
    Iterates across all points held in a loader and store all points in the data store.
    @param loader: a Loader class providing the input data.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    """

    # Initialize a new point window
    window = PointWindow(head_length, tail_length)

    # Initialize a batch counter
    batch_count = 0

    # Load all points from the loader, store in the database
    while load_points(loader, window, db, track):
        batch_count += 1

    # Check if there are points left in the window
    if len(window.head) > 0:
        # Drain the window
        log.info('No more data available, draining window')
        drain_window(window, db, track)

    log.info('Load complete: %d points loaded for %s', db.insert_count, track.track_id)
    log.info('%s', t)
