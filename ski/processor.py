import logging
from math import atan2, degrees, hypot
from .coordinate import DMSCoordinate, DMS_to_WGS, WGS_to_UTM
from .gsd import convert_gsd_alt, convert_gsd_coord, convert_gsd_date, convert_gsd_speed
from .utils import MovingWindow

log = logging.getLogger(__name__)
points_log = logging.getLogger('points')


def __log_point(msg:str, point:dict, *args:str):
    points_log.info('[%10s] ' + msg, point['ts'], *[point[x] for x in args])

def map_all(iterable, *functions):
    for f in functions:
        iterable = map(f, iterable)

    return iterable


def build_point_from_gsd(gsd_line:list, convert_coords:bool=True) -> dict:
    """Build a GPS point from a line of GSD-formatted data"""
    if gsd_line is None:
        return None

    log.debug('build_point_from_gsd: line=%s', gsd_line)

    # GSD line should be a list of 6 strs
    if len(gsd_line) != 6:
        log.warn('gsd_line does not look like valid GSD data: %s', gsd_line)
        return None

    # Read data from GSD line
    gsd_lat = gsd_line[0]
    gsd_lon = gsd_line[1]
    gsd_tm  = gsd_line[2]
    gsd_dt  = gsd_line[3]
    gsd_spd = gsd_line[4]
    gsd_alt = gsd_line[5]
    log.debug('build_point_from_gsd: lat=%s; lon=%s; tm=%s; dt=%s; spd=%s; alt=%s', gsd_lat, gsd_lon, gsd_tm, gsd_dt, gsd_spd, gsd_alt)

    point = {}

    try:
        # Convert GSD date and time strings to UTC timestamp?
        point['dt'] = convert_gsd_date(gsd_dt, gsd_tm)
        point['ts'] = int(point['dt'].timestamp())
        __log_point(f'IN=GSD{gsd_line}', point)
        __log_point('dt=%s', point, 'dt')
        
        # Convert GSD coordinate to DMS
        dms = DMSCoordinate(*convert_gsd_coord(gsd_lat), *convert_gsd_coord(gsd_lon))
        # Then convert to WGS
        wgs = DMS_to_WGS(dms)
        log.debug('build_point_from_gsd: (%s,%s) -> %s -> %s', gsd_lat, gsd_lon, dms, wgs)

        # Latitude & Longitude
        point['lat'] = wgs.get_latitude_degrees()
        point['lon'] = wgs.get_longitude_degrees()
        __log_point('lat=%4f', point, 'lat')
        __log_point('lon=%.4f', point, 'lon')

        # Cartesian coordinates
        if convert_coords:
            # Convert to UTM
            utm = WGS_to_UTM(wgs)
            log.debug('build_point_from_gsd: %s -> %s', wgs, utm)

            # X & Y
            point['x'] = utm.x
            point['y'] = utm.y
            __log_point('x=%d', point, 'x')
            __log_point('y=%d', point, 'y')
            

        # GSD speed in m/h?
        point['spd'] = convert_gsd_speed(gsd_spd)
        __log_point('spd=%.2f', point, 'spd')

        # GSD altitude in 10^-5?!, convert from floating point to int
        point['alt'] = convert_gsd_alt(gsd_alt)
        __log_point('alt=%4d', point, 'alt')

    except ValueError as e:
        log.warn('Failed to parse GSD line: %s; %s', gsd_line, e, exc_info=True)
        return None
        
    # Return data item
    return point


def enrich_point(window: MovingWindow, point: dict, add_distance:bool=True, add_deltas:bool=True) -> dict:
    # Add point to window
    window.add_point(point)

    # Get distance and heading
    if add_distance and 'x' in point and 'y' in point:
        point['d'] = hypot(window.delta('x'), window.delta('y'))
        calc_spd = (point['d'] / window.delta('ts')) if window.delta('ts') > 0 else 0
        # Get heading
        point['hdg'] = degrees(atan2(window.delta('x'), window.delta('y')))
        __log_point('d=%.3f', point, 'd')
        __log_point('hdg=%03d', point, 'hdg')

    if add_deltas and 'alt' in point:
        # Altitude delta
        point['alt_d'] = window.delta('alt')
        __log_point('alt_d=%d', point, 'alt_d')

    if add_deltas and 'spd' in point:
        # Speed delta
        point['spd_d'] = window.delta('spd')
        __log_point('spd_d=%.3f', point, 'spd_d')

    return point
