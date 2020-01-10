"""
  Module containing classes for loading GPS data from GSD files.
"""
import logging
import time

from ski.aws.s3 import S3File
from ski.logging import increment_stat
from ski.data.commons import BasicGPSPoint
from ski.data.coordinate import add_seconds, DMSCoordinate, dms_to_wgs
from datetime import datetime

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}


class GSDLoader:
    """
    Load GSD formatted data.
    """
    def __init__(self, data):
        # Store data reference
        self.data = data
        # Set up array and internal pointer
        self.sections = []
        self.sectionPtr = 0

    """
    Load an array of points from the GSD file. Will always return a single section (up to 64 points).
    """
    def load_points(self):
        """Load all the GPS points from a GSD section."""

        start_time = time.time()

        # Prepare a new array
        points = []

        # Get next section from array, return if no sections remain
        if self.sectionPtr < len(self.sections):
            # Get the next section
            section = self.sections[self.sectionPtr]
            # Increment pointer
            self.sectionPtr += 1
        else:
            log.info('load_points: reached section %d; end of data', self.sectionPtr)
            return None

        # Load section data into array
        lines = []
        load_gsd_section(self.data, section, lines)

        # Get all lines in the section
        for line in lines:
            points.append(parse_gsd_line(line))

        log.info('load_points: loaded %d points from section %s', len(points), section)

        end_time = time.time()
        increment_stat(stats, 'process_time', (end_time - start_time))
        increment_stat(stats, 'point_count', len(points))

        # Return points array
        return points

    def load_sections(self, section_offset, section_limit):
        """
        Load the list of GPS sections from the file header, optionally limiting as specified.
        
        Params:
          section_offset: skip the first number of sections.
          section_limit: only load the number of sections.
        """
        # Load the GSD header
        load_gsd_header(self.data, sections=self.sections)

        # Set bounds on the number of sections to parse
        off = 0 if section_offset is None else min(section_offset, len(self.sections))
        lim = len(self.sections) if section_limit is None else off + section_limit
        log.debug('load_sections: %d GSD sections in file; loading sections %d to %d',
                  len(self.sections), off, (lim - off))

        # Constrain section list according to offset and limit
        self.sections = self.sections[off:lim]
        log.info('load_sections: loaded %d GSD sections', len(self.sections))

        increment_stat(stats, 'section_count', len(self.sections))


class GSDFileLoader(GSDLoader):
    """Load GSD data from a local file."""
    def __init__(self, gsd_file, section_offset=None, section_limit=None):
        super().__init__(gsd_file)

        log.info('Loading GSD data from local file (%s)', gsd_file.name)
        self.load_sections(section_offset, section_limit)

    @staticmethod
    def get_stats():
        return stats


class GSDS3Loader(GSDLoader):
    """Load GSD data from a resource on S3."""
    def __init__(self, s3_file, section_offset=None, section_limit=None):
        if type(s3_file) != S3File:
            raise TypeError('s3_file parameter must be an S3File')

        super().__init__(s3_file.body)

        log.info('Loading GSD data from S3 (%s)', s3_file)
        self.load_sections(section_offset, section_limit)


def __get_alt(line):
    return split_line(line)[5]


def __get_date(line):
    return split_line(line)[3]


def __get_lat(line):
    return split_line(line)[0]


def __get_lon(line):
    return split_line(line)[1]


def __get_speed(line):
    return split_line(line)[4]


def __get_time(line):
    return split_line(line)[2]


def __next_section(f):
    for line in f:
        if line.startswith('['):
            return line.strip()
    return None


def __parse_gsd_coord(coord):
    # Convert to signed zero-padded 8 digit field
    coord_str = '{:+010d}'.format(int(coord))

    # Degrees is first 4 characters (includes sign)
    d = int(coord_str[:4])
    # Minute is remainder of string
    dm = float(coord_str[4:]) / 10000.0
    # Convert from decimal minutes to DMS
    dms = add_seconds(d, dm)
    log.debug('Coordinate: %s->%s->%s->%s', coord, coord_str, (d, dm), dms)

    return dms


def __parse_header_line(line):
    # Get line parts
    line_parts = split_line(line)
    return int(line_parts[0].strip()), line_parts[1].strip()


def __parse_section_name(name):
    # Strip header characters if present
    if name.startswith('['):
        name = name[1:-1]

    # Parse into tuple
    name_parts = name.split(',')
    if len(name_parts) < 2:
        return name
    return int(name_parts[0].strip()), name_parts[1].strip()


def __skip_to_section(f, name=None, section_id=0):
    """Skip to a named/numbered section in a GSD file"""
    section_found = False
    while not section_found:
        s = __next_section(f)
        if s is None:
            raise EOFError('Could not find section {0}'.format(name))
        # Search by section name
        if name is not None:
            section_found = (s.strip() == '[{0}]'.format(name))
        # Search by section ID
        if section_id > 0:
            section_found = (__parse_section_name(s.strip())[0] == section_id)


def load_gsd_header(f, sections=None):
    """Load the header from a GSD file."""
    if sections is None:
        sections = []
    # Advance to TP section
    __skip_to_section(f, 'TP')
    for line in f:
        # Skip blank lines
        if len(line.strip()) == 0:
            continue
        # Stop once we reach the next header
        if line.startswith('['):
            break

        sections.append(__parse_header_line(line))


def load_gsd_section(f, section, lines=None):
    """Load a section from a GSD file."""
    if lines is None:
        lines = []
    # Reconstruct the section name
    s_idx, s_name = section
    section_name = '{:03d},{:s}'.format(s_idx, s_name)

    # Start at beginning of file
    f.seek(0)

    # Skip to section
    __skip_to_section(f, name=section_name)

    for line in f:
        # Stop at next section
        if line.startswith('['):
            break
        # Skip blank lines
        if len(line.strip()) == 0:
            continue
        # Add the cleaned-up line
        lines.append(line.strip())


def parse_gsd_line(line):
    """Parse a line of GSD data for a GPS point."""
    if line is None:
        return None

    log.debug('Parsing line: %s', line)

    # Read data from GSD line
    gsd_lat = __get_lat(line)
    gsd_lon = __get_lon(line)
    gsd_dt = __get_date(line)
    gsd_tm = __get_time(line)
    gsd_alt = __get_alt(line)
    gsd_spd = __get_speed(line)
    log.debug('GSD: lat=%s; lon=%s; dt=%s; tm=%s; alt=%s; spd=%s', gsd_lat, gsd_lon, gsd_dt, gsd_tm, gsd_alt, gsd_spd)

    point = BasicGPSPoint()
    
    try:
        # GSD date and time in DDMMYYHHMMSS format
        dt_str = '{:06d}{:06d}'.format(int(gsd_dt), int(gsd_tm))
        dt = datetime.strptime(dt_str, '%d%m%y%H%M%S')
        log.debug('Date: %s, %s', dt_str, dt)
        # Convert to timestamp
        point.ts = int(dt.timestamp())

        # Parse latitude, first convert to DMS
        (latD, latM, latS) = __parse_gsd_coord(gsd_lat)

        # Parse longitude, first convert to DMS
        (lonD, lonM, lonS) = __parse_gsd_coord(gsd_lon)

        # Convert to WGS
        dms = DMSCoordinate(latD, latM, latS, lonD, lonM, lonS)
        log.debug('DMS: %s', dms)
        wgs = dms_to_wgs(dms)
        log.debug('WGS: %s', wgs)

        # Latitude & Longitude
        point.lat = wgs.get_latitude_degrees()
        point.lon = wgs.get_longitude_degrees()

        # GSD altitude in 10^-5?!, convert from floating point to int
        point.alt = int(int(gsd_alt) / 10000)

        # GSD speed in m/h?
        point.spd = float(gsd_spd) / 100.0

    except ValueError as e:
        log.warning('Failed to parse GSD line: %s; %s', line, e)
        
    # Return data item
    return point


def split_line(line, as_header=False):
    """Extract the section number and section data from a GSD line."""
    # Look for allocation marker
    try:
        ix = line.index('=')
        # Get line parts and strip whitespace
        parts = [a.strip() for a in line[ix + 1:].split(',')]

    except ValueError:
        log.warning('Missing allocation marker in GSD line')
        parts = []

    if as_header:
        # Headers should have 2 parts
        if len(parts) < 2:
            log.warning('Unexpected number of data parts in GSD header line')
            # Ensure that we return 2 parts, pad with zeros
            return [parts[i] if len(parts) > i else 0 for i in range(0, 2)]

        return parts[0:2]

    else:
        # Data lines have 6 parts
        if len(parts) < 6:
            log.warning('Unexpected number of data parts in GSD data line')
            # Ensure that we return 6 parts, pad with zeros
            return [parts[i] if len(parts) > i else 0 for i in range(0, 6)]

        return parts[0:6]
