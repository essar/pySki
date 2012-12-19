'''
Created on 3 Dec 2012

@author: sroberts
'''

import logging as log

class GLController:

    playing = True
        
    last_x = last_y = last_z = 0    
    
    # Live transformations
    live_scale_x = live_scale_y = live_scale_z = 1
    live_tx = live_ty = live_tz = 0

    def animation_pause(self):
        self.playing = False
        log.info('[GLController] Animation paused')
    
    def animation_play(self):
        self.playing = True
        log.info('[GLController] Animation playing')
    
    def pan_view(self, xShift, yShift, zShift):
        self.live_tx += xShift
        self.live_ty += yShift
        self.live_tz += zShift
        log.info('[GLController] Panning by (%d, %d, %d) to (%d, %d, %d)', xShift, yShift, zShift, self.live_tx, self.live_ty, self.live_tz)
    
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
        log.info('[GLController] Panning values reset')
        
    def pan_view_to(self, cX, cY, cZ):
        self.live_tx = cX
        self.live_ty = cY
        self.live_tz = cZ
        log.info('[GLController] Panning view to to (%d, %d, %d)', cX, cY, cZ)
    
    def zoom_view(self, zFac):
        if zFac == 0:
            # Reset zoom factors to 1
            self.live_scale_x = 1.0
            self.live_scale_y = 1.0
            self.live_scale_z = 1.0
            log.info('[GLController] Zoom factors reset')
        else:
            self.live_scale_x *= zFac
            self.live_scale_y *= zFac
            self.live_scale_z *= zFac
            log.info('[GLController] Zooming by %.1f to (%.1f, %.1f, %.1f)', zFac, self.live_scale_x, self.live_scale_y, self.live_scale_z)

    def zoom_view_in(self, zFac = 2.0):
        self.zoom_view(zFac)
        
    def zoom_view_out(self, zFac = 2.0):
        self.zoom_view(1.0 / zFac)
        
    def zoom_view_reset(self):
        self.zoom_view(0.0)
