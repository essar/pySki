"""
  Module containing functions for loading GPS data from a variety of sources and storing
  this in a backend data store such as a database.

  Supported data formats: GSD, GPX
  Supported source tyoes: String, local file, S3 file
  Supported data stores: AWS Dynamo
"""
import logging

from datetime import datetime
from pytz import timezone
from ski.aws.dynamo import DynamoDataStore
from ski.aws.s3 import S3File
from ski.data.commons import Track
from ski.io.db import TestDataStore
from ski.io.gpx import GPXStringLoader
from ski.io.gsd import GSDFileLoader, GSDS3Loader

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



def load_from_file(db, track):
    """
    Test funtion: load data from a local GSD file.
    """
    # Create loader
    with open('tests/testdata.gsd', mode='r') as f:
        loader = GSDFileLoader(f, section_limit=1)
        
        # Load points
        load_all_points(loader, db, track)


def load_from_s3(db, track):
    """
    Test funtion: load data from an S3 GSD file.
    """
    s3f = S3File('gsd/testdata.gsd', True)
    loader = GSDS3Loader(s3f, section_limit=1)

    # Load points
    load_all_points(loader, db, track)


def load_from_string(db, track):
    """
    Test funtion: load data from a GPX string.
    """
    test_data = '<track><trkpt lat="51.0000" lon="01.0000"><time>2019-04-16T17:00:00Z</time><ele>149</ele><speed>4.5</speed></trkpt>\
                 <trkpt lat="51.2345" lon="-01.2345"><time>2019-04-16T17:00:05Z</time><ele>135</ele><speed>3.25</speed></trkpt></track>'
    log.debug('Testing data:\n%s', test_data)

    loader = GPXStringLoader(test_data)

    # Create data store
    db = TestDataStore()

    # Load points
    load_all_points(loader, db, track)
    

def tester():
    """
    Test funtion: load data from a local GSD file.
    """
    # Create data store
    db = DynamoDataStore()

    # Create track
    tz = timezone('UTC')
    track = Track('abcdefg','TEST', datetime.now(tz))

    #load_from_string(db, track)
    load_from_file(db, track)


if __name__ == "__main__":
    # Initialise logger
    logging.basicConfig()
    # Execute tester
    tester()
