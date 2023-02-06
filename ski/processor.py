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
        __log_point(f'SRC=GSD{gsd_line}', point)
        __log_point('dt=%s', point, 'dt')
        
        # Convert GSD coordinate to DMS
        dms = DMSCoordinate(*convert_gsd_coord(gsd_lat), *convert_gsd_coord(gsd_lon))
        # Then convert to WGS
        wgs = DMS_to_WGS(dms)
        log.debug('build_point_from_gsd: (%s,%s) -> %s -> %s', gsd_lat, gsd_lon, dms, wgs)

        # Latitude & Longitude
        point['lat'] = round(wgs.get_latitude_degrees(), 4)
        point['lon'] = round(wgs.get_longitude_degrees(), 4)
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
        point['spd'] = round(convert_gsd_speed(gsd_spd), 3)
        __log_point('spd=%.3f', point, 'spd')

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


def linear_interpolate(iter_in) -> None:

    # Define internal interpolation function
    def __interp_f(prev_point: dict, point: dict, item:str, delta:int):
        int_value = prev_point[item] + ((point[item] - prev_point[item]) / delta)
        log.debug('linear_interpolate: (%s,%s)[%d] -> %s', prev_point[item], point[item], delta, int_value)
        return int_value

    try:
        prev_point = None
        while True:
            point = next(iter_in)
            
            if prev_point:
                ts_d = point['ts'] - prev_point['ts']
                log.debug('linear_interpolate: %d -> %d; ts_d=%d', prev_point['ts'], point['ts'], ts_d)
                
                if ts_d == 0:
                    # Remove if duplicate
                    log.info('linear_interpolate: duplicate identified at %d, removing', point['ts'])
                    continue
                
                while ts_d > 1:
                    int_ts = int(__interp_f(prev_point, point, 'ts', ts_d))
                    log.debug('linear_interpolate: Adding interpolated point at %d', int_ts)
                    new_point = {
                        'ts': int_ts,
                        'lat': round(__interp_f(prev_point, point, 'lat', ts_d), 4),
                        'lon': round(__interp_f(prev_point, point, 'lon', ts_d), 4),
                        'x': int(__interp_f(prev_point, point, 'x', ts_d)),
                        'y': int(__interp_f(prev_point, point, 'y', ts_d)),
                        'spd': round(__interp_f(prev_point, point, 'spd', ts_d), 3),
                        'alt': int(__interp_f(prev_point, point, 'alt', ts_d))
                    }
                    __log_point(f'SRC=INT{new_point}', new_point)
                    log.debug('linear_interpolate: %s', new_point)
                    
                    yield new_point
                    prev_point = new_point
                    
                    # Recalc delta
                    ts_d = point['ts'] - prev_point['ts']

            yield point
            prev_point = point

    except StopIteration:
        pass


def remove_outlyers(window: MovingWindow, point: dict) -> list:
    pass


def summary(summary_obj:dict, point:dict) -> dict:

    # Total distance
    if 'd' in point:
        summary_obj['total_dist'] = summary_obj.setdefault('total_dist', 0.0) + point['d']

    # XY bounds
    if 'x' in point:
        summary_obj['x_bounds'] = [
            min(summary_obj['x_bounds'][0], point['x']) if 'x_bounds' in summary_obj else point['x'],
            max(summary_obj['x_bounds'][1], point['x']) if 'x_bounds' in summary_obj else point['x']
        ]
    if 'y' in point:
        summary_obj['y_bounds'] = [
            min(summary_obj['y_bounds'][0], point['y']) if 'y_bounds' in summary_obj else point['y'],
            max(summary_obj['y_bounds'][1], point['y']) if 'y_bounds' in summary_obj else point['y']
        ]

    # Min/max alts
    if 'alt' in point:
        summary_obj['min_alt'] = min(summary_obj['min_alt'], point['alt']) if 'min_alt' in summary_obj else point['alt']
        summary_obj['max_alt'] = max(summary_obj['max_alt'], point['alt']) if 'max_alt' in summary_obj else point['alt']

    # Max speed
    if 'spd' in point:
        summary_obj['max_spd'] = max(summary_obj['max_spd'], point['spd']) if 'max_spd' in summary_obj else point['spd']

    # Total descent
    if 'alt_d' in point:
        summary_obj['total_desc'] = summary_obj.setdefault('total_desc', 0.0) + max(0, point['alt_d'])
    

    return point
