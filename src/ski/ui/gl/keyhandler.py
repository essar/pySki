'''
  Module for handling key events within a PySki drawing window.
  Key functions are defined in an internal dictionary (key_map), matching
  keystroke symbol/modifier tuples to function names.
  Key handler functions should accept one argument, a GLPlotWindow.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (3 Dec 2012)
'''

import logging
log = logging.getLogger(__name__)

from math import sqrt

import pyglet.window.key as key

def __centre_on_last(win):
    (lastx, lasty) = win.plot.get_last_xy()
    cx = (float(win.plot.cfg.plot_width) / 2.0) - lastx
    cy = (float(win.plot.cfg.plot_height) / 2.0) - lasty
    
    sx = win.plot.cfg.scale_x / win.plot.live_zoom_x
    sy = win.plot.cfg.scale_y / win.plot.live_zoom_y
    sz = win.plot.cfg.scale_z / win.plot.live_zoom_z
    
    win.plot.pan_view_to(cx * sx, cy * sy, 0.0 * sz)
    
def __pan_down(win):
    win.plot.pan_view_down(win.plot.cfg.pan_step_y / win.plot.live_zoom_y)

def __pan_left(win):
    win.plot.pan_view_left(win.plot.cfg.pan_step_x / win.plot.live_zoom_x)
    
def __pan_right(win):
    win.plot.pan_view_right(win.plot.cfg.pan_step_x / win.plot.live_zoom_x)
    
def __pan_up(win):
    win.plot.pan_view_up(win.plot.cfg.pan_step_y / win.plot.live_zoom_y)

def __play_pause_animation(win):
    if win.plot.playing:
        win.plot.animation_pause()
    else:
        win.plot.animation_play()

def __reset(win):
    # Reset zoom factor
    win.plot.zoom_view_reset()
    # Reset view
    win.plot.pan_view_reset()

def __show_hide_status(win):
    if win.plot.cfg.show_status_bar:
        win.plot.cfg.show_status_bar = False
    else:
        win.plot.cfg.show_status_bar = True

def __step_backward(win):
    win.plot.step_backward(win.plot.cfg.animate_step)

def __step_forward(win):
    win.plot.step_forward(win.plot.cfg.animate_step)
    
def __step_track_backward(win):
    win.plot.step_track_backward(win.plot.cfg.animate_track_step)

def __step_track_forward(win):
    win.plot.step_track_forward(win.plot.cfg.animate_track_step)

def __zoom_in(win):
    win.plot.zoom_view_in(win.plot.cfg.zoom_step)
    
def __zoom_in_small(win):
    win.plot.zoom_view_in(sqrt(win.plot.cfg.zoom_step))

def __zoom_out(win):
    win.plot.zoom_view_out(win.plot.cfg.zoom_step)
    
def __zoom_out_small(win):
    win.plot.zoom_view_out(sqrt(win.plot.cfg.zoom_step))

# Define a dictionary pairing key stroke values with handler functions
key_map = {
           (key.A, 0): __zoom_in
         , (key.A, key.MOD_SHIFT): __zoom_in_small
         , (key.C, 0): __centre_on_last
         , (key.S, 0): __show_hide_status
         , (key.Z, 0): __zoom_out
         , (key.Z, key.MOD_SHIFT): __zoom_out_small
         , (key._0, 0): __reset
         , (key.SPACE, 0): __play_pause_animation
         , (key.LESS, key.MOD_SHIFT): __step_backward
         , (key.LESS, key.MOD_SHIFT + key.MOD_CTRL): __step_track_backward
         , (key.GREATER, key.MOD_SHIFT): __step_forward
         , (key.GREATER, key.MOD_SHIFT + key.MOD_CTRL): __step_track_forward
         , (key.UP, 0): __pan_up
         , (key.UP, key.MOD_SHIFT): NotImplemented
         , (key.DOWN, 0): __pan_down
         , (key.DOWN, key.MOD_SHIFT): NotImplemented
         , (key.LEFT, 0): __pan_left
         , (key.RIGHT, 0): __pan_right
}

def key_str((symbol, modifiers)):
    return (key.symbol_string(symbol), key.modifiers_string(modifiers))
    

def handle_key_press(symbol, modifiers, win):
    '''
      Main keystroke handing function.  Checks defined key handlers in a dict
      to find and execute defined functions.
      @param symbol: the pressed key symbol
      @param modifiers: the pressed key modifiers
      @param win: the current GL window
    '''
    k = (symbol, modifiers)
    log.debug('Key press %s trapped', key_str(k))
    if k in key_map:
        # Key handler function from dict
        f = key_map[k]
        log.debug('Key handler found: %s', f)
        
        if f is NotImplemented:
            log.warn('Handler is %s for %s', f, key_str(k))
        else:
            # Wrap in a try/except block to prevent bad handler functions
            # from crashing entire app
            try:
                key_map[k](win)
            except:
                # Log error details
                log.exception('Error executing key handler %s for %s', f.__name__, key_str(k))
                # Exit method
                return