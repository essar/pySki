'''
Created on 19 Dec 2012

@author: sroberts
'''

def _relativeise(data, value=None):
    mx = min(data)
    if value is None:
        return [x - mx for x in data]
    return value - mx

def _smooth(data, smoothing):
    smoothed = []
    for i in range(len(data)):
        vals = data[(i - smoothing) : (i + smoothing + 1)]
        smoothed.append((sum(vals) + data[i]) / (len(vals) + 1))
    
    return smoothed


class PlotData:
    '''
      Class containing data elements required for drawing a graphical plot.
    '''
    def __init__(self, xList, yList, zList, vList, xSmoothing=0, ySmoothing=0, zSmoothing=0):
        '''
        Constructor
        '''
        if type(xList) is not list:
            raise ValueError('List expected for xList')
        if type(yList) is not list:
            raise ValueError('List expected for yList')
        if type(zList) is not list:
            raise ValueError('List expexted for zList')
        if type(vList) is not list:
            raise ValueError('List expected for vList')
        if len(xList) <> len(yList) or len(yList) <> len(zList) or len(zList) <> len(vList):
            raise ValueError('Lists not same length')
        
        # Convert x,y,z data into relative smoothed lists
        self.x_data = _smooth(_relativeise(xList), xSmoothing)
        self.y_data = _smooth(_relativeise(yList), ySmoothing)
        self.z_data = _smooth(_relativeise(zList), zSmoothing)
        
        # Store value data as-is
        self.v_data = vList
    
    
    def compile_vertex_data(self, renderF, mode=3):
        # Clear lists
        vx_list = []
        cx_list = []
        
        minV = min(self.v_data)
        maxV = max(self.v_data)
        
        for i in range(len(self.x_data)):
            # Build vertex information
            vx_list.append(int(self.x_data[i]))
            vx_list.append(int(self.y_data[i]))
            if mode == 3: vx_list.append(self.z_data[i])
            
            # Build colour
            (r, g, b) = renderF(minV, maxV, self.v_data[i])
            cx_list.append(r)
            cx_list.append(g)
            cx_list.append(b)

        # Verify and update vertices
        assert(len(vx_list) / mode == len(self.x_data))    
        self.vertices_list = (len(self.x_data), vx_list)
        
        # Verify and update colours
        assert(len(cx_list) / 3 == len(self.v_data))
        self.colours_list = (len(self.v_data), cx_list)


    def setup_x_axis(self, label, markers=[]):
        # Set x-axis label value
        self.x_axis_label = label
        
        # Calculate relative position of markers
        self.x_axis_markers = [(lbl, _relativeise(self.x_data, pos)) for (lbl, pos) in markers]
    
    
    def setup_y_axis(self, label, markers=[]):
        # Set y-axis label value
        self.y_axis_label = label
        
        # Calculate relative position of markers
        self.y_axis_markers = [(lbl, _relativeise(self.y_data, pos)) for (lbl, pos) in markers]
    
    
    def setup_z_axis(self, label, markers=[]):
        # Set z-axis label value
        self.z_axis_label = label
        
        # Calculate relative position of markers
        self.z_axis_markers = [(lbl, _relativeise(self.z_data, pos)) for (lbl, pos) in markers]
    
        
    
    @staticmethod
    def build_linear_plot(xData, vData, xSmoothing = 0, ySmoothing = 0, xLabel = '', xMarkers = 0, yLabel = '', yMarkers = 0):
        # Compile synthetic list of z values
        zs = [0 for _x in range(len(xData))]
        
        plot = PlotData(xData, vData, zs, vData, xSmoothing, ySmoothing, 0)

        # Set up x-axis
        ## Calculate values
        xV = max(xData) - min(xData)
        xMarkVals = [(i / 100.0) * xV for i in range(0, 101, (100 / (xMarkers + 1)))]
        xMarks = [(m, m) for m in xMarkVals]
        ## Set plot properties
        plot.setup_x_axis(xLabel, xMarks)
        
        # Set up y-axis
        ## Calculate values
        yV = max(vData) - min(vData)
        yMarkVals = [(i / 100.0) * yV for i in range(0, 101, (100 / (yMarkers + 1)))]
        yMarks = [(m, m) for m in yMarkVals]
        ## Set plot properties
        plot.setup_y_axis(yLabel, yMarks)

        return plot
    
    
    @staticmethod
    def build_xy_plot(xyData, vData):
        # Compile list of x values
        xs = [x for (x, _y) in xyData]
        # Compile list of y values
        ys = [y for (_x, y) in xyData]
        # Compile synthetic list of z values
        zs = [0 for _x in range(len(xyData))]
        
        return PlotData(xs, ys, zs, vData)
        
        
    @staticmethod
    def build_xyz_plot(xyzData, vData):
        # Compile list of x values
        xs = [x for (x, _y, _z) in xyzData]
        # Compile list of y values
        ys = [y for (_x, y, _z) in xyzData]
        # Compile list of z values
        zs = [z for (_x, _y, z) in xyzData]
        
        return PlotData(xs, ys, zs, vData)