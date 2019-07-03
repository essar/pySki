"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import logging

from ski.config import config
from ski.io.cleanup import cleanup_points
from ski.io.enrich import enrich_points, PointWindow


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


load_buffer_len = config['dataloader']['load_buffer']
load_extended = config['dataloader']['extended_points']

windows = {
    'fwd3' : PointWindow(PointWindow.FORWARD, 3)
}
head_length = 0
tail_length = 3


def __array_replace(array, points):
    array.clear()
    array.extend(points)


def __load_to_buffer(loader, tail=[]):
    buf = []
    # Preload any points from the tail
    buf.extend(tail)
    log.debug('__load_to_buffer: %d points loaded into buffer from tail', len(buf))
    # Load a set of points into a buffer
    while len(buf) < load_buffer_len:
        # Set of points from the loader (single point for GPX, single section for GSD)
        points = loader.load_points()
        if points == None or len(points) == 0:
              # End of data
              log.debug('__load_to_buffer: Reached end of data')
              break

        # Build up a local buffer before passing to clean up
        buf.extend(points)
        log.debug('__load_to_buffer: loaded %d points; buf=%d; load_buffer_len=%d', len(points), len(buf), load_buffer_len)

    return buf


def __split_tail(points, tail_length=0):
    body_end = len(points) - tail_length
    return (points[0:body_end], points[body_end:])


def load_extended_points(loader, db, track, head=[], tail=[]):
    """
    Load a set of points from a loader object, clean these and store in the data store as part of a specified track.
    Params:
      loader: a Loader class providing the input data.
      db:     a db class providing the output data store.
      track:  the track to store these points to.
    
    Returns true if a point is added successfully, false if there are no more points to add.
    """
    # Load points into buffer
    buf = __load_to_buffer(loader, tail)
    #log.debug('buf=%s', buf)
    buffer_full = (len(buf) >= load_buffer_len)
    log.debug('Buffer is %s', 'full' if buffer_full else 'not full')

    # No points found so return
    if len(buf) == 0:
        return False

    # Do clean up
    cleaned = []
    cleanup_points(buf, output=cleaned)

    # Extract a new tail from the body; if the buffer isn't full use all the points
    (body, new_tail) = __split_tail(cleaned, tail_length if buffer_full else 0)
    log.debug('body=%d; head=%d; tail=%d', len(body), len(head), len(new_tail))

    # Do enrich
    enrich_points(cleaned, windows, head, new_tail)
    
    # Update the tail with remaining points
    __array_replace(tail, new_tail)
    
    # Save points to data store
    db.add_points_to_track(track, body)

    log.info('%d extended points loaded to track %s', len(body), track.track_id)
    return True


def load_basic_points(loader, db, track, head=[], tail=[]):
    return load_points_to_db(loader, db, track)


def load_points_to_db(loader, db, track):
    """
    Load a set of points from a loader object and store these in the data store as part of a specified track.

    Params:
      loader: a Loader class providing the input data.
      db: a db class providing the output data store.
      track: the track to store these points to.
    
    Returns true if a point is added successfully, false if there are no more points to add.
    """
    points = loader.load_points()
    
    if points == None:
        # End of data
        log.debug('Reached end of data')
        return False
    
    # Load point to data store
    db.add_points_to_track(track, points)

    log.info('%d basic points loaded to track %s', len(points), track.track_id)
    return True


def load_all_points(loader, db, track, extended=load_extended):
    """
    Iterate across all points held in a loader and store all points in the data store.
    
    Params:
      loader: a Loader class providing the input data.
      db: a db class providing the output data store.
      track: the track to store these points to.
    """
    tail = []

    if extended:
        load_f = load_extended_points
        log.info('Loading points in extended mode')
    else:
        load_f = load_basic_points
        log.info('Loading points in basic mode')

    while load_f(loader, db, track, tail=tail):
        log.debug('Remaining tail: %s', tail)
        pass

    log.info('Load complete: %d points loaded', db.insert_count)
