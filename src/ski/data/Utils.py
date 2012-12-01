'''
Created on 16 Nov 2012

@author: sroberts
'''
from ui.gl import GLRenderer

__def_min_max__ = (9999999999999,0)

# Base functional transforms
def alts(data): return map(lambda (ts, (g, c, a, s)): a, data)
def carts(data): return map(lambda (ts, (g, c, a, s)): c, data)
def geos(data): return map(lambda (ts, (g, c, a, s)): g, data)
def speeds(data): return map(lambda (ts, (g, c, a, s)): s, data)
def xs(data): return map(lambda (ts, (g, (x, y), a, s)): x, data)
def ys(data): return map(lambda (ts, (g, (x, y), a, s)): y, data)

# Functional transforms for altitude and speed XY plot data
def cart_alts(data): return map(lambda (ts, (g, c, a, s)): (c, a), data)
def cart_speeds(data): return map(lambda (ts, (g, c, a, s)): (c, s), data)

# Functional transforms for altitude and speed time plot data
def ts_alts(data): return map(lambda (ts, (g, c, a, s)): (ts, a), data)
def ts_speeds(data): return map(lambda (ts, (g, c, a, s)): (ts, s), data)

# Functions for getting minimum and maximum values
def min_max_alts(data): return reduce(lambda (a,b), x: (min(a,x), max(b,x)), alts(data), __def_min_max__)
def min_max_speeds(data): return reduce(lambda (a,b), x: (min(a,x), max(b,x)), speeds(data), __def_min_max__)
def min_max_x(data): return reduce(lambda (a,b), x: (min(a,x), max(b,x)), xs(data), __def_min_max__)
def min_max_y(data): return reduce(lambda (a,b), y: (min(a,y), max(b,y)), ys(data), __def_min_max__)

''' Returns a list of ints, X & Y coordinates '''
def rel_xy_coord_list(data):
    minX = min(xs(data))
    minY = min(ys(data))
    
    coords = []
    for (x, y) in carts(data):
        coords.append(int(x - minX))
        coords.append(int(y - minY))
    
    return coords

def rel_xyz_coord_list(data):
    minX = min(xs(data))
    minY = min(ys(data))
    minA = min(alts(data))
    
    coords = []
    for ((x, y), a) in cart_alts(data):
        coords.append(int(x - minX))
        coords.append(int(y - minY))
        coords.append(int(a - minA))
    
    return coords

def f_colours(f, data):
    # Transform data
    data = f(data)
    
    # Calculate boundary values
    minV = min(data)
    maxV = max(data)
    
    colInfo = []
    for v in data:
        (r, g, b) = GLRenderer.getColourValue(minV, maxV, v)
        colInfo.append(r)
        colInfo.append(g)
        colInfo.append(b)
    
    return colInfo
