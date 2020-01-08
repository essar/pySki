"""
  Loads and manages configuration data.
"""

import logging

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def debug_point_event(logger, point, message, *args):
    log_msg = '[%010d] ' + message
    logger.debug(log_msg, point.ts, *args)


def debug_track_event(logger, track, message, *args):
    log_msg = '[%s] ' + message
    logger.debug(log_msg, track.track_id, *args)


def info_track_event(logger, track, message, *args):
    log_msg = '[%s] ' + message
    logger.debug(log_msg, track.track_id, *args)


def log_json(logger, level, track=None, point=None, message=None, **obj):

    log_msg = {}
    if track is not None:
        log_msg.update({
            'track': '{:s}'.format(track.track_id)
        })
    if point is not None:
        log_msg.update({
            'point': '{:010d}'.format(point.ts)
        })
    if message is not None:
        log_msg.update({
            'message': message.format(obj)
        })
    if len(obj) > 0:
        log_msg.update(obj)

    logger.log(level, log_msg)
