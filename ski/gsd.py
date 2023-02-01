"""
Handles processing of GSD format files.
"""
import datetime
import logging
from math import atan2, degrees, hypot
from .coordinate import DMSCoordinate, WGSCoordinate, add_seconds, DMS_to_WGS, WGS_to_UTM
from .utils import MovingWindow

log = logging.getLogger(__name__)


class GSDFile:
    """
    Class representing a local GSD file.
    """
    def __init__(self, file, load_header:str=True) -> None:
        """Instantiate a new class instance."""
        # Store file reference
        self.file = file
        # Set up array and internal pointer
        self.sections = []

        # Load the header unless flagged not to
        if load_header:
            self.load_gsd_header()


    def is_blank(line:str) -> bool:
        return len(str(line or '').strip()) == 0


    def is_eof(line:str) -> bool:
        return line is None or len(line) == 0


    def is_section_header(line:str) -> bool:
        return (line if type(line) is str else '').startswith('[')


    def parse_header_line(line:str) -> tuple:
        """
        Parse a header section line.
        e.g. `1=001,2018-02-15:16:16:55 -> (1,'2022-01-27T12:00:00')`
        """
        # Get line parts
        line_parts = GSDFile.__split_line(line or '')
        if len(line_parts) != 2:
            log.warn('parse_header_line: line does not look like a header line, did not contain 2 values')
            return None
        # Return as a tuple
        return int(line_parts[0]), line_parts[1]


    def parse_points_line(line:str) -> list:
        """
        Parse a points section line.
        e.g. `1=39531388,-105457814,161655,150218,180,27760000 -> ['39531388','-105457814','161655','150218','180', '27760000']`
        """
        # Get line parts
        line_parts = GSDFile.__split_line(line or '')
        if len(line_parts) < 6:
            log.warn('parse_points_line: line does not look like a points line, did not contain at least 6 values')
            return None
        # Return first 6 parts
        return line_parts[0:6]
        

    def parse_section_name(name:str) -> tuple:
        """
        Parse a section name.
          e.g. `[TP] -> (None, 'TP')`
          e.g. `[001,2018-02-15:16:16:55] -> (1, '2018-02-15:16:16:55')`
        """
        # Strip header characters if present
        name = (name or '').lstrip('[').rstrip(']')

        # Split around a comma separator
        name_parts = name.split(',')
        if len(name_parts) == 1:
            # Parse into tuple  and strip any whitespace
            return (None, name.strip() if len(name) > 0 else None)
        else:
            # Check first element is numeric
            if name_parts[0].isnumeric():
                # Convert first element to numeric and strip whitespace
                return (int(name_parts[0].strip()), name_parts[1].strip())
            else:
                log.warn('parse_section_name: section index is not a number')
                return (name_parts[0].strip(), name_parts[1].strip())


    def __next_section(self):
        """Move to the next section in the file and return the section name."""
        while True:
            line = self.file.readline()
            # Stop if data runs out
            if line is None:
                break

            log.debug('__next_section: read line %s', line)

            # Return the lineif it starts with a square bracket
            if GSDFile.is_section_header(line):
                log.debug('__next_section: at section %s', line)
                return line.strip()
        
        log.debug('__next_section: reached end of file')
        return None


    def __split_line(line:str) -> list:
        """
        Split a line around an '=' and ',' characters.
        Drop the leading counter and return the remaining values as a list of strings.
        eg: `001=1234567,2345678,123456,654321 -> ['123456','234567','123456','654321']`
        """
        # Look for allocation marker
        ix = line.find('=')

        # If no allocation marker found return an empty list
        if ix < 0:
            return []

        # Split the line around a comma separator and strip whitespace
        return [x.strip() for x in line[ix + 1:].split(',')]
    

    def load_gsd_header(self) -> None:
        """Load the header section from a GSD file."""

        # Start at beginning of file
        self.file.seek(0)

        # Advæance to TP section
        self.skip_to_section('TP')

        sections = []

        while True:
            line = self.file.readline()

            # Stop if data runs out
            if GSDFile.is_eof(line):
                log.debug('load_gsd_header: reached end of file')
                break

            # Skip blank lines
            if GSDFile.is_blank(line):
                continue
            
            # Stop once we reach the next header
            if GSDFile.is_section_header(line):
                log.debug('load_gsd_header: reached next section')
                break

            line = GSDFile.parse_header_line(line.strip())
            if line:
                log.debug('load_gsd_header: line=%s')
                sections.append(line)

        # Replace existing sections list
        self.sections = sections

        log.info('Loaded GSD header: %d section(s)', len(self.sections))


    def load_gsd_points(self, section_name:str=None) -> list:
        """Load points from the next or a named section. Each point is returned as an list of string values."""
        # If a section name is provided, skip to that section; otherwise read the next section
        if section_name:
            # Return to beginning of file
            self.file.seek(0)
            # Advance to named section
            self.skip_to_section(section_name=section_name)

        output = []

        while True:
            line = self.file.readline()

            # Stop if data runs out
            if GSDFile.is_eof(line):
                log.debug('load_gsd_points: reached end of file')
                break

            # Skip blank lines
            if GSDFile.is_blank(line):
                continue

            # Stop at next section
            if GSDFile.is_section_header(line):
                log.debug('load_gsd_points: reached next section')
                break

            # Add cleaned-up line to the output
            line = GSDFile.parse_points_line(line.strip())
            if line:
                log.debug('load_gsd_points: line=%s', line)
                output.append(line)

        log.info('Loaded %d point(s)', len(output))
        return output


    def skip_to_section(self, section_name:str=None, section_id:int=0) -> None:
        """Move to the named or indexed section in a GSD file."""
        while True:
            s = self.__next_section()

            # Stop if no section found
            if s is None:
                log.debug('skip_to_section: reached end of file')
                break

            log.debug('skip_to_section: reached section %s', s)

            # Search by section name
            if section_name is not None and s.strip() == f'[{section_name}]':
                log.debug('skip_to_section: reached section %s', section_name)
                return
            
            # Search by section ID
            if section_id > 0 and GSDFile.parse_section_name(s.strip())[0] == section_id:
                log.debug('skip_to_section: reached section %d', section_id)
                return
        
        raise EOFError(f'Could not find section {section_name or section_id}')



def convert_coords(point: dict) -> dict:
    wgs = WGSCoordinate(point['lat'], point['lon'])
    utm = WGS_to_UTM(wgs)
    #log.debug('wgs: %s', wgs)
    #log.debug('utm: %s', utm)
    point['x'] = utm.x
    point['y'] = utm.y
    #log.debug(f'x={utm.x}; y={utm.y}')

    return point


def convert_gsd_alt(gsd_alt:str):
    """Convert read GSD altitude into metres."""
    if not gsd_alt.isnumeric():
        log.warn('convert_gsd_coord: gsd_alt is not valid value: %s', gsd_alt)
        return 0

    try:
        alt = int(int(gsd_alt) / 10000)
        log.debug('convert_gsd_alt: %s -> %d', gsd_alt, alt)

    except ValueError:
        log.error('convert_gsd_alt: Unable to convert GSD string to altitude: %s', gsd_alt, exc_info=True)
        return 0

    return alt


def convert_gsd_coord(gsd_coord:str) -> tuple:
    """Convert read GSD coordinate into DMS tuple."""
    try:
        # Convert to signed zero-padded 10 digit field
        coord_str = f'{int(gsd_coord):10d}'

        # Degrees is first 5 characters (includes sign)
        d = int(coord_str[:5])
        # Minute is remainder of string
        dm = float(coord_str[5:]) / 1000.0
        # Convert from decimal minutes to DMS
        dms = add_seconds(d, dm)
        log.debug('convert_gsd_coord: % s-> %d -> %.4f -> %.4f', gsd_coord, coord_str, (d, dm), dms)

    except ValueError:
        log.error('convert_gsd_coord: Unable to convert GSD string to coordinate: %s', gsd_coord, exc_info=True)
        return None

    return dms


def convert_gsd_date(gsd_dt:str, gsd_tm:str) -> datetime.datetime:
    """Convert read GSD date and time strings into datetime object."""
    if not gsd_dt.isnumeric():
        log.warn('convert_gsd_coord: gsd_dt is not valid value: %s', gsd_dt)
        return None
    if not gsd_tm.isnumeric():
        log.warn('convert_gsd_coord: gsd_tm is not valid value: %s', gsd_tm)
        return None
    
    try:
        # GSD date and time in DDMMYYHHMMSS format
        dt_str = f'{int(gsd_dt):06d}{int(gsd_tm):06d}'    
        dt = datetime.datetime.strptime(dt_str, '%d%m%y%H%M%S')
        log.debug('convert_gsd_date: %s -> %s', dt_str, dt)

    except ValueError:
        log.warn('convert_gsd_date: Unable to convert GSD strings to date: %s %s', gsd_dt, gsd_tm, exc_info=True)
        return None
    
    return dt


def convert_gsd_speed(gsd_spd:str) -> float:
    """Convert read GSD speed into km/h."""
    if not gsd_spd.isnumeric():
        log.warn('convert_gsd_coord: gsd_spd is not a valid value: %s', gsd_spd)
        return 0

    try:
        spd = float(gsd_spd) / 100.0
        log.debug('convert_gsd_speed: %s -> %.3f', gsd_spd, spd)

    except ValueError:
        log.warning('convert_gsd_speed: Unable to convert GSD strings to speed: %s', gsd_spd, exc_info=True)
        return 0.0

    return spd


def stream_records(f) -> None:
    """Retrieve GPS records from the specified GSD file."""
    # Create GSDFile object; read the header
    gsd = GSDFile(f)

    point_count = 0
    section_count = 0

    #for s in gsd.sections:
    while True:
        try:
            points = gsd.load_gsd_points()
            if len(points) == 0:
                log.debug('stream_records: reached end of stream')
                break
            
            # Yield each point
            for p in points:
                yield p
                point_count += 1

            section_count += 1

        except EOFError:
            log.warn('Did not find section %s; skipping', 'x')

    log.info('Returned %d point(s) from %d section(s)', point_count, section_count)
    return None



def convert_gsd_to_data_point(gsd_line:list) -> dict:
    if gsd_line is None:
        return None

    # GSD line should be a list of 6 strs
    if len(gsd_line) != 6:
        raise ValueError('Not a valid gsd_line provided')

    # Read data from GSD line
    gsd_lat = gsd_line[0]
    gsd_lon = gsd_line[1]
    gsd_dt  = gsd_line[3]
    gsd_tm  = gsd_line[2]
    gsd_alt = gsd_line[5]
    gsd_spd = gsd_line[4]
    print(f'GSD: lat={gsd_lat}; lon={gsd_lon}; dt={gsd_dt}; tm={gsd_tm}; alt={gsd_alt}; spd={gsd_spd}')

    point = {}

    try:
        # Convert GSD date and time strings to UTC timestamp?
        point['dt'] = convert_gsd_date(gsd_dt, gsd_tm)
        point['ts'] = int(point['dt'].timestamp())
        
        # Convert GSD coordinate to DMS
        dms = DMSCoordinate(*convert_gsd_coord(gsd_lat), *convert_gsd_coord(gsd_lon))
        #log.debug('DMS: %s', dms)
        # Then convert to WGS
        wgs = DMS_to_WGS(dms)
        #log.debug('WGS: %s', wgs)

        # Latitude & Longitude
        point['lat'] = wgs.get_latitude_degrees()
        point['lon'] = wgs.get_longitude_degrees()

        # GSD altitude in 10^-5?!, convert from floating point to int
        point['alt'] = int(int(gsd_alt) / 10000)

        # GSD speed in m/h?
        point['spd'] = float(gsd_spd) / 100.0

    except ValueError as e:
        #log.warning('Failed to parse GSD line: %s; %s', line, e)
        print(f'Failed to parse GSD line: {e}')
        
    # Return data item
    return point


if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.INFO)

    with open('data/20180215.gsd', 'r') as f:
        result = stream_records(f)
        list(result)

        #print(list(result))
