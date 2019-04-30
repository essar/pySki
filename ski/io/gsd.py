'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import logging

from ski.data.commons import BasicGPSPoint
from ski.data.coordinate import addSeconds, DMSCoordinate, DMStoWGS
from datetime import datetime
from decimal import Decimal

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



class GSDLoader:

	def __init__(self, data, batch_mode=False):
		# Store data reference
		self.data = data
		# Set up array and internal pointer
		self.lines = []
		self.linePtr = 0
		self.sections = []
		self.sectionPtr = 0
		self.batch_mode = batch_mode

	
	def load_data(self, f, section_offset, section_limit):
		# Load list of GSD sections from the file header
		load_gsd_header(f, sections=self.sections)
		log.info('%d GSD sections found', len(self.sections))

		if not self.batch_mode:
			# Set bounds on the number of sections to parse
			off = 0 if section_offset is None else min(section_offset, len(self.sections))
			lim = len(self.sections) if section_limit is None else off + section_limit

			# Load all sections (within bounds)
			for section in self.sections[off:lim]:
				load_gsd_section(f, section, self.lines)


	def load_point(self, limit=-1):
		# Get next line from file, return if no lines remain
		if self.linePtr < len(self.lines) and (limit < 0 or self.linePtr < limit):
			# Look up next line
			line = self.lines[self.linePtr]
			# Increment pointer
			self.linePtr += 1

		else:
			return None

		return parse_gsd_line(line)


	def load_points(self, section_limit=-1):
		# Create a new array
		points = []

		# Get next section from array, return if no sections remain
		if self.sectionPtr < len(self.sections) and (section_limit < 0 or self.sectionPtr < section_limit):
			# Get the next section
			section = self.sections[self.sectionPtr]
			log.debug('Loading GSD section %d (%s)', self.sectionPtr, section)
			# Increment pointer
			self.sectionPtr += 1
		else:
			return None

		# Load section data into array
		lines = []
		load_gsd_section(self.data, section, lines)

		# Get all lines in the section
		for line in lines:
			points.append(parse_gsd_line(line))

		log.info('Loaded GSD section %s (%d points)', section, len(points))

		# Return points array
		return points


	def load_sections(self, section_offset, section_limit):
		# Load list of GSD sections from the file header
		load_gsd_header(self.data, sections=self.sections)
		# Set bounds on the number of sections to parse
		off = 0 if section_offset is None else min(section_offset, len(self.sections))
		lim = len(self.sections) if section_limit is None else off + section_limit
		log.debug('%d GSD sections found; offset=%d, limit=%d', len(self.sections), off, lim)

		# Constrain section list according to offset and limit
		self.sections = self.sections[off:lim]
		log.info('Loaded %d GSD sections', len(self.sections))


class GSDFileLoader(GSDLoader):

	def __init__(self, gsd_file, batch_mode=False, section_offset=None, section_limit=None):
		super().__init__(gsd_file)

		log.info('Loading from local GSD file (%s)', gsd_file.name)
		self.load_sections(section_offset, section_limit)
		
		if not self.batch_mode:
			# Load all sections (within bounds) into lines array
			for section in self.sections:
				load_gsd_section(self.data, section, self.lines)


class GSDS3Loader(GSDLoader):

	def __init__(self, s3f, batch_mode=False, section_offset=None, section_limit=None):
		super().__init__(s3f.body)

		log.info('Loading from S3 GSD file (%s)', s3f)
		self.load_sections(section_offset, section_limit)

		if not self.batch_mode:
			# Load all sections (within bounds) into lines array
			for section in self.sections:
				load_gsd_section(self.data, section, self.lines)


def __get_alt(line):
	return __split_line(line)[5]


def __get_date(line):
	return __split_line(line)[3]


def __get_lat(line):
	return __split_line(line)[0]


def __get_lon(line):
	return __split_line(line)[1]


def __get_speed(line):
	return __split_line(line)[4]


def __get_time(line):
	return __split_line(line)[2]


def __next_section(f):
	for line in f:
		if line.startswith('['):
			return line.strip()
	return None


def __parse_gsd_coord(coord):

	# Convert to signed zero-padded 8 digit field
	coordStr = '{:+010d}'.format(int(coord))

	# Degrees is first 4 characters (includes sign)
	d = int(coordStr[:4])
	# Minute is remainder of string
	dm = float(coordStr[4:]) / 10000.0
	# Convert from decimal minutes to DMS
	dms = addSeconds(d, dm)
	log.debug('Coordinate: %s->%s->%s->%s', coord, coordStr, (d, dm), dms)

	return dms


def __parse_header_line(line):
	# Get line parts
	lParts = __split_line(line)
	return ((int(lParts[0].strip()), lParts[1].strip()))


def __parse_section_name(name):
	# Strip header characters if present
	if name.startswith('['): name = name[1:-1]

	# Parse into tuple
	nParts = name.split(',')
	if len(nParts) < 2: return name
	return (int(nParts[0].strip()), nParts[1].strip())


def __skip_to_section(f, name=None, section_id=0):
	while True:
		s = __next_section(f)
		if s is None: break
		# Search by section name
		if name is not None and s.strip() == '[{0}]'.format(name): return
		# Search by section ID
		if section_id > 0 and __parse_section_name(s.strip())[0] == section_id: return
    
	raise EOFError('Could not find section {0}'.format(name))


def __split_line(line):
	# Look for allocation marker
	ix = line.index('=')
	if ix < 0:
		return (0, [])

	# Get line parts and strip whitespace
	return list(map(lambda a: a.strip(), line[ix + 1:].split(',')))


def load_gsd_header(f, sections=[]):
	# Advance to TP section
	__skip_to_section(f, 'TP')
	for line in f:
		# Skip blank lines
		if len(line.strip()) == 0: continue
		# Stop once we reach the next header
		if line.startswith('['): break

		sections.append(__parse_header_line(line))


def load_gsd_section(f, section, lines=[]):
	# Reconstruct the section name
	si, sname = section
	section_name = '{:03d},{:s}'.format(si, sname)

	# Start at beginning of file
	f.seek(0)

	# Skip to section
	__skip_to_section(f, name=section_name)

	for line in f:
		# Stop at next section
		if line.startswith('['): break
		# Skip blank lines
		if len(line.strip()) == 0: continue
		# Add the cleaned-up line
		lines.append(line.strip())


def parse_gsd_line(line):
	if line is None:
		return None

	log.debug('Parsing line: %s', line)

	# Read data from GSD line
	gsd_lat = __get_lat(line)
	gsd_lon = __get_lon(line)
	gsd_dt  = __get_date(line)
	gsd_tm  = __get_time(line)
	gsd_alt = __get_alt(line)
	gsd_spd = __get_speed(line)
	log.debug('gsd: lat=%s; lon=%s; dt=%s; tm=%s; alt=%s; spd=%s', gsd_lat, gsd_lon, gsd_dt, gsd_tm, gsd_alt, gsd_spd)

	point = BasicGPSPoint()
	
	try:
		# GSD date and time in DDMMYYHHMMSS format
		dtStr = '{:06d}{:06d}'.format(int(gsd_dt), int(gsd_tm))
		dt = datetime.strptime(dtStr, '%d%m%y%H%M%S')
		log.debug('Date: %s, %s', dtStr, dt)
		# Convert to timestamp
		point.ts = int(dt.timestamp())

		# Parse latitude, first convert to DMS
		(latD, latM, latS) = __parse_gsd_coord(gsd_lat)

		# Parse longitude, first convert to DMS
		(lonD, lonM, lonS) = __parse_gsd_coord(gsd_lon)

		# Convert to WGS
		dms = DMSCoordinate(latD, latM, latS, lonD, lonM, lonS)
		log.debug('DMS: %s', dms)
		wgs = DMStoWGS(dms)
		log.debug('WGS: %s', wgs)

		# Latitude & Longitude
		point.lat = wgs.getLatitudeDegrees()
		point.lon = wgs.getLongitudeDegrees()

		# GSD altitude in 10^-5?!, convert from floating point to int
		point.alt = int(int(gsd_alt) / 10000)

		# GSD speed in m/h?
		point.spd = float(gsd_spd) / 100.0

	except ValueError as e:
		log.warning('Failed to parse GSD line: %s; %s', line, e)
		
	# Return data item
	return point