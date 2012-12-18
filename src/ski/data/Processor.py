'''
Created on 28 Nov 2012

@author: sroberts
'''

import ski.data as d
from datetime import datetime

try:
    import pytz
    tz = pytz.utc
    tz_support = True
except ImportError:
    tz_support = False

pData = d.ProcessedData()









def __create_point(d, lastP=None):

    # Create point
    p = SkiTrackPoint(d)
    
    if lastP is not None:
        # Previous point provided
        p.delta_x = p.x - lastP.x
        p.delta_y = p.y - lastP.y
        p.delta_a = p.alt - lastP.alt
        p.delta_ts = p.ts - lastP.ts
        p.distance = sqrt((p.delta_x ** 2) + (p.delta_y ** 2) + (p.delta_a ** 2))
        p.xy_distance = sqrt((p.delta_x ** 2) + (p.delta_y ** 2))
        p.calc_speed = (p.distance / p.delta_ts) * 3.6
        p.angle = degrees(atan(p.delta_a / p.xy_distance)) if p.xy_distance > 0 else 0.0

    return p





def set_tz(tz_name):
    global tz
    if tz_support:
        try:
            tz = pytz.timezone(tz_name)
            print 'Timezone set:{0}'.format(tz.zone)
        except pytz.exceptions.UnknownTimeZoneError:
            print 'Unknown time zone: ' + tz_name
            tz = pytz.utc

def b_ts(secs):
    dt = datetime.fromtimestamp(secs)
    if tz_support:
        loc_dt = pytz.utc.localize(dt)
        return loc_dt.astimezone(tz)
    else:
        print 'Warning: using non-localized time'
        return dt

def pack(mode, ts, x, y, a, s):
    return (mode, (ts, (x, y), a, s))

def repack((ts, (la, lo), (x, y), a, s)):
    return pack('STOP', b_ts(ts), x, y, a, s)

def process(inData):
    print 'Processing using TZ:{0}'.format(tz)
    pData.all_points = map(repack, inData)
    
    return pData.all_points
