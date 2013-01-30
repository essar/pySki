'''
Created on 23 Jan 2013

@author: sroberts
'''

from math import floor

def absColourValue(minV, maxV, value):
    if value == 0: return (1.0, 0.0, 0.0)
    if value == 1: return (1.0, 0.5, 0.0)
    if value == 2: return (1.0, 1.0, 0.0)
    if value == 3: return (0.5, 1.0, 0.0)
    if value == 4: return (0.0, 1.0, 0.0)
    if value == 5: return (0.0, 1.0, 0.5)
    if value == 6: return (0.0, 1.0, 1.0)
    if value == 7: return (0.0, 0.5, 1.0)
    if value == 8: return (0.0, 0.0, 1.0)
    
    return (1.0, 1.0, 1.0)

def relColourValue(minV, maxV, value):
    return absColourValue(minV, maxV, floor(((value - minV) / max(1, (maxV - minV))) * 8))