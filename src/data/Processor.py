'''
Created on 28 Nov 2012

@author: sroberts
'''

def b_ts(date, time):
    return 0

def pack(mode, ts, x, y, a, s):
    return (mode, (ts, (x, y), a, s))

def repack((ts, ((la, lo), (x, y), a, s))):
    return pack('STOP', ts, x, y, a, s)

def process(inData):
    return map(repack, inData)
