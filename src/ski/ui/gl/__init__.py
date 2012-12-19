import GLRenderer
import pyglet.graphics
import ski.data as d

class SkiGLPlotConfig:
    ''' Class containing configurable properties for a GL plot.'''
    
    animate = True
    
    base_bg_colour_4f = (0.1, 0.1, 0.15, 0.1)
    base_depth = -1
    
    draw_fps = 25
    draw_step = 10
    
    plot_depth = 1
    plot_drawmode = '2D'
    plot_height = 0
    plot_width = 0
    
    scale_constrain = False
    scale_stretch = True
    scale_x = 1.0
    scale_y = 1.0
    scale_z = 1.0
    
    show_sprite = True
    
    show_status_panel = True
    status_height = 30
    
    view_x = 0
    view_y = 0
    view_z = 0
    
    window_fullscreen = False
    window_height = 600
    window_width = 800
    window_xmargin = 2
    window_ymargin = 2
    
    def update_scales(self, window_width, window_height):
        if self.scale_stretch:
            # Update scale factors to make plot fill window
            self.scale_x = float(window_width - (2 * self.window_xmargin)) / float(max(1, self.plot_width))
            self.scale_y = float(window_height - (self.status_height if self.show_status_panel else 0) - (2 * self.window_ymargin)) / float(max(1, self.plot_height))
        if self.scale_constrain:
            # Update scale factors so they scale x:X
            self.scale_x = self.scale_y = min(self.scale_x, self.scale_y)
            
            
class SkiGLPlotData:
    ''' Class containing data items used in a GL plot. '''
    
    point_data = []
    
    #vertex_list = pyglet.graphics.vertex_list_indexed(0, 'c3f', 'v3i')
    index_data = []
    colour_data = ('c3f', [])
    vertex_data = ('v3i', [])
    vlen = 0
    
    #b_partial = False
    draw_idxs = []
    idx_start = 0
    idx_end = 2
    
    def last_point(self):
        return self.point_data[min(len(self.point_data), self.idx_end) - 1]

    def get_status_text(self):
        #return '[ {:%d/%m/%Y %H:%M:%S %Z} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>2.1f}km/h ]'.format(
        return '[ {:d} ] [ Mode: {:4s} ] [ Altitude: {:4,d}m ] [ Speed: {:>2.1f}km/h ]'.format(
                        d.p_TS(self.last_point())
                      , d.p_Mode(self.last_point())
                      , d.p_A(self.last_point())
                      , d.p_S(self.last_point())
                      )
    
    def build_colours(self, cData):
        cVals = []
        for v in cData:
            if v == 'STOP':
                (r, g, b) = (1.0, 1.0, 1.0)
            if v == 'LIFT':
                (r, g, b) = (0.0, 0.0, 1.0)
            if v == 'SKI':
                (r, g, b) = (1.0, 0.0, 0.0)
            
            cVals.append(r)
            cVals.append(g)
            cVals.append(b)
        self.colour_data = ('c3f', cVals)
            
        
    def build_coloursa(self, cData):    
        # Calculate boundary values
        minV = min(cData)
        maxV = max(cData)

        cVals = []
        for v in cData:
            (r, g, b) = GLRenderer.getColourValue(minV, maxV, v)
            cVals.append(r)
            cVals.append(g)
            cVals.append(b)
        self.colour_data = ('c3f', cVals)
    
    
    def build_vertex_list(self):
        # Build indices list
        self.update_indices()
        
        # Create GL vertex list
        self.vertex_list = pyglet.graphics.vertex_list_indexed(self.vlen
                            , self.index_data
                            , self.vertex_data
                            , self.colour_data
                            )
   
    
    def draw_all(self):
        self.idx_start = 0
        self.idx_end = self.vlen
        self.refresh_vertex_list()
        
    
    def draw_reset(self):
        self.idx_start = 0
        self.idx_end = 2
        self.refresh_vertex_list()
    
    
    def load_xy_plot(self, pdata, xyF, cF):
        self.point_data = pdata

        # Build flat array of vertex values        
        vVals = [b for a in xyF(pdata) for b in a]
        
        self.vertex_data = ('v2i', vVals)
        self.vlen = len(pdata)
        self.build_colours(cF(pdata))
        
        self.build_vertex_list()
        
    
    def load_xyz_plot(self, pdata, xyzF, cF):
        self.point_data = pdata
        
        xyzdata = xyzF(pdata)
        # Get minimum X, Y & Z values
        minX = min(map(lambda ((x, y), z): x, xyzdata))
        minY = min(map(lambda ((x, y), z): y, xyzdata))
        minZ = min(map(lambda ((x, y), z): z, xyzdata))
    
        # Build list of vertex coordinates
        vVals = []
        for ((x, y), z) in xyzdata:
            vVals.append(int(x - minX))
            vVals.append(int(y - minY))
            vVals.append(int(z - minZ))
            
        self.vlen = len(pdata)
        self.vertex_data = ('v3i', vVals)
        self.build_colours(cF(pdata))
        self.build_vertex_list()
    

    def refresh_vertex_list(self):
        # Update indices list
        self.update_indices()
        # Calculate lengths
        vLen = self.vertex_list.get_size()
        iLen = len(self.index_data)
        # Resize vertex list
        self.vertex_list.resize(vLen, iLen)
        # Set list elements
        self.vertex_list.indices = self.index_data
    
    
    def update_indices(self):
        # Ensure end is at least 2 and does not exceed number of datum points
        self.idx_end = max(2, min(self.vlen, self.idx_end))
        # Update index data
        self.index_data = range(self.idx_start, self.idx_end - 1)
