'''
  Module for handling key events within a PySki drawing window.
  Key functions are defined in an internal dictionary (key_map), matching
  keystroke symbol/modifier tuples to function names.
  Key handler functions should accept two arguments, a SkiGLConfig and
  SkiGLController.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (3 Dec 2012)
'''

import logging as log
from math import sqrt

import pyglet.window.key as key

def __centre_on_last(plot):
    cx = (float(plot.cfg.plot_width) / 2.0) - plot.plot_data[plot.plot_idx].x_data[plot.draw_idx]
    cy = (float(plot.cfg.plot_height) / 2.0) - plot.plot_data[plot.plot_idx].y_data[plot.draw_idx]
    
    sx = plot.cfg.scale_x / plot.live_zoom_x
    sy = plot.cfg.scale_y / plot.live_zoom_y
    sz = plot.cfg.scale_z / plot.live_zoom_z
    
    plot.pan_view_to(cx * sx, cy * sy, 0.0 * sz)
    
def __pan_down(plot):
    plot.pan_view_down(plot.cfg.pan_step_y / plot.live_zoom_y)

def __pan_left(plot):
    plot.pan_view_left(plot.cfg.pan_step_x / plot.live_zoom_x)
    
def __pan_right(plot):
    plot.pan_view_right(plot.cfg.pan_step_x / plot.live_zoom_x)
    
def __pan_up(plot):
    plot.pan_view_up(plot.cfg.pan_step_y / plot.live_zoom_y)

def __play_pause_animation(plot):
    if plot.playing:
        plot.animation_pause()
    else:
        plot.animation_play()

def __reset(plot):
    # Reset zoom factor
    plot.zoom_view_reset()
    # Reset view
    plot.pan_view_reset()

def __show_hide_status(plot):
    if plot.cfg.show_status_bar:
        plot.cfg.show_status_bar = False
    else:
        plot.cfg.show_status_bar = True

def __zoom_in(plot):
    plot.zoom_view_in(plot.cfg.zoom_step)
    
def __zoom_in_small(plot):
    plot.zoom_view_in(sqrt(plot.cfg.zoom_step))

def __zoom_out(plot):
    plot.zoom_view_out(plot.cfg.zoom_step)
    
def __zoom_out_small(plot):
    plot.zoom_view_out(sqrt(plot.cfg.zoom_step))

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
         , (key.UP, 0): __pan_up
         , (key.UP, key.MOD_SHIFT): NotImplemented
         , (key.DOWN, 0): __pan_down
         , (key.DOWN, key.MOD_SHIFT): NotImplemented
         , (key.LEFT, 0): __pan_left
         , (key.RIGHT, 0): __pan_right
}

def key_str((symbol, modifiers)):
    return (key.symbol_string(symbol), key.modifiers_string(modifiers))
    

def handle_key_press(symbol, modifiers, plot):
    '''
      Main keystroke handing function.  Checks defined key handlers in a dict
      to find and execute defined functions.
      @param symbol: the pressed key symbol
      @param modifiers: the pressed key modifiers
      @param cfg: the current GL configuration
      @param ctl: the current GL controller
    '''
    k = (symbol, modifiers)
    log.debug('[KeyHandler] Key press %s trapped', key_str(k))
    if k in key_map:
        # Key handler function from dict
        f = key_map[k]
        log.debug('[KeyHandler] Key handler found: %s', f)
        
        if f is NotImplemented:
            log.warn('[KeyHandler] Handler is %s for %s', f, key_str(k))
        else:
            # Wrap in a try/except block to prevent bad handler functions
            # from crashing entire app
            try:
                key_map[k](plot)
            except:
                # Log error details
                log.exception('[KeyHandler] Error executing key handler %s for %s', f.__name__, key_str(k))
                # Exit method
                return