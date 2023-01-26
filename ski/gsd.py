import datetime
from math import atan2, degrees, hypot
from .coordinate import DMSCoordinate, WGSCoordinate, add_seconds, DMS_to_WGS, WGS_to_UTM
from .utils import MovingWindow


class GSDFile:

    def __init__(self, file, load_header=True) -> None:
        # Store file reference
        self.file = file
        # Set up array and internal pointer
        self.sections = []
        self.section_ptr = 0

        if load_header:
            self.load_gsd_header()

    def __parse_header_line(line:str) -> tuple:
        # Get line parts
        line_parts = GSDFile.__split_line(line)
        return int(line_parts[0].strip()), line_parts[1].strip()

    def __parse_section_name(name:str) -> tuple:
        # Strip header characters if present
        if name.startswith('['): name = name[1:-1]

        # Parse into tuple
        name_parts = name.split(',')
        if len(name_parts) < 2:
            return name
        
        return (int(name_parts[0].strip()), name_parts[1].strip())

    def __split_line(line:str) -> list:
        # Look for allocation marker
        ix = line.index('=')

        # If no allocation marker found return an empty line
        if ix < 0:
            return (0, [])

        # Get line parts and strip whitespace
        return [x.strip() for x in line[ix + 1:].split(',')]

    def __next_section(self):
        while True:
            line = self.file.readline()
            # Stop if data runs out
            if line is None:
                break

            # Return the lineif it starts with a square bracket
            if line.startswith('['):
                return line.strip()
        return None
    
    def load_gsd_header(self) -> None:
        """Load the header from a GSD file."""

        # Start at beginning of file
        self.file.seek(0)

        # Advæance to TP section
        self.skip_to_section('TP')

        while True:
            line = self.file.readline()

            # Stop if data runs out
            if line is None:
                break

            # Skip blank lines
            if len(line.strip()) == 0:
                continue
            
            # Stop once we reach the next header
            if line.startswith('['):
                break

            self.sections.append(GSDFile.__parse_header_line(line))

    def load_gsd_section(self, section:tuple, lines:list=[]) -> None:
        """Load a section from a GSD file."""
        # Reconstruct the section name
        si, sname = section
        section_name = f'{si:03d},{sname}'

        # Start at beginning of file
        self.file.seek(0)

        # Skip to section
        self.skip_to_section(name=section_name)

        while True:
            line = self.file.readline()

            # Stop if data runs out
            if line is None:
                break

            # Stop at next section
            if line.startswith('['):
                break
            
            # Skip blank lines
            if len(line.strip()) == 0:
                continue
            
            # Add the cleaned-up line to list
            lines.append(line.strip())

    def read_section(self, section_name:str=None) -> None:
        # If a section name is provided, skip to that section; otherwise read the next section
        if section_name:
            self.skip_to_section(name=section_name)

        while True:
            line = self.file.readline()

            # Stop if data runs out
            if line is None:
                break

            # Stop at next section
            if line.startswith('['):
                break

            # Skip blank lines
            if len(line.strip()) == 0:
                continue

            # Yield the cleaned-up line
            yield GSDFile.__split_line(line.strip())

        return

    def skip_to_section(self, name:str=None, section_id:int=0) -> None:
        while True:
            s = self.__next_section()

            # Stop if no section found
            if s is None:
                break
            # Search by section name
            if name is not None and s.strip() == f'[{name}]':
                return
            # Search by section ID
            if section_id > 0 and GSDFile.__parse_section_name(s.strip())[0] == section_id:
                return
        
        raise EOFError(f'Could not find section {name}')



def __parse_gsd_coord(coord):
        # Convert to signed zero-padded 8 digit field
        coordStr = '{:+010d}'.format(int(coord))

        # Degrees is first 4 characters (includes sign)
        d = int(coordStr[:4])
        # Minute is remainder of string
        dm = float(coordStr[4:]) / 10000.0
        # Convert from decimal minutes to DMS
        dms = add_seconds(d, dm)
        #log.debug(f'Coordinate: {coord}->{coordStr}->{(d, dm)}->{dms}', coord, coordStr, (d, dm), dms)

        return dms

def convert_coords(point: dict) -> dict:
    wgs = WGSCoordinate(point['lat'], point['lon'])
    utm = WGS_to_UTM(wgs)
    #log.debug('wgs: %s', wgs)
    #log.debug('utm: %s', utm)
    point['x'] = utm.x
    point['y'] = utm.y
    #log.debug(f'x={utm.x}; y={utm.y}')

    return point

def convert_gsd_to_data_point(gsd_line:list) -> dict:
    # GSD line should be a list of 6 strs
    if gsd_line is None:
        return None

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
        # GSD date and time in DDMMYYHHMMSS format
        dtStr = f'{int(gsd_dt):06d}{int(gsd_tm):06d}'
        dt = datetime.datetime.strptime(dtStr, '%d%m%y%H%M%S')
        #log.debug('Date: %s, %s', dtStr, dt)
        # Convert to timestamp
        point['ts'] = int(dt.timestamp())

        # Parse latitude, first convert to DMS
        (latD, latM, latS) = __parse_gsd_coord(gsd_lat)

        # Parse longitude, first convert to DMS
        (lonD, lonM, lonS) = __parse_gsd_coord(gsd_lon)

        # Convert to WGS
        dms = DMSCoordinate(latD, latM, latS, lonD, lonM, lonS)
        #log.debug('DMS: %s', dms)
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


def enrich_point_with_alt_delta(window: MovingWindow, point: dict) -> dict:
    # Add point to window
    window.add_point(point)

    # Get alt delta
    alt_delta = window.delta('alt')
    print(f'alt_d={alt_delta}')

    # Enrich point
    point['alt_d'] = alt_delta

    return point

def enrich_point_with_distance_and_heading(window: MovingWindow, point: dict) -> dict:
    # Add point to window
    window.add_point(point)

    # Get distance
    dist = hypot(window.delta('x'), window.delta('y'))
    calc_spd = (dist / window.delta('ts')) if window.delta('ts') > 0 else 0

    # Get heading
    hdg = degrees(atan2(window.delta('x'), window.delta('y')))
    print(f'dist={dist}; hdg={hdg}; calc_spd={calc_spd}')

    # Enrich point
    point['d'] = dist
    point['hdg'] = hdg

    return point


if __name__ == '__main__':
    with open('data/20180215.gsd', 'r') as f:
        gsd = GSDFile(f)

        print(gsd.sections)

        alt_window = MovingWindow(2)
        alt_delta_function = lambda x: enrich_point_with_alt_delta(alt_window, x)

        dist_window = MovingWindow(2)
        dist_function = lambda x: enrich_point_with_distance_and_heading(dist_window, x)

        result = map(alt_delta_function, map(dist_function, map(convert_coords, map(convert_gsd_to_data_point, gsd.read_section()))))

        print(list(result))
