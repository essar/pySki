'''
Created on 16 Nov 2012

@author: sroberts
'''

import logging as log

import pyglet
import io.GPXLoader
import data.preprocessor
import data.processor

#import ui.gl.linearrenderer as renderer
#import ui.gl.moderenderer as renderer
import ui.gl.ninepointrenderer as renderer
import ui.gl.glplot as glplot
from ui.gl.plotdata import PlotData


# Load data from file
def readData(*files):
    dList = []
    for filename in files:
    
        # Read GSD data from file
        gpxData = io.GPXLoader.load_gpx_file(filename)
        
        # Pre-process
        dList.append(data.preprocessor.preprocess(gpxData))
        
    # Synchronise two plots
    (dList[0], dList[1]) = data.preprocessor.synchronize(dList[0], dList[1])

    # Set time zone
    data.processor.set_tz('US/Mountain')
    
    # Process data
    all_data = data.processor.process(*dList)
    hdr = all_data.hdr
    hdr.print_track_header()
    
    #(minX, minY) = hdr.area[0]
    
    #xyData1 = [(stp.x, stp.y) for stp in all_data.data if stp.setID == 0]
    #vData1 = [stp.setID for stp in all_data.data if stp.setID == 0]
    #glData1 = PlotData.build_xy_plot(xyData1, vData1, minX, minY)
    #glData1.compile_vertex_data(renderer.absColourValue, 2)
    
    #xyData2 = [(stp.x, stp.y) for stp in all_data.data if stp.setID == 1]
    #vData2 = [stp.setID for stp in all_data.data if stp.setID == 1]
    #glData2 = PlotData.build_xy_plot(xyData2, vData2, minX, minY)
    #glData2.compile_vertex_data(renderer.absColourValue, 2)
    
    xyData = [(stp.x, stp.y) for stp in all_data.data]
    vData = [stp.setID for stp in all_data.data]
    #vData = [stp.alt for stp in all_data.data]
    #vData = [stp.spd for stp in all_data.data]
    #vData = [stp.mode for stp in all_data.data]
    glData = PlotData.build_xy_plot(xyData, vData)
    glData.compile_vertex_data(renderer.absColourValue, 2)
    
    # Create plot
    plot = glplot.GLPlot()
    
    # Calculate plot size
    plot.cfg.plot_width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*hdr.area)
    plot.cfg.plot_height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*hdr.area)
    
    # Calculate sensible altitude scaling
    altScale = float(abs(hdr.hiAlt - hdr.loAlt)) / 1000.0
    plot.cfg.scale_z = altScale
    plot.cfg.drawmode = '2D'
    plot.cfg.animate = False
    plot.cfg.window_fullscreen = True
    plot.cfg.show_marker = False
    plot.cfg.show_status_bar = False
    
    #plot.cfg.status_txt = '[ {:%d/%m/%Y %H:%M:%S %Z} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>4.1f}km/h ]'
    #plot.cfg.status_values_f = lambda idx : (all_data.data[idx].loc_time
    #                  , all_data.data[idx].mode
    #                  , all_data.data[idx].alt
    #                  , all_data.data[idx].spd
    #)
    
    #win.init_window()
    #plot.show([glData]) 
    #plot.show() 
    
    # Create plot window
    glplot.create_plot_window(plot, [glData])
    #glplot.create_plot_window(plot, [glData1, glData2])
    


# Config log levels
log.basicConfig(level=log.INFO)
log.getLogger('ski').setLevel(log.INFO)

# Code a-go-go
#readData('../data/ski_20130210_sjr.gpx'
#         , '../data/ski_20130211_sjr.gpx'
#         , '../data/ski_20130212_sjr.gpx'
#         , '../data/ski_20130213_sjr.gpx'
#         , '../data/ski_20130214_sjr.gpx'
#         , '../data/ski_20130215_sjr.gpx'
#         , '../data/ski_20130216_sjr.gpx')
readData('../data/ski_20130217_sjr.gpx'
         , '../data/ski_20130218_sjr.gpx'
         , '../data/ski_20130219_sjr.gpx'
         , '../data/ski_20130220_sjr.gpx'
         , '../data/ski_20130221_sjr.gpx'
         , '../data/ski_20130222_sjr.gpx')
#readData('../data/ski_20130220_sjr.gpx', '../data/ski_20130220_mr.gpx')
pyglet.app.run()
    