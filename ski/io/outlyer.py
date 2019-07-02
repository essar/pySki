"""
"""
import logging

from ski.config import config
from ski.io.cleanup import get_distance, get_ts_delta


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

outlyer_max_speed = config['outlyer']['max_speed']
outlyer_max_speed_factor = config['outlyer']['max_speed_factor']


def is_outlyer(prev_point, point):
    # Skip if no previous point provided
    if prev_point == None:
        log.debug('is_outlyer: skipping as previous point is None')
        return False
    
    # calculate distance travelled in metres
    calc_dist = get_distance(prev_point, point)
    ts_delta = get_ts_delta(prev_point, point)
    
    # calculate speed (convert metres per second -> km per hour)
    calc_spd = (calc_dist / ts_delta) * 3.60
    calc_spd_factor = 1 if point.spd == 0.0 else calc_spd / max(1, point.spd)
    log.debug('is_outlyer: ts_delta=%d, calc_dist=%.2f, gps_speed=%.2f, calc_speed=%.4f, calc_spd_factor=%.3f', ts_delta, calc_dist, point.spd, calc_spd, calc_spd_factor)

    # Compare calculated speed against max speed
    if calc_spd > outlyer_max_speed:
        log.info('Removing point: calculated speed (%.2f) exceeds threshold', calc_spd)
        return True

    # Compare calculated speed factor against max speed factor and inverse (e.g. 1/3) speed factor
    if calc_spd_factor > outlyer_max_speed_factor or calc_spd_factor < (1 / outlyer_max_speed_factor):
        log.info('Removing point: calculated speed (%.2f) exceeds factor threshold (%.1fx)', calc_spd, calc_spd_factor)
        return True

    return False
