'''
Created on 19 Dec 2012

@author: sroberts
'''

import logging as log

import pyglet
import pyglet.graphics as gl

import keyhandler
from plotcfg import PlotCfg

# Load fonts
pyglet.font.add_file('../resources/saxmono.ttf')
status_height = 30

win = pyglet.window.Window()


class GLPlot:
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.cfg = PlotCfg()
        
        self.playing = True
        self.draw_idx = 0
        self.plot_idx = 0
        
        # Live transformations
        self.live_zoom_x = self.live_zoom_y = self.live_zoom_z = 1
        self.live_tx = self.live_ty = self.live_tz = 0
    
    
    def _build_vertex_list(self, plotdata):
        if type(plotdata.vertices_list) is not tuple:
            raise ValueError('Vertex data has not yet been compiled')
        if type(plotdata.colours_list) is not tuple:
            raise ValueError('Colour data has not yet been compiled')
        
        (vlen, vs) = plotdata.vertices_list
        (clen, cs) = plotdata.colours_list
        assert(vlen == clen)
        
        # Create GL vertex list
        vertex_list = pyglet.graphics.vertex_list_indexed(vlen
                        , range(vlen)
                        , ('v2i', vs)
                        , ('c3f', cs)
        )
        return vertex_list    
    
        
    def _calc_scales(self):
        if self.cfg.scale_stretch:
            # Update scale factors to make plot fill window
            viewWidth = float(win.width
                              - (2 * self.cfg.window_margin_x)
            )
            viewHeight = float(win.height
                              - (status_height if self.cfg.show_status_bar else 0)
                              - (2 * self.cfg.window_margin_y)
            )
            self.cfg.scale_x = float(viewWidth / float(max(1, self.cfg.plot_width)))
            self.cfg.scale_y = float(viewHeight / float(max(1, self.cfg.plot_height)))
        if self.cfg.scale_constrain:
            # Update scale factors so they scale x:X
            self.cfg.scale_x = self.cfg.scale_y = min(self.cfg.scale_x, self.cfg.scale_y)
            
        return (self.cfg.scale_x, self.cfg.scale_y, self.cfg.scale_z)
    
    
    def _draw_background(self):
        gl.glPushMatrix()
        
        # Scale to fit window
        gl.glScalef(*self._calc_scales())
        
        width = self.cfg.plot_width
        height = self.cfg.plot_height
        depth = -1
        
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        gl.glColor4f(*self.cfg.bg_colour_4f)
        
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3i(0, 0, depth)
        gl.glVertex3i(0, height, depth)
        gl.glVertex3i(width, height, depth)
        gl.glVertex3i(width, 0, depth)
        gl.glEnd()
        
        gl.glPopMatrix()
    
    
    def _draw_plot(self):
        
        vl = self.vlists[self.plot_idx]
        
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        vl.draw(gl.GL_LINE_STRIP)
        
        
    def _draw_status_bar(self):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    
        # Clear transforms
        gl.glLoadIdentity()
        
        #py_fps = pyglet.app.clock.get_fps()
        #lbl_status.text = glData.get_status_text()
        #lbl_status.draw()
        
        #lbl_fps.text =  '[{0:3.3f}fps]'.format(py_fps)
        #lbl_fps.draw()
        
    def _init_window(self):
        
        win.set_fullscreen(self.cfg.window_fullscreen)
        if not self.cfg.window_fullscreen:
            win.set_size(self.cfg.window_width, self.cfg.window_height)
    
    
    def _update_vertex_list(self, vertex_list):
        # Update vertex data
        idxs = range(self.draw_idx)
                
        # Calculate lengths
        vLen = vertex_list.get_size()
        iLen = len(idxs)
            
        # Resize vertex list
        vertex_list.resize(vLen, iLen)
            
        # Set list elements
        vertex_list.indices = idxs

    
    def animation_pause(self):
        self.playing = False
        log.info('[GLPlot] Animation paused')
    
    def animation_play(self):
        self.playing = True
        log.info('[GLPlot] Animation playing')
    
    def pan_view(self, xShift, yShift, zShift):
        self.live_tx += xShift
        self.live_ty += yShift
        self.live_tz += zShift
        log.info('[GLPlot] Panning by (%d, %d, %d) to (%d, %d, %d)', xShift, yShift, zShift, self.live_tx, self.live_ty, self.live_tz)
    
    def pan_view_down(self, shift):
        self.pan_view(0, shift, 0)  
        
    def pan_view_left(self, shift):
        self.pan_view(shift, 0, 0)  
    
    def pan_view_right(self, shift):
        self.pan_view(-shift, 0, 0)  
        
    def pan_view_up(self, shift):
        self.pan_view(0, -shift, 0)  

    def pan_view_reset(self):
        self.live_tx = 0
        self.live_ty = 0
        self.live_tz = 0
        log.info('[GLPlot] Panning values reset')
        
    def pan_view_to(self, cX, cY, cZ):
        self.live_tx = cX
        self.live_ty = cY
        self.live_tz = cZ
        log.info('[GLPlot] Panning view to to (%d, %d, %d)', cX, cY, cZ)
    
    def zoom_view(self, zFac):
        if zFac == 0:
            # Reset zoom factors to 1
            self.live_zoom_x = 1.0
            self.live_zoom_y = 1.0
            self.live_zoom_z = 1.0
            log.info('[GLPlot] Zoom factors reset')
        else:
            self.live_zoom_x *= zFac
            self.live_zoom_y *= zFac
            self.live_zoom_z *= zFac
            log.info('[GLPlot] Zooming by %.1f to (%.1f, %.1f, %.1f)', zFac, self.live_zoom_x, self.live_zoom_y, self.live_zoom_z)

    def zoom_view_in(self, zFac = 2.0):
        self.zoom_view(zFac)
        
    def zoom_view_out(self, zFac = 2.0):
        self.zoom_view(1.0 / zFac)
        
    def zoom_view_reset(self):
        self.zoom_view(0.0)
        
    
    ###########################################################################
    # PUBLIC FUNCTIONS
    ###########################################################################
    
    def draw(self):
        # Adjust for margin
        gl.glTranslatef(self.cfg.window_margin_x, self.cfg.window_margin_y, 0.0)
        # Adjust for status bar
        gl.glTranslatef(0.0, (30.0 if self.cfg.show_status_bar else 0), 0.0)
            
        # Draw base plane
        self._draw_background()
            
        # Adjust for view
        gl.glTranslatef(self.live_tx, self.live_ty, self.live_tz)
        # Scale to fit window
        gl.glScalef(*self._calc_scales())
        
        # Compute centre point
        cx = float((self.cfg.plot_width / 2.0) - (self.live_tx / self.cfg.scale_x))
        cy = float((self.cfg.plot_height / 2.0) - (self.live_ty / self.cfg.scale_y))
        #cz = float(glCfg.plot_depth / 2.0)
            
        # Scale according to zoom factors about centre point
        gl.glTranslatef(cx, cy, 0.0)
        gl.glScalef(self.live_zoom_x, self.live_zoom_y, self.live_zoom_z)
        gl.glTranslatef(-cx, -cy, 0.0)
                
        # Rotate about X axis
        #glRotatef(-90.0, 10.0, 0.0, 0.0)
        
        # Draw axis
            
        # Draw plot elements as lines
        self._draw_plot()
        
        if self.cfg.show_status_panel:
            self._draw_status_bar()
    
    
    def get_last_xy(self):
        last_x = self.plot_data[self.plot_idx].x_data[self.draw_idx]
        last_y = self.plot_data[self.plot_idx].y_data[self.draw_idx]
        return (last_x, last_y)
    
    
    def get_last_xyx(self):
        last_x = self.plot_data[self.plot_idx].x_data[self.draw_idx]
        last_y = self.plot_data[self.plot_idx].y_data[self.draw_idx]
        last_z = self.plot_data[self.plot_idx].z_data[self.draw_idx]
        return (last_x, last_y, last_z)
    
    
    def reset(self):
        self.draw_idx = 0
        self._update_vertex_list(self.vlists[self.plot_idx], self.draw_idx)
    
    def show(self, plotData):
        self.plot_data = plotData
        self.vlists = [self._build_vertex_list(d) for d in plotData]
        
        self._init_window()
        
        # One-time GL setup functions
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glEnable(gl.GL_DEPTH_TEST)
        
        # If in animate mode, call update function
        if self.cfg.animate:
            self.reset()
            pyglet.clock.schedule_interval(self.update, 1.0 / self.cfg.animate_fps)
    
        # Start pyglet main thread
        pyglet.app.run()
    
        
    def update(self, dt):
        # Update if we're running and there are indexes left
        if self.playing and self.draw_idx < self.vlists[self.plot_idx].vertex_count():
            # Increment end index
            self.draw_idx += self.cfg.animate_step
            self._update_vertex_list(self.vlists[self.plot_idx], self.draw_idx)
            
            
###############################################################################
# WINDOW EVENT FUNCTIONS
###############################################################################
            
@win.event
def on_draw():
    # Clear buffers and reset transforms
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glLoadIdentity()
            
    plot.draw()
        
    gl.glFlush()    
    
        
@win.event
def on_key_press(symbol, modifiers):
    keyhandler.handle_key_press(symbol, modifiers, plot)


@win.event
def on_key_release(symbol, mods):
    pass

    
@win.event
def on_resize(width, height):
    gl.glViewport(0, 0, width, height)
            
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    #gluPerspective(70, 1.0 * width/height, 0.1, 1000.0)
    gl.glOrtho(0, width, 0, height, -1000, 1000)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
            
    return True


plot = GLPlot()