'''
Created on 19 Dec 2012

@author: sroberts
'''

class PlotCfg:
    '''
      Class containing configuration items relating to how a plot is drawn
    '''

    animate = False
    animate_fps = 25.0
    animate_step = 10
    animate_track_step = 1
    
    bg_colour_4f = (0.1, 0.1, 0.15, 0.1)

    pan_step_x = 50
    pan_step_y = 50
    
    plot_width = 0
    plot_height = 0
    
    scale_constrain = False
    scale_stretch = True
    scale_x = 1.0
    scale_y = 1.0
    scale_z = 1.0
    
    show_axis = False
    show_axis_labels = False
    show_axis_markers = False
    show_status_bar = False
    
    status_height = 20
    status_txt = ''
    status_values_f = NotImplemented
    
    window_fullscreen = False
    window_height = 600
    window_margin_x = 2
    window_margin_y = 2
    window_width = 800
    
    zoom_step = 2
    
    
    def _update_scaling(self):
        if self.scale_stretch:
            # Update scale factors to make plot fill window
            viewWidth = float(self.window_width
                              - (20 if self.show_axis else 0)
                              - (2 * self.window_margin_x)
            )
            viewHeight = float(self.window_height
                              - (20 if self.show_axis else 0)
                              - (self.status_height if self.show_status_bar else 0)
                              - (2 * self.window_margin_y)
            )
            self.scale_x = float(viewWidth / float(max(1, self.plot_width)))
            self.scale_y = float(viewHeight / float(max(1, self.plot_height)))
        
        if self.scale_constrain:
            # Update scale factors so they scale x:X
            self.scale_x = self.scale_y = min(self.scale_x, self.scale_y)
            
        return (self.scale_x, self.scale_y, self.scale_z)