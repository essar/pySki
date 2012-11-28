
import GLRenderer
import pyglet.graphics

class SkiGLPlotConfig:
    ''' Class containing configurable properties for a GL plot.'''
    
    draw_fps = 25
    draw_step = 10
    
    info_label_font_name = 'Arial'
    info_label_font_size = 20
    
    plot_depth = 1
    plot_drawmode = '2D'
    plot_height = 0
    plot_width = 0
    
    scale_constrain = False
    scale_stretch = True
    scale_x = 1.0
    scale_y = 1.0
    scale_z = 1.0
    
    show_info_panel = True
    show_sprite = True
    
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
            self.scale_y = float(window_height - (2 * self.window_ymargin)) / float(max(1, self.plot_height))
        if self.scale_constrain:
            # Update scale factors so they scale x:X
            self.scale_x = self.scale_y = max(self.scale_x, self.scale_y)
            
            
class SkiGLPlotData:
    ''' Class containing data items used in a GL plot. '''
    
    point_data = []
    
    #vertex_list = pyglet.graphics.vertex_list_indexed(0, 'c3f', 'v3i')
    index_data = []
    colour_data = ('c3f', [])
    vertex_data = ('v3i', [])
    vlen = 0
    
    b_partial = False
    draw_idxs = []
    idx_start = 0
    idx_end = 2
    
    def last_point(self):
        return self.point_data[min(len(self.point_data), self.idx_end) - 1]
    
    def last_altitude(self):
        (__ts, (__g, __c, __a, __s)) = self.point_data[min(len(self.point_data), self.idx_end) - 1]
        return __a
    
    def last_speed(self):
        (__ts, (__g, __c, __a, __s)) = self.point_data[min(len(self.point_data), self.idx_end) - 1]
        return __s
    
    def last_x(self):
        (__ts, (__g, (__x, __y), __a, __s)) = self.point_data[min(len(self.point_data), self.idx_end) - 1]
        return __x
    
    def last_y(self):
        (__ts, (__g, (__x, __y), __a, __s)) = self.point_data[min(len(self.point_data), self.idx_end) - 1]
        return __y
    
    
    def build_colours(self, cData):    
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
    
    
    def load_xy_plot(self, data, xyF, cF):
        self.point_data = data
        
        xydata = xyF(data)
        # Get minimum X & Y values
        minX = min(map(lambda (x, y): x, xydata))
        minY = min(map(lambda (x, y): y, xydata))
    
        # Build list of vertex coordinates
        vVals = []
        for (x, y) in xydata:
            vVals.append(int(x - minX))
            vVals.append(int(y - minY))
        
        self.vertex_data = ('v2i', vVals)
        self.vlen = len(data)
        self.build_colours(cF(data))
        
        self.build_vertex_list()
        
    
    def load_xyz_plot(self, data, xyzF, cF):
        self.point_data = data
        
        xyzdata = xyzF(data)
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
            
        self.vlen = len(data)
        self.vertex_data = ('v3i', vVals)
        self.build_colours(cF(data))
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
        #self.vertex_list.vertices = self.vertex_data
        self.vertex_list.indices = self.index_data
    
    
    def update_indices(self):
        # Ensure end is at least 2 and does not exceed number of datum points
        self.idx_end = max(2, min(self.vlen, self.idx_end))
        # Update index data
        self.index_data = range(self.idx_start, self.idx_end - 1)
    
        
    def vertex_count(self):
        (__a, __b) = self.vertex_data
        return len(__b)
    
        