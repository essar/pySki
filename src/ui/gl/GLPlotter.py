'''
Created on 16 Nov 2012

@author: sroberts
'''
from pyglet.gl import *
import ui.gl

# Create config & data objects
glCfg = ui.gl.SkiGLPlotConfig()
glData = ui.gl.SkiGLPlotData()
    
# Create a new window
win = pyglet.window.Window(width=glCfg.window_width, height=glCfg.window_height)
    

@win.event
def on_draw():
    # Clear buffers and reset transforms
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
        
    # Adjust for margin
    glTranslatef(glCfg.window_xmargin, glCfg.window_ymargin, 0.0)
        
    # Scale to fit window
    glCfg.update_scales(win.width, win.height) # Apply scaling rules
    glScalef(glCfg.scale_x, glCfg.scale_y, glCfg.scale_z)
        
    # Rotate about X axis
    #glRotatef(-90.0, 10.0, 0.0, 0.0)
        
    # Draw plot elements as lines
    glData.vertex_list.draw(GL_LINE_STRIP)
    
    glFlush()


@win.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
        
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #gluPerspective(70, 1.0 * width/height, 0.1, 1000.0)
    glOrtho(0, width, 0, height, -1000, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
        
    return True


# One-time GL setup functions
def setup():
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glEnable(GL_DEPTH_TEST)
    
    
def update(dt):
    if glData.idx_end < glData.vlen:
        # Increment end index
        glData.idx_end = glData.idx_end + glCfg.draw_step
        
        # Update vertex data
        glData.refresh_vertex_list()
    
    
def drawSkiGLPlot():
    # Call one-off set up
    setup()
    
    # If in partial mode, call update function
    if glData.b_partial:
        pyglet.clock.schedule_interval(update, 1.0 / glCfg.draw_fps)
        print 'Update event scheduled'
    
    # Start pyglet main thread
    pyglet.app.run()
