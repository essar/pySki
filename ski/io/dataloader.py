'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import logging

from datetime import datetime
from pytz import timezone
from ski.data.commons import BasicTrackPoint, Track
from ski.io.db import TestDataStore
from ski.io.gpx import GPXStringLoader
from ski.io.gsd import GSDFileLoader, GSDS3Loader

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def load_point_to_db(loader, db, track):

	point = loader.load_point()
	
	if point == None:
		# End of data
		log.debug('Reached end of data')
		return False

	#track_point = BasicTrackPoint(track_id='TEST', ts=point.ts, lat=point.lat, lon=point.lon, alt=point.alt, spd=point.spd)

	# convert_coords = config['dataloader']['gps']['convert_coords']
	# Cartesian X & Y
	# if convert_coords:
	#	wgs = WGSCoordinate(track_point.lat, track_point.lon)
	#	utm = WGStoUTM(wgs)
	#	log.debug('wgs: %s', wgs)
	#	log.debug('utm: %s', utm)
	#	track_point.x = utm.x
	#	track_point.y = utm.y
	
	# Load point to data store
	db.add_point_to_track(track, point)

	return True


def load_all_points(loader, db, track):
	while load_point_to_db(loader, db, track):
		pass

	log.info('Load complete: %d points loaded', db.count)



def tester():
	test_data = '<track><trkpt lat="51.0000" lon="01.0000"><time>2019-04-16T17:00:00Z</time><ele>149</ele><speed>4.5</speed></trkpt>\
				 <trkpt lat="51.2345" lon="-01.2345"><time>2019-04-16T17:00:05Z</time><ele>135</ele><speed>3.25</speed></trkpt></track>'
	log.debug('Testing data:\n%s', test_data)

	# Create loader
	#loader = GPXStringLoader(test_data)
	#loader = GSDFileLoader('tests/testdata.gsd', section_offset=15, section_limit=2)
	loader = GSDS3Loader('gsd/testdata.gsd', section_limit=3)

	# Create data store
	db = TestDataStore()

	# Create track
	tz = timezone('UTC')
	track = Track('abcdefg','TEST', datetime.now(tz))

	# Load points
	load_all_points(loader, db, track)


if __name__ == "__main__":
	# Execute tester
	tester()
