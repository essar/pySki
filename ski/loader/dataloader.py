"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import logging

from ski.config import config
from ski.data.commons import basic_to_extended_point
from ski.loader.cleanup import cleanup_points
from ski.loader.enrich import enrich_points, PointWindow, WindowKey

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

load_buffer_len = config['dataloader']['load_buffer']
load_extended = config['dataloader']['extended_points']

#################
# Adjust these parameters depending on what windows you want to add
window_keys = {
    WindowKey(PointWindow.FORWARD, 3): None,
    WindowKey(PointWindow.FORWARD, 30): None
}
head_length = 30
tail_length = 30
#################


def drain_window(window, db, track):
    """
    Drains the point window of any remaining points.
    @param window: the current point window.
    @param db: a db class providing the output data store.
    @param track: the track to store these points to.
    """

    # Set drain flag on window
    window.drain = True

    # Process remainder of the window
    enriched_points = enrich_points([], window, window_keys)

    # Save points to data store
    db.add_points_to_track(track, enriched_points)

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

    # Load points into buffer and convert to extended points
    points = loader.load_points()
    if points is None or len(points) == 0:
        return False

    ext_points = list(map(basic_to_extended_point, points))
    log.debug('[%s] load_points: %d extended points', track.track_id, len(ext_points))

    # Do clean up
    cleaned_points = cleanup_points(ext_points)
    log.debug('[%s] load_points: %d cleaned points', track.track_id, len(cleaned_points))

    # Do enrichment
    enriched_points = enrich_points(cleaned_points, window, window_keys)
    log.debug('[%s] load_points: %d enriched points', track.track_id, len(enriched_points))

    # Save points to data store
    db.add_points_to_track(track, enriched_points)

    log.info('%d extended points loaded to track %s', len(enriched_points), track.track_id)
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

    # Load all points from the loader, store in the database
    while load_points(loader, window, db, track):
        pass

    # Check if there are points left in the window
    if len(window.head) > 0:
        # Drain the window
        log.info('No more data available, draining window')
        drain_window(window, db, track)

    log.info('Load complete: %d points loaded for %s', db.insert_count, track.track_id)
