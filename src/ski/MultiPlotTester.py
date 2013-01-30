'''
Created on 16 Nov 2012

@author: sroberts
'''

import logging as log

import pyglet
import io.GSDLoader
import data.preprocessor
import data.processor

#import ui.gl.moderenderer as renderer
import ui.gl.ninepointrenderer as renderer
from ui.gl.plotdata import PlotData
from ui.gl.glplot import plot


# Load data from file
def readData(filename1, filename2):
    # Read GSD data from file
    gsdData1 = io.GSDLoader.load_gsd_file(filename1)
    gsdData2 = io.GSDLoader.load_gsd_file(filename2)
    
    # Pre-process
    dList1 = data.preprocessor.preprocess(gsdData1)
    dList2 = data.preprocessor.preprocess(gsdData2)

    # Set time zone
    data.processor.set_tz('US/Mountain')
    
    # Process data
    all_data = data.processor.process(dList1, dList2)
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
    #vData = [stp.spd for stp in all_data.data]
    #vData = [stp.mode for stp in all_data.data]
    glData = PlotData.build_xy_plot(xyData, vData)
    glData.compile_vertex_data(renderer.relColourValue, 2)
    
    # Calculate plot size
    plot.cfg.plot_width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*hdr.area)
    plot.cfg.plot_height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*hdr.area)
    
    
    # Calculate sensible altitude scaling
    altScale = float(abs(hdr.hiAlt - hdr.loAlt)) / 1000.0
    plot.cfg.scale_z = altScale
    plot.cfg.drawmode = '2D'
    plot.cfg.animate = True
    plot.cfg.show_status_bar = False
    
    #plot.cfg.status_txt = '[ {:%d/%m/%Y %H:%M:%S %Z} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>4.1f}km/h ]'
    #plot.cfg.status_values_f = lambda idx : (all_data.data[idx].loc_time
    #                  , all_data.data[idx].mode
    #                  , all_data.data[idx].alt
    #                  , all_data.data[idx].spd
    #)
    
    plot.show([glData]) 
    #plot.show([glData1, glData2]) 


# Config log levels
log.basicConfig(level=log.INFO)
log.getLogger('ski').setLevel(log.INFO)

# Code a-go-go
readData('../data/sjr_20120211.gsd', '../data/sjr_20120212.gsd')
pyglet.app.run()
    