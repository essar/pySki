'''
Created on 16 Nov 2012

@author: sroberts
'''

import logging as log

import pyglet
import io.GSDLoader
import data.preprocessor
import data.processor

import ui.gl.linearrenderer as renderer
from ui.gl.plotdata import PlotData
from ui.gl.glplot import plot


# Load data from file
def readData(filename):
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
    
    #xyData = [(stp.x, stp.y) for stp in all_data.data]
    #vData = [stp.spd for stp in all_data.data]
    
    #glData = PlotData.build_xy_plot(xyData, vData)
    #glData.compile_vertex_data(renderer.getColourValue, 2)
    
    # Calculate plot size
    #plot.cfg.plot_width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*hdr.area)
    #plot.cfg.plot_height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*hdr.area)
    
    
    xData = [stp.ts for stp in all_data.data]
    vData = [stp.spd for stp in all_data.data]
    
    glData = PlotData.build_linear_plot(xData, vData, ySmoothing=60)
    glData.compile_vertex_data(renderer.getColourValue, 2)
    
    # Calculate plot size
    plot.cfg.plot_width = max(xData) - min(xData)
    plot.cfg.plot_height = max(vData) - min(vData)
    
    
    # Calculate sensible altitude scaling
    altScale = float(abs(hdr.hiAlt - hdr.loAlt)) / 1000.0
    plot.cfg.scale_z = altScale
    plot.cfg.drawmode = '2D'
    plot.cfg.animate = False
    plot.cfg.show_status_panel = False
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(xData), plot.cfg.plot_width, plot.cfg.plot_height)
    plot.show([glData])


# Config log levels
log.basicConfig(level=log.INFO)

# Code a-go-go
readData('../data/sjr_20120211.gsd')
pyglet.app.run()
    