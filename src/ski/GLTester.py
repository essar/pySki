'''
Created on 16 Nov 2012

@author: sroberts
'''

import pyglet
import io.CSVLoader
import io.GSDLoader
import data as d
import data.Processor
import data.Tracks as xtr
from ui.gl import GLPlotter

glCfg = GLPlotter.glCfg
glData = GLPlotter.glData

# Load data from file
def readData(filename):
    # Read CSV data from file
    #ioData = io.CSVLoader.loadCSVFile(filename)
    # Read GSD data from file
    ioData = io.GSDLoader.load_gsd_file(filename)
    
    
    data.Processor.set_tz('US/Mountain')
    data.Processor.process(ioData)
    
    appData = data.Processor.pData.all_points

    # Calculate track summary data
    ts = xtr.SkiTrackHeader(appData)
    # Output summary
    ts.print_track_header()
    
    # Calculate sensible altitude scaling
    altScale = float(abs(ts.hiAlt - ts.loAlt)) / 1000.0
    glCfg.scale_z = altScale
    glCfg.plot_drawmode = '2D'
    glCfg.animate = True
    glCfg.show_status_panel = True

    # Generate list of coordinates
    glData.load_xy_plot(appData, d.ps_Cart_r, d.ps_Ss)

    # Calculate plot size
    glCfg.plot_width = (lambda (x1, y1), (x2, y2): abs(x2 - x1))(*ts.area)
    glCfg.plot_height = (lambda (x1, y1), (x2, y2): abs(y2 - y1))(*ts.area)
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(appData), glCfg.plot_width, glCfg.plot_height)


# Code a-go-go
#readData('../data/ski_11-02-2012_sjr_20120211.csv')
readData('../data/sjr_20120211.gsd')
GLPlotter.drawSkiGLPlot()    
pyglet.app.run()
    