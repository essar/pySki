
from datetime import datetime
import time

def as_seconds(dateStr, timeStr, dtFmt='%d%m%y', tmFmt='%H%M%S'):
    da = datetime.strptime(dateStr, dtFmt)
    ti = datetime.strptime(timeStr, tmFmt)
    
    dt = datetime.combine(da.date(), ti.time())
    return time.mktime(dt.timetuple())
    