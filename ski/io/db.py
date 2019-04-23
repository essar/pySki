'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import logging

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class DataStore:

	def add_point_to_track(self, track, point):
		return NotImplemented


class TestDataStore(DataStore):

	def __init__(self):
		self.count = 0
		log.info('[TestDataStore] Initialized TestDataStore')


	def add_point_to_track(self, track, point):
		self.count += 1
		key = "{:s}-{:d}".format(track.track_id, point.ts)
		log.info('[TestDataStore] Saving point to track %s: %s', track.track_id, point)
		log.debug('[TestDataStore] https://www.google.com/maps/@%f,%f,17z', point.lat, point.lon)
