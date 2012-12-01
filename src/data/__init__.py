'''

  GPS data structures:
    GPSDatum: (ts, geo_coords, cart_coords, a, s)

  Main data structures:
    SkiPoint: (mode, (ts, (x, y), a, s))
    Track: (TrackHeader, [SkiPoint])
    TrackHeader: <class>


@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (28 Nov 2012)
'''

################################
# SKI POINT FUNCTIONS
########

# Define functions for extracting elements from point
p_Mode = lambda (m, (ts, (x, y), a, s)): m
p_TS = lambda (m, (ts, (x, y), a, s)): ts
p_X = lambda (m, (ts, (x, y), a, s)): x
p_Y = lambda (m, (ts, (x, y), a, s)): y
p_A = lambda (m, (ts, (x, y), a, s)): a
p_S = lambda (m, (ts, (x, y), a, s)): s

# Convenience functions for XY plots
p_Cart = lambda (m, (ts, c, a, s)): c
p_Cart_r = lambda (mx, my), (m, (ts, (x, y), a, s)): (x - mx, y - my)
p_Cart_A = lambda (m, (ts, c, a, s)): (c, a)
p_Cart_A_r = lambda (mx, my), (m, (ts, (x, y), a, s)): ((x - mx, y - my), a)
p_Cart_S = lambda (m, (ts, c, a, s)): (c, s)
p_Cart_S_r = lambda (mx, my), (m, (ts, (x, y), a, s)): ((x - mx, y - my), s)

# Convenience functions for time stamp plots
p_TS_A = lambda (m, (ts, c, a, s)): (ts, a)
p_TS_Mode = lambda (m, (ts, c, a, s)): (ts, m)
p_TS_S = lambda (m, (ts, c, a, s)): (ts, s)


################################
# SKI POINT LIST FUNCTIONS
########

# Move to UTILS
def repeat(value, times):
    return [value for __i in range(times)]


def min_xy(data): return (min(ps_Xs(data)), min(ps_Ys(data)))

# Base functional transforms
def ps_Carts(data): return map(p_Cart, data)
def ps_Modes(data): return map(p_Mode, data)
def ps_TSs(data): return map(p_TS, data)
def ps_Xs(data): return map(p_X, data)
def ps_Ys(data): return map(p_Y, data)
def ps_As(data): return map(p_A, data)
def ps_Ss(data): return map(p_S, data)

# Functional transforms for altitude and speed XY plot data
def ps_Cart_As(data): return map(p_Cart_A, data)
def ps_Cart_Ss(data): return map(p_Cart_S, data)

# Functional transforms for altitude and speed time plot data
def ps_TS_As(data): return map(p_TS_A, data)
def ps_TS_Modes(data): return map(p_TS_Mode, data)
def ps_TS_Ss(data): return map(p_TS_S, data)

# Functional transform to get relative XY pairs
def ps_Cart_r(data): return map(p_Cart_r, repeat(min_xy(data), len(data)), data)
def ps_Cart_As_r(data): return map(p_Cart_A_r, repeat(min_xy(data), len(data)), data)
def ps_Cart_Ss_r(data): return map(p_Cart_S_r, repeat(min_xy(data), len(data)), data)


################################
# CLASSES, TBC
########

class ProcessedData:
    def __init__(self):
        self.all_points = []

class GPSDatum:
    '''
      Class representing a single entry of GPS data, as read from a GPS device
      or file.
    '''
    def __init__(self, (ts, (la, lo), (x, y), a, s)):
        self.gps_ts = ts
        self.gps_la = la
        self.gps_lo = lo
        self.gps_x = x
        self.gps_y = y
        self.gps_a = a
        self.gps_s = s


class SkiPoint:
    
    mode = None
    x = y = 0
    alt = 0
    speed = 0
    ts = 0
    
    MODE_LIFT = 'LIFT'
    MODE_SKI = 'SKI'
    MODE_STOP = 'STOP'
    P0 = (MODE_STOP, (0, (0, 0), 0, 0))
    
    def __init__(self, (mode, (ts, (x, y), alt, speed))):
        self.mode = mode
        self.ts = ts
        self.x = x
        self.y = y
        self.alt = alt
        self.speed = speed
    
    def flatten(self):
        return (self.mode, (self.ts, (self.x, self.y), self.alt, self.speed))
    
    def print_point(self):
        print 'Ski point: {0}'.format(self.mode)
        print 'Timestamp: {0}'.format(self.ts)
        print 'Location: {0}'.format((self.x, self.y))
        print 'Altitude: {0}m'.format(self.alt)
        print 'Speed: {0}km/h'.format(self.speed)



        

        
