'''
Created on 16 Nov 2012

@author: sroberts
'''

import logging as log

import io.GSDLoader
import io.GPXLoader
import data.preprocessor
import data.processor

def readGPXData(*filename):
    dList = []
    # Read GPX data from file
    for f in filename:
        gpxData = io.GPXLoader.load_gpx_file(f)
    
        # Pre process
        dList.append(data.preprocessor.preprocess(gpxData))

    # Set time zone
    data.processor.set_tz('US/Mountain')
    
    # Process data
    all_data = data.processor.process(*dList)
    hdr = all_data.hdr
    hdr.print_track_header()
    
    return all_data

def readGSDData(filename):
    # Read GSD data from file
    gsdData = io.GSDLoader.load_gsd_file(filename)
    
    # Pre process
    dList = data.preprocessor.preprocess(gsdData)

    # Set time zone
    data.processor.set_tz('US/Mountain')
    
    # Process data
    all_data = data.processor.process(dList)
    hdr = all_data.hdr
    hdr.print_track_header()
    
    return all_data

# Config log levels
log.basicConfig(level=log.INFO)
log.getLogger('ski').setLevel(log.INFO)
log.getLogger('ski.data.preprocessor').setLevel(log.DEBUG)

readGPXData('../data/ski_20130210_sjr.gpx'
          , '../data/ski_20130211_sjr.gpx'
          , '../data/ski_20130212_sjr.gpx'
          , '../data/ski_20130213_sjr.gpx'
          , '../data/ski_20130214_sjr.gpx'
          , '../data/ski_20130215_sjr.gpx'
          , '../data/ski_20130216_sjr.gpx')

#readGPXData('../data/ski_20130217_sjr.gpx'
#          , '../data/ski_20130218_sjr.gpx'
#          , '../data/ski_20130219_sjr.gpx'
#          , '../data/ski_20130220_sjr.gpx'
#          , '../data/ski_20130221_sjr.gpx'
#          , '../data/ski_20130222_sjr.gpx')