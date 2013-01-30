'''
Created on 23 Jan 2013

@author: sroberts
'''

def getColourValue(minV, maxV, value):
    if value == 'SKI': return (1.0, 0.0, 0.0)
    if value == 'LIFT': return (0.0, 0.0, 1.0)
    if value == 'STOP': return (1.0, 1.0, 1.0)
    
    return (0.0, 0.0, 0.0)
