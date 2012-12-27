'''
  Module responsible for processing GPS data, building tracks and analytics
  data.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (28 Nov 2012)
'''

from datetime import datetime
import logging
from math import degrees, sqrt, atan

log = logging.getLogger(__name__)

from skitrack import MODE_LIFT, MODE_SKI, MODE_STOP, SkiTrack, SkiTrackPoint
from types import InstanceType

###############################################################################
# TIMEZONE SUPPORT
###############################################################################

# Import time zone modules if available
try:
    import pytz
    tz = pytz.utc
    tz_support = True
except ImportError:
    log.warn('Unable to enable time zone support, please add pytz package to path.')
    tz_support = False

def as_time(secs):
    '''
      Turns a time stamp into a time object.  The time stamp is localised if time
      zone support has been enabled.
      @param secs: a number of seconds since epoch to covert to a time object.
      @return: the argument as a localised time object.
    '''
    dt = datetime.fromtimestamp(secs)
    if tz_support:
        # Convert time to local time zone
        loc_dt = pytz.utc.localize(dt)
        return loc_dt.astimezone(tz)
    else:
        log.debug('Time zone support not enabled')
        # Return non-localised time
        return dt

def set_tz(tz_name):
    '''
      Sets the time zone for the data, if time zone support has been enabled.
      @param tz_name: The standard name of the time zone to use (e.g. US/Mountain)
    '''
    global tz
    if tz_support:
        try:
            # Set the time zone
            tz = pytz.timezone(tz_name)
            log.debug('Time zone set: %s.', tz.zone)
        except pytz.exceptions.UnknownTimeZoneError:
            log.warn('Unknown time zone: %s.', tz_name)
            # Use default time zone
            tz = pytz.utc
    else:
        log.info('Time zone support not available; using UTC.')


###############################################################################
# SKI TRACK BUILDING
###############################################################################
def create_st_point(datum, last_stp=None):
    '''
      Create a SkiTrackPoint out of a GPSDatum object. If a previous
      SkiTrackPoint is provided, aggregate values (distance, speed, angle) etc.
      are calculated.
      @param datum: the GPSDatum to convert.
      @param last_stp: the last SkiTrackPoint converted.
      @return: a SkiTrackPoint, containing data captured from this datum.
    '''
    # Create point
    p = SkiTrackPoint(datum)
    log.debug('Datum converted to %s', p)
    
    # Process time stamp
    p.loc_time = as_time(p.ts)
    
    # If a previous point provided, calculate additional attributes
    if last_stp is not None:
        log.debug('    last_stp: %s', last_stp)
        
        # Calculate delta values
        p.delta_x = p.x - last_stp.x
        p.delta_y = p.y - last_stp.y
        p.delta_a = p.alt - last_stp.alt
        p.delta_ts = p.ts - last_stp.ts
        
        # Distances
        p.distance = sqrt((p.delta_x ** 2) + (p.delta_y ** 2) + (p.delta_a ** 2))
        p.xy_distance = sqrt((p.delta_x ** 2) + (p.delta_y ** 2))
        
        # Re-calculate speed
        p.calc_speed = (p.distance / p.delta_ts) * 3.6
        
        # Angle
        p.angle = degrees(atan(p.delta_a / p.xy_distance)) if p.xy_distance > 0 else 0.0

    return p
    
    
    
###############################################################################
# PROCESSING
###############################################################################

window_sz = 20

def build_track_data(all_data_list):
    global track_data, track_index
    
    track_data = {}
    track_index = []
    this_track = []
    this_mode = None
    
    for stp in all_data_list:
        if this_mode is not None and this_mode <> stp.mode:
            # New mode, save previous track
            st = SkiTrack(this_track)
            log.debug('Compiled %s track of %d points (distance=%.1fm; dAlt=%dm)', this_mode, len(this_track), st.hdr.distance, st.hdr.dAlt)
            track_data[this_track[0]] = (st, None)
            
            # Create new track
            this_track = []
        
        # Set track mode
        this_mode = stp.mode
        # Add point to current track    
        this_track.append(stp)
        # Add track to index
        track_index.append(this_track[0])


def find_nearby_tracks(radius=20):
    # Look through track_data dictionary key list for near by points of same mode
    log.debug('Looking for tracks within %dm', radius)
    
    for k1 in track_data.keys():
        # Ignore STOP tracks
        if k1.mode == MODE_STOP:
            continue
        
        k_nears = []
        for k2 in track_data.keys():
            # Pass if is the same track
            if k2.ts == k1.ts:
                continue
            # Pass if modes are not the same
            if k2.mode != k1.mode:
                continue
         
            # Calculate distance between two points
            dx = k2.x - k1.x
            dy = k2.y - k1.y
            da = k2.alt - k1.alt
            dst = sqrt((dx ** 2) + (dy ** 2) + (da ** 2))
    
            if dst <= radius:
                log.debug('%d: Found track nearby (%d, (%d, %d)); distance=%.2fm', k1.ts, k2.ts, k2.x, k2.y, dst)
                # Save track
                k_nears.append(k2)
        
        if len(k_nears) > 0:
            (track, _nears) = track_data[k1]
            track_data[k1] = (track, k_nears)
            log.debug('%d: (%d, %d) found %d %s tracks within %dm radius', k1.ts, k1.x, k1.y, len(k_nears), k1.mode, radius)
        

def process_track_point(current_mode, this_point, point_window):
    # Validate arguments
    if type(current_mode) is not str:
        raise ValueError('Expected String at argument 1', type(current_mode))
    if type(this_point) is not InstanceType:
        raise ValueError('Expected SkiTrackPoint at argument 2', type(this_point))
    if type(point_window) is not list:
        raise ValueError('Expected list at argument 3')
    
    # Calculate window properties
    wLen = float(len(point_window))
    
    alts = map(lambda stp: stp.delta_a, point_window)
    ascent = sum(alts)
    ascending = float(sum([1 for a in alts if a > 0])) / wLen
    descending = float(sum([1 for a in alts if a < 0 ])) / wLen
    
    dists = map(lambda stp: stp.distance, point_window)
    moving = float(sum([1 for d in dists if d > 0])) / wLen
    stopped = float(sum([1 for d in dists if d == 0])) / wLen
    
    if current_mode == MODE_STOP:
        # Stopped, but now moving
        if this_point.distance > 0 and moving >= 0.5:
            if this_point.delta_a > 0 and ascent > 0 and ascending > 0.3:
                # Altitude ascending
                log.debug('%s->%s, at %s.', current_mode, MODE_LIFT, this_point)
                log.debug('    alts=%s', alts)
                log.debug('    dists=%s', dists)
                log.debug('    distance=%.1f; moving=%.2f.', this_point.distance, moving)
                log.debug('    delta_a=%.1f, ascent=%.1f, ascending=%.2f', this_point.delta_a, ascent, ascending)
                return MODE_LIFT
            if this_point.delta_a < 0 and ascent < 0 and descending > 0.3:
                # Altitude descending
                log.debug('%s->%s, at %s.', current_mode, MODE_SKI, this_point)
                log.debug('    alts=%s', alts)
                log.debug('    dists=%s', dists)
                log.debug('    distance=%.1f; moving=%.2f.', this_point.distance, moving)
                log.debug('    delta_a=%.1f, ascent=%.1f, descending=%.2f', this_point.delta_a, ascent, descending)
                return MODE_SKI
        
    if current_mode == MODE_SKI:
        # Skiing, but now not moving
        if this_point.distance == 0 and stopped > 0.8:
            log.debug('%s->%s, at %s.', current_mode, MODE_STOP, this_point)
            log.debug('    alts=%s', alts)
            log.debug('    dists=%s', dists)
            log.debug('    distance=%.1f; stopped=%.2f.', this_point.distance, stopped)
            return MODE_STOP

        # Skiing, but now on a lift
        if this_point.delta_a > 0 and ascent > 0 and ascending > 0.7:
            log.debug('%s->%s, at %s.', current_mode, MODE_LIFT, this_point)
            log.debug('    alts=%s', alts)
            log.debug('    dists=%s', dists)
            log.debug('    delta_a=%.1f, ascent=%.1f, ascending=%.2f', this_point.delta_a, ascent, ascending)
            return MODE_LIFT

    if current_mode == MODE_LIFT:
        # On a lift, but now not moving
        if this_point.distance == 0 and stopped > 0.8:
            log.debug('%s->%s, at %s.', current_mode, MODE_STOP, this_point)
            log.debug('    alts=%s', alts)
            log.debug('    dists=%s', dists)
            log.debug('    distance=%.1f; stopped=%.2f.', this_point.distance, stopped)
            return MODE_STOP
        
        # On a lift, but now skiing
        if this_point.delta_a <= 0 and ascent < 0 and descending > 0.7:
            log.debug('%s->%s, at %s.', current_mode, MODE_SKI, this_point)
            log.debug('    alts=%s', alts)
            log.debug('    dists=%s', dists)
            log.debug('    delta_a=%.1f, ascent=%.1f, descending=%.2f', this_point.delta_a, ascent, descending)
            return MODE_SKI
        
    # No matches, so stay in same mode
    return current_mode


def process(data):
    '''
      Process GPS data into ski tracks and perform analytics.
      @param data: a list of GPSDatum objects that have been pre-processed.
    '''
    global all_data, lift_data, ski_data, stop_data, track_data, track_index
    
    log.info('Starting data processing of %d points.', len(data))
    log.info('Time zone: %s.', tz)
    
    # Build list of STPs
    log.info('----------------------------------------')
    log.info(' POINTS')
    log.info('----------------------------------------')
    
    all_data_list = []
    last_stp = None
    for d in data:
        last_stp = create_st_point(d, last_stp)
        all_data_list.append(last_stp)
    assert(len(data) == len(all_data_list))
    log.info('Built list of %d data points.', len(all_data_list))
    
    # Process to set modes
    log.info('----------------------------------------')
    log.info(' MODES')
    log.info('----------------------------------------')
    
    window_start = 0
    cMode = MODE_STOP
    
    for stp in all_data_list:
        # Calculate window end
        window_end = window_start + window_sz
        # Process mode
        cMode = process_track_point(cMode, stp, all_data_list[window_start:window_end])
        # Update point mode
        stp.mode = cMode
        # Increment window
        window_start += 1
    
    # Mode lists
    all_data = SkiTrack(all_data_list)
    log.info('all_data:  %d points', len(all_data))
    
    lift_data = SkiTrack(filter(lambda stp: stp.mode == MODE_LIFT, all_data_list))
    log.info('lift_data: %d points', len(lift_data))
    
    ski_data = SkiTrack(filter(lambda stp: stp.mode == MODE_SKI, all_data_list))
    log.info('ski_data:  %d points', len(ski_data))
    
    stop_data = SkiTrack(filter(lambda stp: stp.mode == MODE_STOP, all_data_list))
    log.info('stop_data: %d points', len(stop_data))
    
    assert(len(all_data) == (len(lift_data) + len(ski_data) + len(stop_data)))
    
    # Track processing
    log.info('----------------------------------------')
    log.info(' TRACKS')
    log.info('----------------------------------------')
    build_track_data(all_data_list)
    find_nearby_tracks()
    log.info('track_data:  %d tracks', len(track_data))
    log.info('track_index: %d points', len(track_index))
    
    log.info('Processing completed.')
    return all_data
