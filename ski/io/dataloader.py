"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import logging

from ski.io.cleanup import cleanup_points

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



def load_extended_points(loader, db, track):
  """
  Load a set of points from a loader object, clean these and store in the data store as part of a specified track.
  """

  buf = []
  buflen = 100 # TODO Move this to properties

  while len(buf) < buflen:
    # Set of points from the loader (single point for GPX, single section for GSD)
    points = loader.load_points()

    if points == None:
          # End of data
          log.debug('Reached end of data')
          break

    # Build up a local buffer before passing to clean up
    buf.extend(points)
    log.debug('Read %d points; buffered=%d', len(points), len(buf))

  # No points found so return
  if len(buf) == 0:
    return False

  # Do clean up
  cleaned = []
  cleanup_points(buf, output=cleaned)

  # Enrich points

  # Save points to data store
  db.add_points_to_track(track, cleaned)

  return True


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

    return True


def load_all_points(loader, db, track):
    """
    Iterate across all points held in a loader and store all points in the data store.
    
    Params:
      loader: a Loader class providing the input data.
      db: a db class providing the output data store.
      track: the track to store these points to.
    """
    while load_points_to_db(loader, db, track):
        pass

    log.info('Load complete: %d points loaded', db.insert_count)
