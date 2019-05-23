"""
  Module providing classes and functions that store data in a persistent data store or database. 
"""
import logging

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class DataStore:
    """Represents a generic data store."""
    def add_points_to_track(self, track, points):
        """
        Add a list of GPS points to the data store, associating them with the specified track.

        Params:
          track: the track to add points to.
          points: list of points to add.

        """
        raise NotImplementedError


class TestDataStore(DataStore):
    """Internal in-memory data store used for test purposes."""
    def __init__(self):
        self.points = []
        self.insert_count = 0
        log.info('[TestDataStore] Initialized TestDataStore')


    def add_points_to_track(self, track, points):
        for point in points:
            key = "{:s}-{:d}".format(track.track_id, point.ts)
            points.append(point)
            self.insert_count += 1

            log.info('[TestDataStore] Saving point to track %s: %s', track.track_id, point)
            log.debug('[TestDataStore] https://www.google.com/maps/@%f,%f,17z', point.lat, point.lon)


    def get_track_points(self, track, offset=0, length=-1):
        log.debug('[TestDataStore] Retriving points %d to %d', offset, length)
        return points[offset:length]