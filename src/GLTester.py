'''
Created on 16 Nov 2012

@author: sroberts
'''

import pyglet
import io.CSVLoader
import data as d
import data.Processor
import data.Tracks as xtr
from ui.gl import GLPlotter

glCfg = GLPlotter.glCfg
glData = GLPlotter.glData

# Load data from file
def readData(filename):
    # Read CSV data from file
    ioData = io.CSVLoader.loadCSVFile(filename)[:10000]
    appData = data.Processor.process(ioData)

    # Calculate track summary data
    ts = xtr.TrackSummary(ioData)
    # Output summary
    ts.print_summary()
    
    # Calculate sensible altitude scaling
    altScale = float(ts.altDelta) / 1000.0
    glCfg.scale_z = altScale
    glCfg.plot_drawmode = '2D'
    glData.b_partial = True
    glCfg.show_sprite = False
    glCfg.show_status_panel = True

    # Generate list of coordinates
    glData.load_xy_plot(appData, d.ps_Cart_r, d.ps_Ss)

    # Calculate plot size
    glCfg.plot_width = ts.sizeX
    glCfg.plot_height = ts.sizeY
    
    print 'Draw {0} points fitting {1}x{2}'.format(len(appData), glCfg.plot_width, glCfg.plot_height)


# Code a-go-go
readData('../data/ski_11-02-2012_sjr_20120211.csv')
GLPlotter.drawSkiGLPlot()    
pyglet.app.run()
    