'''
Created on 16 Nov 2012

@author: sroberts
'''

import pyglet
import io.GSDLoader
import data.preprocessor
import data.processor
import data as d
from data.skitrack import SkiTrack
from ui.gl import GLPlotter

glCfg = GLPlotter.glCfg
glData = GLPlotter.glData

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
    
    # Calculate sensible altitude scaling
    altScale = float(abs(hdr.hiAlt - hdr.loAlt)) / 1000.0
    glCfg.scale_z = altScale
    glCfg.plot_drawmode = '2D'
    glCfg.animate = True
    glCfg.show_status_panel = True

    # Generate list of coordinates
    appData = [x.as_tuple() for x in all_data.data]

    # Generate list of coordinates
    glData.load_xy_plot(appData, d.ps_Cart_r, d.ps_Modes)

    # Calculate plot size
    glCfg.plot_width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*hdr.area)
    glCfg.plot_height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*hdr.area)
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(appData), glCfg.plot_width, glCfg.plot_height)


# Code a-go-go
#readData('../data/ski_11-02-2012_sjr_20120211.csv')
readData('../data/sjr_20120211.gsd')
GLPlotter.drawSkiGLPlot()    
pyglet.app.run()
    