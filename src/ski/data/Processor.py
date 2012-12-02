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
