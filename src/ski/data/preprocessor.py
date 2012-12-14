'''
Created on 11 Dec 2012

@author: sroberts
'''
from math import atan, degrees, sqrt
from gpsdatum import GPSDatum
from skitrack import SkiTrackPoint


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

def as_dpoints(dList):
    return [GPSDatum(d) for d in dList]

def as_points(dList):
    pts = []
    lastP = None
    for d in dList:
        lastP = __create_point(d, lastP)
        pts.append(lastP)
    return pts;