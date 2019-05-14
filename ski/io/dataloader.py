'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

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
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def load_points_to_db(loader, db, track):

	points = loader.load_points()
	
	if points == None:
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
	db.add_points_to_track(track, points)

	return True


def load_all_points(loader, db, track):
	while load_points_to_db(loader, db, track):
		pass

	log.info('Load complete: %d points loaded', db.insert_count)



def load_from_file(db, track):
	# Create loader
	with open('tests/testdata.gsd', mode='r') as f:
		loader = GSDFileLoader(f, section_limit=1)
		
		# Load points
		load_all_points(loader, db, track)


def load_from_s3(db, track):
	s3f = S3File('gsd/testdata.gsd', True)
	loader = GSDS3Loader(s3f, section_limit=1)

	# Load points
	load_all_points(loader, db, track)


def load_from_string(db, track):
	test_data = '<track><trkpt lat="51.0000" lon="01.0000"><time>2019-04-16T17:00:00Z</time><ele>149</ele><speed>4.5</speed></trkpt>\
				 <trkpt lat="51.2345" lon="-01.2345"><time>2019-04-16T17:00:05Z</time><ele>135</ele><speed>3.25</speed></trkpt></track>'
	log.debug('Testing data:\n%s', test_data)

	loader = GPXStringLoader(test_data)

	# Create data store
	db = TestDataStore()

	# Load points
	load_all_points(loader, db, track)
	

def tester():
	# Create data store
	db = DynamoDataStore()

	# Create track
	tz = timezone('UTC')
	track = Track('abcdefg','TEST', datetime.now(tz))

	load_from_string(db, track)
	#load_from_file(db, track)


if __name__ == "__main__":
	# Execute tester
	tester()
