'''
Created on 19 Dec 2012

@author: sroberts
'''

import logging
log = logging.getLogger(__name__)

import pyglet
import pyglet.graphics as gl

import keyhandler
from plotcfg import PlotCfg

# Load fonts
pyglet.font.add_file('../resources/saxmono.ttf')


class GLPlot:
    '''
      Holds data relating to a plot to draw within a GL window.
    '''
    
    def __init__(self, cfg=PlotCfg()):
        '''
        Constructor
        '''
        self.cfg = cfg
        self.cfg = PlotCfg()
        self.status = GLPlotStatusBar(self.cfg.window_width)
        
        self.playing = True
        self.draw_idx = 0
        self.plot_idx = 0
        
        self.vx_dom = pyglet.graphics.vertexdomain.create_domain('v2i','c3f')
        
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
        vertex_list = self.vx_dom.create(vlen)
        vertex_list.vertices = vs
        vertex_list.colors = cs
        
        log.info('Compiled vertex list of %d vertices', vlen)
        return vertex_list
    
    
    def _draw_axis(self):
        gl.glPushMatrix()
        
        # Scale to fit window
        self.cfg._update_scaling()
        
        width = int(self.cfg.plot_width)
        height = int(self.cfg.plot_height)
        log.debug('Drawing axis; width=%d, height=%d', width, height)
        
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3i(0, 0, 0)
        gl.glVertex3i(width, 0, 0)
        
        gl.glVertex3i(0, 0, 0)
        gl.glVertex3i(0, height, 0)
        
        gl.glEnd()
        
        for (_lbl, pos) in self.plot_data[self.plot_idx].x_axis_markers:
            gl.glBegin(gl.GL_LINES)
            gl.glVertex3i(int(pos), 0, 0)
            gl.glVertex3i(int(pos), -1, 0)
            gl.glEnd()
            log.debug('Drawing x-axis marker at %d', int(pos))
            
            if _lbl is not None:
                gl.glPushMatrix()
                gl.glLoadIdentity()
                pyglet.text.Label(str(_lbl), font_name='Arial', font_size=8, x=pos, y=-0.5).draw()
                gl.glPopMatrix()
            
        for (_lbl, pos) in self.plot_data[self.plot_idx].y_axis_markers:
            gl.glBegin(gl.GL_LINES)
            gl.glVertex3i(0, int(pos), 0)
            gl.glVertex3i(-1, int(pos), 0)
            gl.glEnd()
            log.debug('Drawing y-axis marker at %d', int(pos))
        
        gl.glPopMatrix()
        
    
    def _draw_background(self):
        gl.glPushMatrix()
        
        # Scale to fit window
        gl.glScalef(*self.cfg._update_scaling())
        
        width = int(self.cfg.plot_width)
        height = int(self.cfg.plot_height)
        depth = -1
        log.debug('Drawing background; width=%d, height=%d, depth=%d', width, height, depth)
        
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
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        self.vx_dom.draw(gl.GL_LINE_STRIP)
        
        
    def _draw_status_bar(self):
        if self.cfg.status_txt is not None:
            if self.cfg.status_values_f is NotImplemented:
                status_text = self.cfg.status_txt
            else:
                status_text = self.cfg.status_txt.format(*self.cfg.status_values_f(self.draw_idx))
        
        self.status.draw(status_text)
        
    
    def _get_current_track(self):
        if self.index_data is None:
            return None
        # Calculate current track
        currentTrack = 0
        while(self.index_data[currentTrack].idx < self.draw_idx):
            currentTrack += 1
        
        log.debug('Currently in track %d/%d', currentTrack, len(self.index_data))
        return currentTrack
        
        
    def _set_draw_idx(self, idx):
        min_idx = 2
        max_idx = max([len(p.v_data) for p in self.plot_data]) - 1
        
        self.draw_idx = max(min_idx, min(max_idx, idx))
        log.debug('draw_idx=%d', self.draw_idx)


    def _update_all_vertex_lists(self):
        for i in range(len(self.vlists)):
            # Update if we're running and there are indexes left
            if self.draw_idx < self.plot_data[i].vertices_list[0]:
                self._update_vertex_list(i)
                

    def _update_vertex_list(self, vlix):
        dx = self.draw_idx * 2
        vLen = self.draw_idx
        
        # Get vertex data
        vData = self.plot_data[vlix].vertices_list[1][:dx]
        assert(len(vData) == dx)
        log.debug('Resizing vertex list %d, vLen=%d', vlix, vLen)
        
        # Resize vertex list
        vl = self.vlists[vlix]
        vl.resize(vLen)
        log.debug('Vertex list %d length: %d', vlix, vl.get_size())
        
        # Set list elements
        vl.vertices = vData
        

    def animation_pause(self):
        self.playing = False
        log.info('Animation paused')
    
    def animation_play(self):
        self.playing = True
        log.info('Animation playing')
    
    def pan_view(self, xShift, yShift, zShift):
        self.live_tx += xShift
        self.live_ty += yShift
        self.live_tz += zShift
        log.info('Panning by (%d, %d, %d) to (%d, %d, %d)', xShift, yShift, zShift, self.live_tx, self.live_ty, self.live_tz)
    
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
        log.info('Panning values reset')
        
    def pan_view_to(self, cX, cY, cZ):
        self.live_tx = cX
        self.live_ty = cY
        self.live_tz = cZ
        log.info('Panning view to (%d, %d, %d)', cX, cY, cZ)
    
    def step_backward(self, step):
        self._set_draw_idx(self.draw_idx - step)
        self._update_all_vertex_lists()
        log.info('Stepped backward by %d', step)
    
    def step_forward(self, step):
        self._set_draw_idx(self.draw_idx + step)
        self._update_all_vertex_lists()
        log.info('[GLPlot] Stepped forward by %d', step)
    
    def step_track_backward(self, step=1):
        # Calculate current track
        currentTrack = self._get_current_track()
        if currentTrack is None:
            log.warn('Cannot step track backward without track index')
            return
            
        newTrack = currentTrack - step
            
        # Get index of next track
        newIndex = self.index_data[newTrack].idx
        log.debug('Stepping from track %d to %d', currentTrack, newTrack)

        self._set_draw_idx(newIndex)
        self._update_all_vertex_lists()
        log.info('Stepped backward to %d', newIndex)
        
    def step_track_forward(self, step=1):
        # Calculate current track
        currentTrack = self._get_current_track()
        if currentTrack is None:
            log.warn('Cannot step track forward without track index')
            return

        newTrack = currentTrack + step
            
        # Get index of next track
        newIndex = self.index_data[newTrack].idx
        log.debug('Stepping from track %d to %d', currentTrack, newTrack)

        self._set_draw_idx(newIndex)
        self._update_all_vertex_lists()
        log.info('Stepped forward to %d', newIndex)
    
    def zoom_view(self, zFac):
        if zFac == 0:
            # Reset zoom factors to 1
            self.live_zoom_x = 1.0
            self.live_zoom_y = 1.0
            self.live_zoom_z = 1.0
            log.info('Zoom factors reset')
        else:
            self.live_zoom_x *= zFac
            self.live_zoom_y *= zFac
            self.live_zoom_z *= zFac
            log.info('Zooming by %.1f to (%.1f, %.1f, %.1f)', zFac, self.live_zoom_x, self.live_zoom_y, self.live_zoom_z)

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
        # Adjust for axis bar
        gl.glTranslatef((20.0 if self.cfg.show_axis else 0), (20.0 if self.cfg.show_axis else 0), 0.0)
        # Adjust for status bar
        gl.glTranslatef(0.0, (self.cfg.status_height if self.cfg.show_status_bar else 0), 0.0)
            
        # Draw base plane
        self._draw_background()
            
        # Adjust for view
        gl.glTranslatef(self.live_tx, self.live_ty, self.live_tz)
        # Scale to fit window
        gl.glScalef(*self.cfg._update_scaling())
        
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
        if self.cfg.show_axis:
            self._draw_axis()
            
        # Draw plot elements as lines
        self._draw_plot()
        
        if self.cfg.show_status_bar:
            self._draw_status_bar()
    
    
    def get_last_xy(self):
        last_x = self.plot_data[self.plot_idx].x_data[self.draw_idx]
        last_y = self.plot_data[self.plot_idx].y_data[self.draw_idx]
        return (last_x, last_y)
    
    
    def get_last_xyz(self):
        last_x = self.plot_data[self.plot_idx].x_data[self.draw_idx]
        last_y = self.plot_data[self.plot_idx].y_data[self.draw_idx]
        last_z = self.plot_data[self.plot_idx].z_data[self.draw_idx]
        return (last_x, last_y, last_z)
    
    
    def reset(self):
        self.draw_idx = 2
        self._update_all_vertex_lists()
    
    
    def show(self, plotData, plotIndex=None):
        self.plot_data = plotData
        self.index_data = plotIndex
        self.vlists = [self._build_vertex_list(d) for d in plotData]
        
        #self._init_window()
        
        # One-time GL setup functions
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glEnable(gl.GL_DEPTH_TEST)
        
        # If in animate mode, call update function
        if self.cfg.animate:
            log.info('Starting animation')
            self.reset()
            pyglet.clock.schedule_interval(self.update, 1.0 / self.cfg.animate_fps)
    
        
    def update(self, dt):
        if self.playing:
            # Increment end index
            self._set_draw_idx(self.draw_idx + self.cfg.animate_step)
            # Update if we're running and there are indexes left
            self._update_all_vertex_lists()
   
   
class GLPlotStatusBar():
    
    def __init__(self, win_width):
        # Create label components
        self.lbl_fps = pyglet.text.Label(text='[FPS]'
                , font_name='saxMono'
                , font_size=10
                , x=win_width - 10
                , anchor_x='right'
                , anchor_y='bottom'
        )
        self.lbl_status = pyglet.text.Label(text='pySki'
                , font_name='saxMono'
                , font_size=10
                , x=10
                , anchor_x='left'
                , anchor_y='bottom'
        ) 
    
    
    def draw(self, status_text):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    
        # Clear transforms
        gl.glLoadIdentity()
        
        # Update status label
        if status_text is not None:
            self.lbl_status.text = status_text
        self.lbl_status.draw()
        
        # Update FPS label
        py_fps = pyglet.app.clock.get_fps()
        self.lbl_fps.text =  '[{0:3.3f}fps]'.format(py_fps)
        self.lbl_fps.draw()
   
   
    def set_width(self, win_width):
        # Move FPS label to stay right aligned
        self.lbl_fps.x = win_width - 10
 
 
class GLPlotWindow(pyglet.window.Window):
    
    def __init__(self, plot):
        super(GLPlotWindow, self).__init__()
        self.plot = plot

        self.set_fullscreen(self.plot.cfg.window_fullscreen)
        if not self.plot.cfg.window_fullscreen:
            self.set_size(self.plot.cfg.window_width, self.plot.cfg.window_height)
    
    
    ###############################################################################
    # WINDOW EVENT FUNCTIONS
    ###############################################################################
                
    def on_draw(self):
        # Clear buffers and reset transforms
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
                
        self.plot.draw()
            
        gl.glFlush()    
        
            
    def on_key_press(self, symbol, modifiers):
        keyhandler.handle_key_press(symbol, modifiers, self)
    
    
    def on_key_release(self, symbol, mods):
        pass
    
        
    def on_resize(self, width, height):
        self.plot.cfg.window_width = width
        self.plot.cfg.window_height = height
        
        gl.glViewport(0, 0, width, height)
                
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        #gluPerspective(70, 1.0 * width/height, 0.1, 1000.0)
        gl.glOrtho(0, width, 0, height, -1000, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        self.plot.status.set_width(width)        
                
        return True


def create_plot_window(plot=GLPlot(), plotData=None, plotIndex=None):
    win = GLPlotWindow(plot)
    if plotData is not None:
        log.info('Showing plot')
        plot.show(plotData, plotIndex)
    
    return win
