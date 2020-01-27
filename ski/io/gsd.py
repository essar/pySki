"""
  Module containing classes for loading GPS data from GSD files.
"""
import logging
import time

from codecs import decode
from ski.logging import increment_stat, log_point
from ski.data.commons import BasicGPSPoint
from ski.data.coordinate import add_seconds, DMSCoordinate, dms_to_wgs
from datetime import datetime

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}


class GSDSource:

    def __init__(self, url, section_offset=None, section_limit=None):

        self.url = url

        self.sections = []
        self.section_limit = section_limit
        self.section_offset = section_offset
        self.section_ptr = 0
        self.stream = None
        self.__next_section = None

        self.date = None
        self.index = {}

    def __repr__(self):
        return '<{0} url={1}; stream={2}; date={3}; index_entries={4}>'.format(type(self).__name__, self.url,
                                                                               self.stream, self.date, len(self.index))

    def __read_line_from_stream(self, skip_blanks=True):

        if self.stream is None:
            raise ValueError('Stream is not initialized')

        eof = False
        while not eof:
            line = self.stream.readline()
            if line is None or len(line) == 0:
                # Reached end of file
                eof = True
                continue

            line = line.strip()
            if skip_blanks and len(line) == 0:
                # Skip blank line
                continue

            return line

        return None

    def init_stream(self, stream):

        self.stream = stream

        # Load date and index
        read_gsd_date(self)
        read_gsd_index(self)

        increment_stat(stats, 'section_count', len(self.index))

    def load_points(self):

        # Start of phase
        start_time = time.time()

        # Prepare a new array
        points = []

        # Read the section number from next section line
        section_number = self.__next_section[0]
        for line in self.next_section_iter():
            parsed_point = parse_gps_line(section_number, *line)

            # Add the line to output
            points.append(parsed_point)

            # Write to pointlog
            log_point(parsed_point.ts, 'Point load from GSD', source=self.url, **parsed_point.values())

            # Read the section number from next section line
            section_number = self.__next_section[0]

        # End of phase
        end_time = time.time()
        process_time = end_time - start_time
        point_count = len(points) if points is not None else 0

        increment_stat(stats, 'process_time', process_time)
        increment_stat(stats, 'point_count', point_count)

        log.info('Phase complete %s', {
            'phase': 'load (GSD)',
            'point_count': point_count,
            'process_time': process_time
        })

        # Return points array
        return points

    def next_section_iter(self, expect_header=None, skip_to_header=False):

        # If expect header is provided, ensure we get that (or skip until we do)
        if expect_header is not None:
            if self.__next_section is not None:
                header_line = self.__next_section
                self.__next_section = None
            else:
                header_line = self.__read_line_from_stream()
            if not header_line.strip() == '[{0}]'.format(expect_header):
                log.warning('%s header expected but not found', expect_header)
                return False

        end_of_section = False
        while not end_of_section:
            # Read lines from the stream until we reach eof or end of section
            line = self.__read_line_from_stream()

            if line is None:
                # Reached end of file
                return

            if line.startswith('['):
                # Reached end of section
                # Save the header in case we need it next time
                self.__next_section = line
                return

            parsed_line = parse_gsd_line(line)
            if parsed_line is not None:
                yield parsed_line


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


def parse_gsd_line(line):

    if line is None:
        return None

    try:
        ix = line.index('=')

        # Get line no
        line_no = int(line[:ix])

        # Get line parts and strip whitespace
        parts = [a.strip() for a in line[ix + 1:].split(',')]

    except ValueError:
        log.warning('Missing allocation marker in GSD line')
        line_no = 0
        parts = None

    return line_no, parts


def read_gsd_date(source):
    # Skip until we reach the date section
    gsd_line = source.next_section_iter(expect_header='Date', skip_to_header=True).__next__()
    # Read the date
    source.date = gsd_line[1][0]


def read_gsd_index(source):
    # Read the TP section and load values into the index
    for gsd_line in source.next_section_iter(expect_header='TP'):
        # Read the index
        source.index[gsd_line[1][0]] = gsd_line[1][1]


def parse_gps_line(section_no, line_no, line_data):
    """Parse a line of GSD data for a GPS point."""
    if line_data is None:
        return None

    log.debug('parse_gsd_line: %s', line_data)

    if len(line_data) < 6:
        log.warning('Expected 6 fields in GSD section %d, line %d; received %d', section_no, line_no, len(line_data))
        return None

    # Read data from GSD line
    gsd_lat = line_data[0]
    gsd_lon = line_data[1]
    gsd_tm = line_data[2]
    gsd_dt = line_data[3]
    gsd_spd = line_data[4]
    gsd_alt = line_data[5]

    point = BasicGPSPoint()
    
    try:
        # GSD date and time in DDMMYYHHMMSS format
        dt_str = '{:06d}{:06d}'.format(int(gsd_dt), int(gsd_tm))
        dt = datetime.strptime(dt_str, '%d%m%y%H%M%S')
        log.debug('parse_gsd_line: date=%s; %s', dt_str, dt)
        # Convert to timestamp
        point.ts = int(dt.timestamp())

        # Parse latitude, first convert to DMS
        (latD, latM, latS) = __parse_gsd_coord(gsd_lat)

        # Parse longitude, first convert to DMS
        (lonD, lonM, lonS) = __parse_gsd_coord(gsd_lon)

        # Convert to WGS
        dms = DMSCoordinate(latD, latM, latS, lonD, lonM, lonS)
        wgs = dms_to_wgs(dms)
        log.debug('parse_gsd_line: DMS=%s; WGS=%s', dms, wgs)

        # Latitude & Longitude
        point.lat = wgs.get_latitude_degrees()
        point.lon = wgs.get_longitude_degrees()

        # GSD altitude in 10^-5?!, convert from floating point to int
        point.alt = int(int(gsd_alt) / 10000)

        # GSD speed in m/h?
        point.spd = float(gsd_spd) / 100.0

    except ValueError as e:
        log.warning('Failed to parse GPS data from GSD section %d,line %d: %s; %s', section_no, line_no, line_data, e)

    # Return data item
    return point


def parse_gsd(gsd_source, **kwargs):

    start_time = time.time()

    # Prepare a new array
    points = gsd_source.load_points()

    end_time = time.time()
    process_time = end_time - start_time
    point_count = len(points) if points is not None else 0

    increment_stat(stats, 'process_time', process_time)
    increment_stat(stats, 'point_count', point_count)

    log.info('Phase complete %s', {
        'phase': 'load (GSD)',
        'point_count': point_count,
        'process_time': process_time
    })

    # Return points array
    return points
