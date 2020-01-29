"""
  Loads and manages configuration data.
"""

import logging
from sys import argv

from argparse import ArgumentParser
from ski.config import config

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Set up point logger
point_log = logging.getLogger('POINTLOG')
point_log.setLevel(logging.INFO)

# Load config values
cfg_log_mode = 'DEBUG' if config['logging']['debug'] else 'INFO'
cfg_point_log_mode = config['logging']['point_log']

# Default values
DEFAULT_LOG_FMT = '%(asctime)s %(levelname)7s (%(name)s) %(message)s'


def configure_logging(default_log_level=cfg_log_mode, point_log_level=cfg_point_log_mode):

    # Create default formatter
    fmt = logging.Formatter(DEFAULT_LOG_FMT)

    # Override debug mode
    if len(argv) > 0:
        ap = ArgumentParser()
        ap.add_argument('--debug', action='store_true')
        args = ap.parse_args()
        if args.debug:
            default_log_level = logging.DEBUG

    # Create default handler
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    h.setLevel(default_log_level)

    # Configure root logger; only log errors and above
    logging.root.setLevel(logging.ERROR)

    # Configure default logger
    logging.getLogger('ski').addHandler(h)

    # Configure point log
    configure_point_log(point_log_level)


def configure_point_log(point_log_mode=cfg_point_log_mode):
    log.debug('point_log_mode=%s', point_log_mode)

    if point_log_mode is False or point_log_mode == 'off' or point_log_mode == 'OFF':
        point_log.setLevel(logging.ERROR)
        log.debug('Disabled point log')
    elif point_log_mode is True or point_log_mode == 'console' or point_log_mode == 'CONSOLE':
        point_log.setLevel(logging.INFO)
        log.debug('Enabled point log to console')
    elif point_log_mode == 'file' or point_log_mode == 'FILE':
        # Create a new file handler; overwrite existing file
        file_handler = logging.FileHandler('points.log', 'w')

        # Add a new file handler
        point_log.addHandler(file_handler)
        log.info('Enabled point log to file (points.log)')

    else:
        log.warning('Unexpected point log mode: %s, defaulting to console', point_log_mode)


def debug_point_event(logger, point, message, *args):
    log_msg = '[%010d] ' + message
    logger.debug(log_msg, point.ts, *args)


def debug_track_event(logger, track, message, *args):
    log_msg = '[%s] ' + message
    logger.debug(log_msg, track.track_id, *args)


def info_track_event(logger, track, message, *args):
    log_msg = '[%s] ' + message
    logger.debug(log_msg, track.track_id, *args)


def enable_debug(debug_enable=True):
    for h in logging.getLogger('ski').handlers:
        h.setLevel(logging.DEBUG if debug_enable else logging.INFO)


def calc_stats(stats, total_exec_time):
    return stats['point_count'], stats['process_time'], (stats['process_time'] / total_exec_time * 100.0)


def increment_stat(stats, stat_name, value):
    stats[stat_name] = (stats[stat_name] if stat_name in stats else 0) + value


def log_point(point_id, phase, level=logging.INFO, **obj):
    log_msg = {
        'phase': phase
    }
    log_msg.update(obj)

    point_log.log(level, '[%010d] %s', point_id, log_msg)


# Configure logging
configure_logging()
