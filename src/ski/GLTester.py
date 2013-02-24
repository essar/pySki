'''
Created on 16 Nov 2012

@author: sroberts
'''

import logging as log

import pyglet
#import io.GSDLoader
import io.GPXLoader
import data.preprocessor
import data.processor

import ui.gl.linearrenderer as renderer
import ui.gl.glplot as glplot
from ui.gl.plotdata import PlotData


# Load data from file
def readData(filename):
    # Read GSD data from file
    #gsdData = io.GSDLoader.load_gsd_file(filename)
    gpxData = io.GPXLoader.load_gpx_file(filename)
    
    # Pre process
    dList = data.preprocessor.preprocess(gpxData)

    # Set time zone
    data.processor.set_tz('US/Mountain')
    
    # Process data
    all_data = data.processor.process(dList)
    hdr = all_data.hdr
    hdr.print_track_header()
    
    return all_data

def show_altitude_plot(all_data):
    # Create plot window
    win = glplot.create_plot_window()
    plot = win.plot
    
    xData = [stp.ts for stp in all_data.data]
    yData = [stp.alt for stp in all_data.data]
    vData = [stp.spd for stp in all_data.data]
    
    glData = PlotData.build_linear_plot(xData, yData, vData)
    glData.compile_vertex_data(renderer.getColourValue, 2)
    
    # Calculate plot size
    plot.cfg.plot_width = max(xData) - min(xData)
    plot.cfg.plot_height = max(yData) - min(yData)
    
    # Calculate sensible altitude scaling
    plot.cfg.scale_z = 1
    plot.cfg.drawmode = '2D'
    plot.cfg.animate = False
    plot.cfg.show_status_bar = False
    plot.cfg.show_axis = True
    
    plot.cfg.status_txt = '[ {:%d/%m/%Y %H:%M:%S %Z} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>4.1f}km/h ]'
    plot.cfg.status_values_f = lambda idx : (all_data.data[idx].loc_time
                      , all_data.data[idx].mode
                      , all_data.data[idx].alt
                      , all_data.data[idx].spd
    )
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(vData), plot.cfg.plot_width, plot.cfg.plot_height)
    plot.show([glData])

def show_speed_plot(all_data):
    # Create plot window
    win = glplot.create_plot_window()
    plot = win.plot
    
    xData = [stp.ts for stp in all_data.data]
    yData = [stp.spd for stp in all_data.data]
    vData = [stp.alt for stp in all_data.data]
    
    glData = PlotData.build_linear_plot(xData, yData, vData, ySmoothing=50, xMarkers=1)
    glData.compile_vertex_data(renderer.getColourValue, 2)
    
    # Calculate plot size
    plot.cfg.plot_width = max(xData) - min(xData)
    plot.cfg.plot_height = max(yData) - min(yData)
    
    
    # Calculate sensible altitude scaling
    altScale = 1
    plot.cfg.scale_z = altScale
    plot.cfg.drawmode = '2D'
    plot.cfg.animate = False
    plot.cfg.show_status_bar = False
    
    plot.cfg.status_txt = '[ {:%d/%m/%Y %H:%M:%S %Z} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>4.1f}km/h ]'
    plot.cfg.status_values_f = lambda idx : (all_data.data[idx].loc_time
                      , all_data.data[idx].mode
                      , all_data.data[idx].alt
                      , all_data.data[idx].spd
    )
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(vData), plot.cfg.plot_width, plot.cfg.plot_height)
    plot.show([glData])
    

def show_xy_plot(all_data):
    # Create plot window
    plot = glplot.GLPlot()
    
    xyData = [(stp.x, stp.y) for stp in all_data.data]
    vData = [stp.spd for stp in all_data.data]
    
    glData = PlotData.build_xy_plot(xyData, vData)
    glData.compile_vertex_data(renderer.getColourValue, 2)
    
    # Calculate plot size
    plot.cfg.plot_width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*all_data.hdr.area)
    plot.cfg.plot_height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*all_data.hdr.area)
    
    # Calculate sensible altitude scaling
    altScale = float(abs(all_data.hdr.hiAlt - all_data.hdr.loAlt)) / 1000.0
    plot.cfg.scale_z = altScale
    plot.cfg.drawmode = '2D'
    plot.cfg.animate = True
    plot.cfg.window_fullscreen = True
    plot.cfg.show_marker = True
    plot.cfg.show_status_bar = True
    
    plot.cfg.status_txt = '[ {:%d/%m/%Y %H:%M:%S %Z} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>4.1f}km/h ]'
    plot.cfg.status_values_f = lambda idx : (all_data.data[idx].loc_time
                      , all_data.data[idx].mode
                      , all_data.data[idx].alt
                      , all_data.data[idx].spd
    )
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(xyData), plot.cfg.plot_width, plot.cfg.plot_height)
    
    # Create plot window
    glplot.create_plot_window(plot, [glData], data.processor.track_index)
    #plot.show([glData], data.processor.track_index)


# Config log levels
log.basicConfig(level=log.INFO)
log.getLogger('ski').setLevel(log.INFO)
#log.getLogger('data.processor').setLevel(log.DEBUG)

# Code a-go-go
#all_data = readData('../data/sjr_20120211.gsd')
all_data = readData('../data/ski_20130222_sjr.gpx')
#show_altitude_plot(all_data)
#show_speed_plot(all_data)
show_xy_plot(all_data)
pyglet.app.run()
