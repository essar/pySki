"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import logging

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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

    # convert_coords = config['dataloader']['gps']['convert_coords']
    # Cartesian X & Y
    # if convert_coords:
    #   wgs = WGSCoordinate(track_point.lat, track_point.lon)
    #   utm = WGStoUTM(wgs)
    #   log.debug('wgs: %s', wgs)
    #   log.debug('utm: %s', utm)
    #   track_point.x = utm.x
    #   track_point.y = utm.y
    
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

