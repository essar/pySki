'''
Created on 16 Nov 2012

@author: sroberts
'''
from pyglet.gl import *
import ui.gl

# Create config & data objects
glCfg = ui.gl.SkiGLPlotConfig()
glData = ui.gl.SkiGLPlotData()

# Load fonts
pyglet.font.add_file('../resources/saxmono.ttf')
    
# Create a new window
win = pyglet.window.Window(width=glCfg.window_width, height=glCfg.window_height)

# Create status labels
lbl_status = pyglet.text.Label(text='Essar Ski Data'
                             , font_name='saxMono'
                             , font_size=10
                             , x=10
                             , y=8
                             #, bold=True
                             , anchor_x='left'
                             , anchor_y='bottom'
                             )  

lbl_fps = pyglet.text.Label(text='[fps]'
                             , font_name='saxMono'
                             , font_size=10
                             , x=win.width - 10
                             , y=8
                             , anchor_x='right'
                             , anchor_y='bottom'
                             )  

# Live transformations
live_scale_x = live_scale_y = live_scale_z = 1
live_tx = live_ty = live_tz = 0

def draw_status():
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    # Clear transforms
    glLoadIdentity()
    
    py_fps = pyglet.app.clock.get_fps()
    lbl_status.text = glData.get_status_text()
    lbl_status.draw()
    
    lbl_fps.text =  '[{0:3.3f}fps]'.format(py_fps)
    lbl_fps.draw()
    

@win.event
def on_draw():
    # Clear buffers and reset transforms
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
        
    # Adjust for margin
    glTranslatef(glCfg.window_xmargin, glCfg.window_ymargin, 0.0)
    # Adjust for view
    glTranslatef(glCfg.view_x + live_tx, glCfg.view_y + live_ty, glCfg.view_z + live_tz)
    # Adjust for status bar
    glTranslatef(0.0, (glCfg.status_height if glCfg.show_status_panel else 0), 0.0)
    
        
    # Scale to fit window
    glCfg.update_scales(win.width, win.height) # Apply scaling rules
    glScalef(glCfg.scale_x * live_scale_x, glCfg.scale_y * live_scale_y, glCfg.scale_z * live_scale_z)
        
    # Rotate about X axis
    #glRotatef(-90.0, 10.0, 0.0, 0.0)
    
    # Draw base plane
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glColor4f(*glCfg.base_bg_colour_4f)
    glBegin(GL_QUADS)
    glVertex3i(0, 0, glCfg.base_depth)
    glVertex3i(0, glCfg.plot_height, glCfg.base_depth)
    glVertex3i(glCfg.plot_width, glCfg.plot_height, glCfg.base_depth)
    glVertex3i(glCfg.plot_width, 0, glCfg.base_depth)
    glEnd()
        
    # Draw plot elements as lines
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glData.vertex_list.draw(GL_LINE_STRIP)
    
    if glCfg.show_status_panel:
        draw_status()
    
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
    
    # If in animate mode, call update function
    if glCfg.animate:
        pyglet.clock.schedule_interval(update, 1.0 / glCfg.draw_fps)
    
    # Start pyglet main thread
    pyglet.app.run()
