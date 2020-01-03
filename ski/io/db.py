"""
  Module providing classes and functions that store data in a persistent data store or database. 
"""
import logging

from ski.data.commons import basic_to_extended_point

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
        log.info('[TestDataStore] %d point(s) to load', len(points))
        for point in points:
            key = "{:s}-{:d}".format(track.track_id, point.ts)
            self.points.append(point)
            self.insert_count += 1
            
            log.debug('[TestDataStore] Saving point to track %s: %s|%s', track.track_id, key, point)
            log.debug('[TestDataStore] https://www.google.com/maps/@%f,%f,17z', point.lat, point.lon)
        log.info('[TestDataStore] Inserted %d/%d', self.insert_count, len(points))

    def get_track_points(self, track, offset=0, length=-1):
        log.debug('[TestDataStore] Retrieving points track %s (%d to %d)', track.track_id, offset, length)
        return list(map(basic_to_extended_point, self.points[offset:length]))

    def save_extended_points(self, points):
        log.info('[TestDataStore] %d point(s) to load', len(points))
        for point in points:
            key = "{:s}-{:d}".format(point.track_id, point.ts)
            self.points.append(point)
            self.insert_count += 1
            
            log.info('[TestDataStore] Saving point: %s|%s', key, point)
            log.debug('[TestDataStore] Inserted %d/%d', self.insert_count, len(points))
